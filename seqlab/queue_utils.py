import re
import os
import sets
import threading
import pyinotify
import Queue
import refs

def queue_events(queue, path, mask, exit_event, fun=lambda x:x.pathname, include_regex=[]):
    class Handler(pyinotify.ProcessEvent):
        def process_IN_UNMOUNT(self, event):
            syslog.syslog(syslog.LOG_NOTICE, ("Backing filesystem of %s was unmounted."
                                              "Exiting.") % event.pathname)
            exit(1)
        def process_default(self, event):
            if re.search(include_regex, event.pathname):
                queue.put(fun(event))
    wm = pyinotify.WatchManager()
    notifier = pyinotify.ThreadedNotifier(wm, Handler())
    wm.add_watch(path, mask, rec=True)
    notifier.start()
    def monitor_exit():
        exit_event.wait()
        notifier.stop()
    threading.Thread(target=monitor_exit).start()


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

def enqueue_files(queue, path_ref, include_regex=r'.'):
    def g():
        path = path_ref.get()
        filenames = os.listdir(path)
        def f(filename):
            if re.search(include_regex, filename):
                queue.put(os.path.join(path, filename))
        for filename in filenames:
            f(filename)
    return g
        
def map_queue(queue, fun, exit_event):
    while not(exit_event.is_set()):
        try:
            v = queue.get_nowait()
            fun(v)
        except Queue.Empty:
            pass

    

