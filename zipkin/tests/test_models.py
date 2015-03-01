import unittest

from ..models import TraceStack, Annotation, Endpoint, Trace


class TestTrace(unittest.TestCase):
    def setUp(self):
        self.trace = Trace('test')

    def test_child(self):
        self.trace.child('child')

        self.assertEquals(len(self.trace.children()), 2)
        self.assertEquals(self.trace.children()[0].name, 'child')

    def test_child_noref(self):
        self.trace.child_noref('test')
        self.assertEquals(len(self.trace.children()), 1)

    def test_record(self):
        self.trace.record(Annotation.string('key', 'value'))
        self.assertEquals(self.trace.children()[0].annotations[0].name, 'key')

    def test_type(self):
        # Unicode or string should not raise
        self.trace.child('string')
        self.trace.child(u'unicode')

        # rest should raise
        self.assertRaises(AssertionError, self.trace.child, 1)
        self.assertRaises(AssertionError, self.trace.child, None)


class TestTraceStack(unittest.TestCase):
    def setUp(self):
        self.stack = TraceStack()

    def test_push_pop(self):
        self.stack.append(Trace('testing stack'))
        self.stack.child('subtrace')

        self.assertEquals(self.stack.current.name, 'subtrace')
        trace = self.stack.pop()
        self.assertEquals(trace.name, 'subtrace')

        self.assertEquals(self.stack.current.name, 'testing stack')

    def test_pop_empty(self):
        self.assertRaises(IndexError, self.stack.pop)

    def test_reset(self):
        self.stack.append(Trace('testing stack'))
        self.stack.reset()
        self.assertEquals(len(self.stack.stack), 0)
        self.assertEquals(self.stack.current, None)

    def test_replace(self):
        self.stack.append(Trace('testing stack'))
        self.stack.replace(Trace('testing stack'))

        # We replaced stack, we should have only one item
        self.assertEquals(len(self.stack.stack), 1)

    def test_types(self):
        self.assertRaises(AssertionError, self.stack.replace, "string")
        self.assertRaises(AssertionError, self.stack.append, "string")
        self.stack.append(Trace('testing stack'))
        self.assertRaises(AssertionError, self.stack.child, 1)
        self.assertRaises(AssertionError, self.stack.child, None)
        self.assertRaises(AssertionError, self.stack.child, "string", "test")
        self.assertRaises(AssertionError, self.stack.child, "string", False)

        # String or unicode should not raise
        self.stack.child("string")
        self.stack.child(u"unicode")
