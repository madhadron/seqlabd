import common
import os
import threading
import time
import Queue
import pyinotify

import seqlablib.refs
import seqlablib.queue_utils

def test_queue_events():
    q = Queue.Queue()
    exit_event = threading.Event()
    seqlablib.queue_utils.queue_events(q, 'data', pyinotify.IN_CREATE, exit_event, exclude_list=['.*beta$'])
    for i in ['data/alpha','data/beta','data/gamma']:
        with open(i, 'w') as h:
            print >>h, 'Hello'
        os.unlink(i)
    exit_event.set()
    assert os.path.split(q.get())[1] == 'alpha'
    assert os.path.split(q.get())[1] == 'gamma'


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
    exitevt.set()
    assert d==[1,2,3]


def test_intermittently():
    delay_ref = seqlablib.refs.Ref()
    delay_ref.put(0.5)
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
    seqlablib.queue_utils.enqueue_files(q, path_ref, exclude_list=[r'.*?beta$'])
    d = []
    while not(q.empty()):
        x = q.get()
        n = os.path.split(x)[1]
        d.append(n)
    assert d == ['alpha','gamma']

test_enqueue_files()
