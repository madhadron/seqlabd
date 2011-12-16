import threading
import time
import Queue

import seqlablib.refs
import seqlablib.queue_utils

def test_queue_events():
    # ensure that target dir exists, make a queue, start up the queue_events, touch a couple files in target dir, check that they are queued properly
    pass

def test_batched_unique():
    q = Queue.Queue()
    timeout_ref = seqlablib.refs.Ref()
    timeout_ref.put(0.2)
    e = threading.Event()
    d = []
    def f(xs):
        print "Running batch: %s" % str(xs)
        d.extend(xs)
        e.set()
    t = threading.Thread(target=seqlablib.queue_utils.batched_unique, args=(q, f, timeout_ref, 1))
    t.start()
    q.put(1); q.put(2); q.put(3)
    e.wait()
    assert d==[1,2,3]
    t.daemon = True

test_batched_unique()
