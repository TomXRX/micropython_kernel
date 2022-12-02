from util import *
# 仅UDP
import ustruct as struct
def spliter(format,buffer):
    data=buffer[:struct.calcsize(format)]
    buffer=buffer[struct.calcsize(format):]
    ret=struct.unpack(format,data)
    if len(ret)==1:ret=ret[0]
    return ret,buffer


def get_wifi_location():
    import network
    wlan = network.WLAN(network.STA_IF)
    location=(wlan.ifconfig()[0], 8080)
    return location


import time

class UDP_Connection:
    def __init__(self,location=None):
        import socket
        if location is None:
            location=get_wifi_location()
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(location)
        self.s.setblocking(False)

    to=[]
    def __call__(self, *args, **kwargs):
        try:
            data,host = self.s.recvfrom(8192)
            if not host in self.to: self.to.append(host)
            return data
        except Exception as e:
            if e.args[0]==11:return

    last = 0
    def last_recv(self, check=True, wait=5):
        # 检查是否是同一个连接
        if check:
            return self.get_time() - self.last > wait
        else:
            self.last = self.get_time()

    def get_time(self):return time.ticks_ms()/1000

    def send(self,data):
        if len(self.to)==0:return   
        
        # use asyncio to handle loop send
        self.s.sendto(data,self.to[0])
        
        


class Responder(UDP_Connection):
    def __init__(self, *args,send_rate=100,):
        super().__init__(*args)
        self.encode_list=[]
        self.decode_list=[]
        self.encode_list.append(["I","get_num"])
        self.encode_list.append(["b","get_rssi"])

        self.decode_list.append(["I","to_num"])
        # ESP不支持assignment
        self.dict={"to_num":0}

        self.mode=0

        import network
        self.wlan = network.WLAN(network.STA_IF)

        
    def add_control_set(self,lis):
        self.decode_list.append(lis)
    def add_recv_set(self,lis):
        self.encode_list.append(lis)
        
    def get_num(self):
        return self.dict["to_num"]

    last = 0
    def last_recv(self, check=True, wait=5):
        # 检查是否是同一个连接
        if check:
            return self.get_time() - self.last > wait
        else:
            self.last = self.get_time()

    def get_time(self):return time.ticks_ms()/1000


    #ESP不支持assignment
    def decode(self,buffer):
        self.last_recv(0)
        for form,name in self.decode_list:
            data,buffer=spliter(form,buffer)

            if name=="to_num":
                if self.dict[name]>data:
                    if self.last_recv():break
            try:
                if hasattr(self, name):
                    if type(data)==tuple:
                        getattr(self, name)(*data)
                    else:getattr(self, name)(data)
                else:
                    self.dict[name]=data
            except Exception as e:
                print(form)
                print(data)
                print(e)


    def encode(self):
        buffer=b""
        for form, name in self.encode_list:
            if name in self.__dict__ and not callable(self.__dict__[name]):
                data = self.__dict__[name]
            elif hasattr(self, name):
                data = getattr(self, name)()
            try:

                if type(data) in [tuple, list]:
                    buffer += struct.pack(form, *data)
                else:
                    buffer += struct.pack(form, data)
            except Exception as e:
                print(form)
                print(data)
                print(e)
        return buffer

    def get_rssi(self):
        return self.wlan.status("rssi")

    
    def send(self):
        super().send(self.encode())
        
    
    def __call__(self, *args, **kwargs):
        if self.mode==0:
            data=super().__call__(*args,**kwargs)
            if data:
                self.decode(data)
                
    @go_loop(0.01)         
    async def loop_send(self):
        if len(self.to)==0:return
        # self.encode()
        #just to test ability
        self.send()
            
                
    @go_loop(0.1)         
    async def loop_recv(self):
        #not_working_at_unix
        
        data=self()
        if data:self.decode(data)



class ResponderDummy(Responder):
    def __init__(self, *args,send_rate=100,):
        UDP_Connection.__init__(self,*args)
        self.encode_list=[]
        self.decode_list=[]
        self.encode_list.append(["I","get_num"])
        self.encode_list.append(["b","get_rssi"])

        self.decode_list.append(["I","to_num"])
        # ESP不支持assignment
        self.dict={"to_num":0}

        self.mode=0
        
    def get_rssi(self):
        return 1

