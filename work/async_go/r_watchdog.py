from util import *

class Call:
    last_call=0
    
    @go_loop(0.1)
    async def dummy(self):
        if self.last_call>0:self.last_call-=1
C=Call()
f=asyncio.create_task(C.dummy())

def foo():
    return getattr(C,"last_call")

class Watch:    
    def __init__(self,watch_func):
        self.last=False
        self.watch_func=watch_func
    
    @go_loop(0.1)
    async def foo(self):
        if self.watch_func()<=0:
            if self.last:
                print("do_stuff")
                self.last=False
        else:self.last=True
        

