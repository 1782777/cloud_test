import socketserver
import json
from abc import ABCMeta, abstractmethod
import struct


class MyTCPHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        car =Car(self.request)

    def setup(self):
        print("before handle,连接建立：",self.client_address)
        
    def finish(self):
        print("finish run  after handle")

class Car():
    def __init__(self,request):
        self.sCount =0
        self.eCount=0
        self.isread =False
        self.mLen =0
        self.request =request
        try:
            while True:
                data = self.request.recv(1)
                #print(data)
                self.decode(data)
                if not data:
                    print("connection lost")
                    break
                
        except:
            print ('hack attack me!')

    def decode(self,data):
        if self.isread != True:
            if data==b'\xaa':
                self.sCount =1
                return
            if self.sCount ==1 :
                if data==b'\xff':
                    self.isread =True
                else:
                    self.sCount =0
        else:
            
            self.mLen+=1
            if data==b'\xff':
                self.eCount =1
                return
            if self.eCount ==1 :
                if data==b'\xaa':
                    self.isread =False
                    print(self.mLen)
                    self.mLen =0
                else:
                    self.eCount =0
            
            

        

HOST,PORT = "172.16.31.10",8080

server=socketserver.ThreadingTCPServer((HOST,PORT),MyTCPHandler)#mutilt
server.serve_forever()