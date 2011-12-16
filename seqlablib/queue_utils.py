import os
import sets
import threading
#import pyinotify
import Queue
import refs

def queue_events(queue, path, mask, fun=lambda x:x.path):
    class Handler(pyinotify.ProcessEvent):
        def process_IN_UNMOUNT(self, event):
            syslog.syslog(syslog.LOG_NOTICE, ("Backing filesystem of %s was unmounted."
                                              "Exiting.") % event.path)
            exit(1)
        def process_default(self, event):
            queue.put(fun(event))

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, Handler())
    wm.add_watch(path, mask, rec=True)
    notifier.loop()


def batched_unique(queue, fun, timeout_ref, exit_event):
    state_ref = refs.Ref()
    state_ref.put(sets.ImmutableSet())
    def run_batch():
        batch = state_ref.put(sets.ImmutableSet())
        threading.Thread(target=fun,args=(batch,)).run()
    timer = None
    while True:
        try:
            v = queue.get(False, None)
            state_ref.put(state_ref.get().union([v]))
            if timer:
                timer.cancel()
            timer = threading.Timer(timeout_ref.get(), run_batch)
            timer.start()
        except Queue.Empty, e:
            if exit_event.is_set():
                return
                
def intermittently(fun, delay_ref, exit_event):
    run_again = threading.Event()
    run_again.set()
    timer = None
    while not(exit_event.is_set()):
        if run_again.is_set():
            run_again.clear()
            threading.Thread(target=fun).start()
            timer = threading.Timer(delay_ref.get(), lambda: run_again.set())
            timer.start()
    timer.cancel()

def enqueue_files(queue, path_ref):
    path = path_ref.get()
    filenames = os.listdir(path)
    for f in filenames:
        queue.put(os.path.join(path, f))
        

    

