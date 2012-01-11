import common
import os
import threading
import time
import Queue
import pyinotify

import seqlab.refs
import seqlab.queue_utils

def test_queue_events():
    q = Queue.Queue()
    exit_event = threading.Event()
    seqlab.queue_utils.queue_events(q, 'data', pyinotify.IN_CREATE, exit_event, 
                                       include_regex=r'.*(alpha|gamma)$')
    for i in ['data/alpha','data/beta','data/gamma']:
        with open(i, 'w') as h:
            print >>h, 'Hello'
        os.unlink(i)
    exit_event.set()
    assert os.path.split(q.get())[1] == 'alpha'
    assert os.path.split(q.get())[1] == 'gamma'


def test_batched_unique():
    q = Queue.Queue()
    timeout_ref = seqlab.refs.Ref()
    timeout_ref.put(0.2)
    batchedevt = threading.Event()
    exitevt = threading.Event()
    d = []
    def f(xs):
        d.extend(xs)
        batchedevt.set()
    t = threading.Thread(target=seqlab.queue_utils.batched_unique, args=(q, f, timeout_ref, exitevt))
    t.start()
    q.put(1); q.put(2); q.put(3)
    batchedevt.wait()
    exitevt.set()
    assert d==[1,2,3]


def test_intermittently():
    delay_ref = seqlab.refs.Ref()
    delay_ref.put(0.1)
    d = []
    evt = threading.Event()
    exit_evt = threading.Event()
    def f():
        d.append(None)
        evt.set()
    threading.Thread(target=seqlab.queue_utils.intermittently, args=(f, delay_ref, exit_evt)).start()
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
    path_ref = seqlab.refs.Ref()
    path_ref.put('data/to_enqueue')
    seqlab.queue_utils.enqueue_files(q, path_ref, include_regex=r'(alpha|gamma)')()
    d = []
    while not(q.empty()):
        x = q.get()
        n = os.path.split(x)[1]
        d.append(n)
    assert d == ['alpha','gamma']

def test_map_queue():
    q = Queue.Queue()
    exit_event = threading.Event()
    done_event = threading.Event()
    d = []
    def f(x):
        d.append(x)
        if x==3:
            done_event.set()
    threading.Thread(target=seqlab.queue_utils.map_queue, args=(q, f, exit_event)).start()
    q.put(1)
    q.put(2)
    q.put(3)
    done_event.wait()
    exit_event.set()
    assert d == [1,2,3]

