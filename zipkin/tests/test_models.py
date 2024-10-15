import unittest

from ..models import TraceStack, Annotation, Trace


class TestTrace(unittest.TestCase):
    def setUp(self):
        self.trace = Trace("test")

    def test_child(self):
        self.trace.child("child")

        self.assertEqual(len(self.trace.children()), 2)
        self.assertEqual(self.trace.children()[0].name, "child")

    def test_child_noref(self):
        self.trace.child_noref("test")
        self.assertEqual(len(self.trace.children()), 1)

    def test_record(self):
        self.trace.record(Annotation.string("key", "value"))
        self.assertEqual(self.trace.children()[0].annotations[0].name, "key")

    def test_type(self):
        # Unicode or string should not raise
        self.trace.child(b"dummy_bytes")
        self.trace.child("dummy_string")

        # rest should raise
        self.assertRaises(AssertionError, self.trace.child, 1)
        self.assertRaises(AssertionError, self.trace.child, None)


class TestTraceStack(unittest.TestCase):
    def setUp(self):
        self.stack = TraceStack()

    def test_push_pop(self):
        self.stack.append(Trace("testing stack"))
        self.stack.child("subtrace")

        self.assertEqual(self.stack.current.name, "subtrace")
        trace = self.stack.pop()
        self.assertEqual(trace.name, "subtrace")

        self.assertEqual(self.stack.current.name, "testing stack")

    def test_pop_empty(self):
        self.assertRaises(IndexError, self.stack.pop)

    def test_reset(self):
        self.stack.append(Trace("testing stack"))
        self.stack.reset()
        self.assertEqual(len(self.stack.stack), 0)
        self.assertEqual(self.stack.current, None)

    def test_replace(self):
        self.stack.append(Trace("testing stack"))
        self.stack.replace(Trace("testing stack"))

        # We replaced stack, we should have only one item
        self.assertEqual(len(self.stack.stack), 1)

    def test_types(self):
        self.assertRaises(AssertionError, self.stack.replace, "string")
        self.assertRaises(AssertionError, self.stack.append, "string")
        self.stack.append(Trace("testing stack"))
        self.assertRaises(AssertionError, self.stack.child, 1)
        self.assertRaises(AssertionError, self.stack.child, None)
        self.assertRaises(AssertionError, self.stack.child, "string", "test")
        self.assertRaises(AssertionError, self.stack.child, "string", False)

        # String or unicode should not raise
        self.stack.child(b"dummy_bytes")
        self.stack.child("dummy_string")
