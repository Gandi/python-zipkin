
import threading

class TraceStack():
    def __init__(self):
        self.stack = []
        self.cur = None

    def child(self, name, endpoint = None):
        print "child", self.stack
        trace = self.cur.child(name, endpoint)
        self.stack.append(trace)
        self.cur = trace
        return trace

    def append(self, trace):
        self.stack.append(trace)
        self.cur = trace
        print "append", self.stack

    def pop(self):
        trace = self.stack.pop()
        try:
            cur = self.stack.pop()
            self.stack.append(cur)
            self.cur = cur
        except:
            self.cur = None
        return trace

    @property
    def current(self):
        return self.cur


data = threading.local()

def local():
    global data
    if not getattr(data, 'trace', None):
        data.trace = TraceStack()
    print data.trace
    return data.trace
