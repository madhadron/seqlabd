import collections
import locks

class Ref(object):
    def __init__(self, val=None):
        self.initialized = (val != None)
        self.lock = locks.ReadWriteLock()
        self.value = val
    def put(self, val):
        try:
            old_val = self.value
            self.lock.acquireWrite()
            self.value = val
            self.initialized = True
            return old_val
        finally:
            self.lock.release()
    def get(self):
        if not(self.initialized):
            raise ValueError("Tried to get value from uninitialized Ref")
        try:
            self.lock.acquireRead()
            return self.value
        finally:
            self.lock.release()
    def __getitem__(self, key):
        return FieldRef(self, key)

class FieldRef(object):
    def __init__(self, ref, field):
        self.ref = ref
        self.field = field
    def put(self, val):
        try:
            self.ref.lock.acquireWrite()
            d = self.ref.value
            old_val = d[self.field]
            d[self.field] = val
            return old_val
        finally:
            self.ref.lock.release()
    def get(self):
        return self.ref.get()[self.field]

