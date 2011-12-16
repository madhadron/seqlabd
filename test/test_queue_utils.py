import common
import os
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
    batchedevt = threading.Event()
    exitevt = threading.Event()
    d = []
    def f(xs):
        d.extend(xs)
        batchedevt.set()
    t = threading.Thread(target=seqlablib.queue_utils.batched_unique, args=(q, f, timeout_ref, exitevt))
    t.start()
    q.put(1); q.put(2); q.put(3)
    batchedevt.wait()
    assert d==[1,2,3]
    exitevt.set()

def test_intermittently():
    delay_ref = seqlablib.refs.Ref()
    delay_ref.put(0.05)
    d = []
    evt = threading.Event()
    exit_evt = threading.Event()
    def f():
        d.append(None)
        evt.set()
    threading.Thread(target=seqlablib.queue_utils.intermittently, args=(f, delay_ref, exit_evt)).start()
    evt.wait()
    assert d==[None]
    evt.clear()
    evt.wait()
    assert d==[None,None]
    evt.clear()
    evt.wait()
    assert d==[None,None,None]
    evt.clear()
    exit_evt.set()

def test_enqueue_files():
    q = Queue.Queue()
    path_ref = seqlablib.refs.Ref()
    path_ref.put('data/to_enqueue')
    seqlablib.queue_utils.enqueue_files(q, path_ref)
    d = []
    while not(q.empty()):
        x = q.get()
        n = os.path.split(x)[1]
        d.append(n)
    assert d == ['alpha','beta','gamma']
