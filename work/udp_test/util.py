import uasyncio as asyncio
# from functools import wraps

def go_loop(t=0.001):
    def wrapper(func):
        # @wraps(func)
        async def wrapped(*args, **kwargs):
            while 1:
                await asyncio.sleep(t)
                ret=await func(*args, **kwargs)
                if ret:break
            return
        return wrapped
    return wrapper

def to_pop(li):
    def poper(ret_len=5):
        p=li[:ret_len]
        li.pop(0)
        return p
    return poper

def add_num(func):
    num=-1
    def go_num():
        nonlocal num
        num+=1
        # r=num,*func()
        # incompatible
        r=[num]
        r.extend(func())
        return r
    return go_num

class Buff(list):
    def __init__(self, iterable=(),maxlen=128):
        self.maxlen=maxlen
        assert len(iterable)<=maxlen
        super().__init__(iterable)
    def extend(self):
        raise NotImplementedError
    
    def append(self, item):
        if len(self)>=self.maxlen:
            self.pop(0)
        super().append(item)