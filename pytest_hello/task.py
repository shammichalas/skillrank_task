# test_hello.py
from task import say_hello

def test_say_hello():
    assert say_hello() == "hello world"
