from unittest import TestCase
from ExceptionCatcher import *


def div(k):
    return 1 / k


class TestGlobalExceptionCatcher(TestCase):
    def test_basic(self):
        @ExceptionCatcher
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertIsNone(f(0))
        self.assertEqual(f(-1), -1)

    def test_with(self):
        with ExceptionCatcher:
            div(1)
            div(0)

    def test_with_post_check(self):
        with ExceptionCatcher as catcher:
            div(1)
            div(0)
        self.assertRaises(AssertionError, lambda: catcher.failed)

    def test_with_post_result(self):
        with ExceptionCatcher as catcher:
            div(1)
            div(0)
        self.assertRaises(AssertionError, lambda: catcher.result)

    def test_keyboard_interrupt(self):
        try:
            with ExceptionCatcher:
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            pass
        else:
            self.fail('Nothing Raised')

    def test_exit_0(self):
        output = []

        try:
            with ExceptionCatcher(output=output.append):
                exit(0)
        except SystemExit:
            self.assertTrue(len(output) == 0)
        else:
            self.fail('Nothing Raised')

    def test_exit_1(self):
        output = []

        try:
            with ExceptionCatcher(output=output.append):
                exit(1)
        except SystemExit:
            self.assertTrue(len(output) != 0)
        else:
            self.fail('Nothing Raised')


class TestInstanceExceptionCatcher(TestCase):
    def test_wrong_args(self):
        self.assertRaises(TypeError, ExceptionCatcher,
                          to_wrap=lambda: None, callback=lambda: None)

    def test_instance(self):
        @ExceptionCatcher()
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertIsNone(f(0))
        self.assertEqual(f(-1), -1)

    def test_callback(self):
        @ExceptionCatcher(callback=lambda: 69)
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertEqual(f(0), 69)
        self.assertEqual(f(-1), -1)

    def test_with(self):
        with ExceptionCatcher():
            div(1)
            div(0)

    def test_with_callback(self):
        calls = []

        with ExceptionCatcher(callback=lambda: calls.append(None)):
            div(1)
            div(0)

        self.assertEqual(calls, [None])

    def test_with_post_check(self):
        with ExceptionCatcher() as catcher:
            div(1)
            div(0)
        self.assertTrue(catcher.failed)

    def test_with_post_result(self):
        with ExceptionCatcher() as catcher:
            div(1)
            div(0)
        self.assertIsNone(catcher.result)

    def test_with_callback_post_check(self):
        calls = []

        with ExceptionCatcher(callback=lambda: calls.append(None)) as catcher:
            div(1)
            div(0)

        self.assertEqual(calls, [None])
        self.assertTrue(catcher.failed)

    def test_with_callback_post_result(self):
        calls = []

        def callback():
            calls.append(None)
            return 69

        with ExceptionCatcher(callback=callback) as catcher:
            div(1)
            div(0)

        self.assertEqual(calls, [None])
        self.assertEqual(catcher.result, 69)

    def test_exception_callback(self):
        @ExceptionCatcher(callback=exception_callback)
        def f(k):
            return 1 / k

        self.assertEqual(f(1), 1)
        self.assertEqual(f(0), "ZeroDivisionError: division by zero")
        self.assertEqual(f(-1), -1)

    def test_silent(self):
        output = []

        @ExceptionCatcher(silent=True, output=output.append)
        def f(k):
            return 1 / k

        f(1), f(0), f(-1)

        self.assertTrue(len(output) == 0)

    def test_not_silent(self):
        output = []

        @ExceptionCatcher(silent=False, output=output.append)
        def f(k):
            return 1 / k

        f(1), f(0), f(-1)

        self.assertTrue(len(output) != 0)

    def test_output(self):
        output = []

        @ExceptionCatcher(output=output.append)
        def f(k):
            return 1 / k

        f(1), f(0), f(-1)

        output = '\n'.join(output)
        print(output)

        for snippet in ('f(1), f(0), f(-1)',
                        '=Exception caught here=',
                        'return 1 / k',
                        'ZeroDivisionError: division by zero'):
            self.assertIn(snippet, output)
