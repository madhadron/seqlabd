import sets
import threading
#import pyinotify

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


def batched_unique(queue, fun, timeout_ref, n_batches=None):
    state_ref = refs.Ref()
    state_ref.put(sets.ImmutableSet())
    def run_batch():
        batch = state_ref.put(sets.ImmutableSet())
        threading.Thread(fun,(batch,)).run()
        if n_batches:
            n_batches -= 1
    timer = None
    while n_batches > 0:
        v = queue.get(True, None)
        state_ref.put(state_ref.get().union([v]))
        if timer:
            timer.cancel()
        timer = threading.Timer(timeout_ref.get(), run_batch)

    

