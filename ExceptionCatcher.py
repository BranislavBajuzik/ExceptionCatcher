import sys
import traceback

from functools import wraps
from itertools import chain
from typing import Any, Callable

__all__ = ['ExceptionCatcher', 'exception_callback']


class __ExceptionCatcher:
    __output = print

    def __init__(self,
                 callback: Callable[[], Any] = None,
                 silent: bool = False,
                 output: Callable[[str], Any] = None):
        """General wrapper for catching exceptions

        :param callback: This will be called if an exception is caught.
                         The return value of this will be the result / returned
        :param silent: Nothing will be outputted to :param output: if True
        :param output: The output will be sent here.
                       Defaults to `print` if omitted
        """
        self.__callback = callback
        self.__silent = silent
        self.__result = None
        self.__failed = False

        if output is not None:
            self.__output = output

    def set_output(self, output: Callable[[str], Any]):
        """Set default output handler"""
        self.__class__.__output = output

    @property
    def __is_global(self):
        """Check if :param self: is created as an instance or not"""
        return id(self) == id(ExceptionCatcher)

    @property
    def failed(self):
        """Used to query if an exception was caught in with block"""
        assert not self.__is_global, 'Unable to get state of global ' \
                                     'ExceptionCatcher, use an instance instead'
        return self.__failed

    @property
    def result(self):
        """Used to get result after an exception was caught in with block"""
        assert not self.__is_global, 'Unable to get result of global ' \
                                     'ExceptionCatcher, use an instance instead'
        return self.__result

    def __call__(self,
                 to_wrap=None,
                 *,
                 callback: Callable[[], Any] = None,
                 silent: bool = False,
                 output: Callable[[str], Any] = None):
        if to_wrap is not None and callback is not None:
            raise TypeError('Both \'to_wrap\' and \'callback\' were provided')

        if to_wrap is None:
            return self.__class__(callback, silent, output)

        @wraps(to_wrap)
        def ExceptionCatcher(*args, **kwargs):
            ok = False
            ret = None

            with self:
                ret = to_wrap(*args, **kwargs)
                ok = True

            if not ok:
                return self.__result
            return ret

        return ExceptionCatcher

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ret = False

        if exc_type is not None and \
                (exc_type is not SystemExit or exc_val.code != 0):
            ret = exc_type not in (SystemExit, KeyboardInterrupt)

            if not self.__silent:
                before = traceback.format_list(traceback.extract_stack())[:-2]
                after = traceback.format_list(traceback.extract_tb(exc_tb))

                after[0] = ' =Exception caught here=\n'  # Replace current line
                after[-1] = after[-1][:-1]  # Remove trailing newline

                self.__output('Traceback (most recent call last):')
                self.__output(''.join(chain(before, after)))
                self.__output(f'{exc_type.__name__}: {exc_val}')

        if ret and self.__callback is not None:
            if not self.__silent:
                callback = str(self.__callback)
                if hasattr(self.__callback, '__name__'):
                    callback = self.__callback.__name__
                self.__output(f'\nCallback \'{callback}\' provided, executing.')
            with ExceptionCatcher(silent=self.__silent):
                self.__result = self.__callback()

        self.__failed = ret
        return ret


def exception_callback():
    """Returns the last thrown exception formatted as: ex_name: ex_text"""
    return '{0.__name__}: {1}'.format(*sys.exc_info())


# Global ExceptionCatcher for syntax convenience
ExceptionCatcher = __ExceptionCatcher()
