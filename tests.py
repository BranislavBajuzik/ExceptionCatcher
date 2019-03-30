import sys

import ExceptionCatcher as E

from io import StringIO
from importlib import reload
from unittest import TestCase
from unittest.mock import patch
from functools import partial


def div(k):
    return 1 / k


class TestGlobalExceptionCatcher(TestCase):
    def setUp(self):
        reload(E)

    def test_basic(self):
        @E.ExceptionCatcher
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertIsNone(f(0))
        self.assertEqual(f(-1), -1)

    def test_with(self):
        with E.ExceptionCatcher:
            div(1)
            div(0)

    def test_with_post_check(self):
        with E.ExceptionCatcher as catcher:
            div(1)
            div(0)
        self.assertRaises(AssertionError, lambda: catcher.failed)

    def test_with_post_result(self):
        with E.ExceptionCatcher as catcher:
            div(1)
            div(0)
        self.assertRaises(AssertionError, lambda: catcher.result)

    def test_keyboard_interrupt(self):
        try:
            with E.ExceptionCatcher:
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            pass
        else:
            self.fail('Nothing Raised')

    def test_exit_0(self):
        output = []

        try:
            with E.ExceptionCatcher(output=output.append):
                exit(0)
        except SystemExit:
            self.assertTrue(len(output) == 0)
        else:
            self.fail('Nothing Raised')

    def test_exit_1(self):
        output = []

        try:
            with E.ExceptionCatcher(output=output.append):
                exit(1)
        except SystemExit:
            self.assertTrue(len(output) != 0)
        else:
            self.fail('Nothing Raised')

    def test_output(self):
        @E.ExceptionCatcher
        def f(k):
            return 1 / k

        with patch('sys.stdout', new=StringIO()) as captured_stdout:
            f(1), f(0), f(-1)

        output = captured_stdout.getvalue()

        for snippet in ('f(1), f(0), f(-1)',
                        '=Exception caught here=',
                        'return 1 / k',
                        'ZeroDivisionError: division by zero'):
            self.assertIn(snippet, output)

    def test_output_default_setter(self):
        @E.ExceptionCatcher
        def f(k):
            return 1 / k

        @E.ExceptionCatcher
        def g(k):
            return 1 / k

        with patch('sys.stderr', new=StringIO()) as captured_stderr, \
                patch('sys.stdout', new=StringIO()) as captured_stdout:
            E.ExceptionCatcher.set_output(partial(print, file=sys.stderr))
            f(1), f(0), f(-1)
            E.ExceptionCatcher.set_output(print)
            g(1), g(0), g(-1)

        captured_stderr = captured_stderr.getvalue()
        captured_stdout = captured_stdout.getvalue()

        for snippet in ('=Exception caught here=',
                        'return 1 / k',
                        'ZeroDivisionError: division by zero'):
            self.assertIn(snippet, captured_stderr)
            self.assertIn(snippet, captured_stdout)

        self.assertIn('f(1), f(0), f(-1)', captured_stderr)
        self.assertIn('g(1), g(0), g(-1)', captured_stdout)
        self.assertNotIn('g(1), g(0), g(-1)', captured_stderr)
        self.assertNotIn('f(1), f(0), f(-1)', captured_stdout)

    def test_output_stderr(self):
        @E.ExceptionCatcher
        def f(k):
            return 1 / k

        with patch('sys.stderr', new=StringIO()) as captured_stderr:
            E.ExceptionCatcher.set_output(partial(print, file=sys.stderr))

            f(1), f(0), f(-1)

        output = captured_stderr.getvalue()

        for snippet in ('f(1), f(0), f(-1)',
                        '=Exception caught here=',
                        'return 1 / k',
                        'ZeroDivisionError: division by zero'):
            self.assertIn(snippet, output)


class TestInstanceExceptionCatcher(TestCase):
    def setUp(self):
        reload(E)

    def test_instance(self):
        @E.ExceptionCatcher()
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertIsNone(f(0))
        self.assertEqual(f(-1), -1)

    def test_lambda(self):
        f = E.ExceptionCatcher(lambda k: 1/k, callback=lambda: 69)

        self.assertEqual(f(1), 1)
        self.assertEqual(f(0), 69)
        self.assertEqual(f(-1), -1)

    def test_callback(self):
        @E.ExceptionCatcher(callback=lambda: 69)
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertEqual(f(0), 69)
        self.assertEqual(f(-1), -1)

    def test_callback_no_name(self):
        def callback(k):
            return k

        @E.ExceptionCatcher(callback=partial(callback, 69))
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertEqual(f(0), 69)
        self.assertEqual(f(-1), -1)

    def test_with(self):
        with E.ExceptionCatcher():
            div(1)
            div(0)

    def test_with_callback(self):
        calls = []

        with E.ExceptionCatcher(callback=lambda: calls.append(None)):
            div(1)
            div(0)

        self.assertEqual(calls, [None])

    def test_with_post_check(self):
        with E.ExceptionCatcher() as catcher:
            div(1)
            div(0)
        self.assertTrue(catcher.failed)

    def test_with_post_result(self):
        with E.ExceptionCatcher() as catcher:
            div(1)
            div(0)
        self.assertIsNone(catcher.result)

    def test_with_callback_post_check(self):
        calls = []

        with E.ExceptionCatcher(callback=lambda: calls.append(None)) as catcher:
            div(1)
            div(0)

        self.assertEqual(calls, [None])
        self.assertTrue(catcher.failed)

    def test_with_callback_post_result(self):
        calls = []

        def callback():
            calls.append(None)
            return 69

        with E.ExceptionCatcher(callback=callback) as catcher:
            div(1)
            div(0)

        self.assertEqual(calls, [None])
        self.assertEqual(catcher.result, 69)

    def test_exception_callback(self):
        @E.ExceptionCatcher(callback=E.exception_callback)
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertEqual(f(0), "ZeroDivisionError: division by zero")
        self.assertEqual(f(-1), -1)

    def test_silent(self):
        output = []

        @E.ExceptionCatcher(silent=True, output=output.append)
        def f(k):
            return 1 / k

        f(1), f(0), f(-1)

        self.assertTrue(len(output) == 0)

    def test_not_silent(self):
        output = []

        @E.ExceptionCatcher(silent=False, output=output.append)
        def f(k):
            return 1 / k

        f(1), f(0), f(-1)

        self.assertTrue(len(output) != 0)

    def test_output(self):
        with patch('sys.stdout', new=StringIO()) as captured_stdout:
            @E.ExceptionCatcher
            def f(k):
                return 1 / k
            f(1), f(0), f(-1)

        output = captured_stdout.getvalue()

        for snippet in ('f(1), f(0), f(-1)',
                        '=Exception caught here=',
                        'return 1 / k',
                        'ZeroDivisionError: division by zero'):
            self.assertIn(snippet, output)

    def test_output_default(self):
        with patch('sys.stderr', new=StringIO()) as captured_stderr, \
                patch('sys.stdout', new=StringIO()) as captured_stdout:
            @E.ExceptionCatcher(output=partial(print, file=sys.stderr))
            def f(k):
                return 1 / k
            f(1), f(0), f(-1)

            @E.ExceptionCatcher
            def g(k):
                return 1 / k
            g(1), g(0), g(-1)

        captured_stderr = captured_stderr.getvalue()
        captured_stdout = captured_stdout.getvalue()

        for snippet in ('=Exception caught here=',
                        'return 1 / k',
                        'ZeroDivisionError: division by zero'):
            self.assertIn(snippet, captured_stderr)
            self.assertIn(snippet, captured_stdout)

        self.assertIn('f(1), f(0), f(-1)', captured_stderr)
        self.assertIn('g(1), g(0), g(-1)', captured_stdout)
        self.assertNotIn('g(1), g(0), g(-1)', captured_stderr)
        self.assertNotIn('f(1), f(0), f(-1)', captured_stdout)
