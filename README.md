# ExceptionCatcher

General wrapper for catching exceptions

Any exception (Except for `KeyboardInterrupt` and `SystemExit`) raised inside ExceptionCatcher context will be caught and suppressed and the whole traceback will be printed out.

## Usage

As decorator
```python
@ExceptionCatcher
def foo(a):
    raise BaseException

@ExceptionCatcher(callback=lambda: 42)
def bar(a):
    return 1 / a
    
print(foo())  # None
print(bar(0))  # 42
print(bar(1))  # 1
```

As context manager
```python
with ExceptionCatcher:
    raise BaseException

with ExceptionCatcher(callback=lambda: 42) as catcher:
    raise BaseException
    
print(catcher.failed)  # True
print(catcher.result)  # 42
```
