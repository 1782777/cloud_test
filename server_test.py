import socketserver
import json
from abc import ABCMeta, abstractmethod
import struct
#import numpy as np

CARLIST=[]
PHONELIST=[]

class MyTCPHandler(socketserver.BaseRequestHandler):
    

    def handle(self):
        mtype = ''
        name = ''
        try:
            #data = self.request.recv(4)
            data = self.request.recv(1024).decode('utf8')
            print(data)
            json_info = json.loads(data)
            if json_info['type'] =='init':
                mtype =json_info['which']
                name = json_info['name']
        except:
            print ('hack attack me!')

        if mtype =='car':
            car = Car(self.request,self.client_address[0])
        elif mtype =='phone':
            phone = Phone(self.request,self.client_address)
                
        
        
    def setup(self):
        print("before handle,连接建立：",self.client_address)
        
    def finish(self):
        print("finish run  after handle")
        for car in CARLIST:
            if car.add == self.client_address:
                CARLIST.remove(car)
        
    



class Manager():
    __metaclass__ = ABCMeta
    def __init__(self,resquest,address):
        self.request =resquest
        self.add = address
        self.link = None
        self.buff_len=0
        self.loop()
    
    def loop(self):
        while True:
            try:
                data=self.request.recv(1024)
                #print(data)
            except Exception as e:
                print(self.add,"disconnect",e)
                self.request.close()
                

            if not data:
                print("connection lost")
                self.disconect()
                break
            #print(self.add,data)
            self.rev(data)

    @abstractmethod
    def rev(self,data):
        pass 

    @abstractmethod
    def disconect(self):
        pass 

    def send_append_data(self,data):
        # self.request.send(data)  
        
        try:
            self.request.send(b'\xaa\xff')
            self.request.send(data)
            self.request.send(b'\xff\xaa')
        except:
            #self.disconnect()
            print ('phone send fald')

    def sendcarlist(self):
        print(len(CARLIST))
        dic_list =[]
        for cars in CARLIST:
            dic_name ={'name':cars.add}
            dic_list.append(dic_name)
        dic = {'type':'carlist'}
        dic.update({'carlist':dic_list})
        js = json.dumps(dic)
        print (js)
        self.send_append_data(js.encode())
           

class Car(Manager):
    def __init__(self,resquest,address):
        print('join a car')
        CARLIST.append(self)
        super(Car, self).__init__(resquest,address)

    def rev(self,data):
        if self.link:
            self.link.request.send(data)

    def disconect(self):
        CARLIST.remove(self)  
        if self.link:
            dic = {'type':'disconnect'} 
            js = json.dumps(dic)
            self.link.send_append_data(js.encode())   
            self.link.link =None
        
       
       
    


class Phone(Manager):
    def __init__(self,resquest,address):
        print('join a phone')
        PHONELIST.append(self)
        super(Phone, self).__init__(resquest,address)
        
    def rev(self,data):
        try:
            data_json= data.decode('utf8')
            json_info = json.loads(data_json)
            if json_info['type']=='getcarlist':
                self.sendcarlist()
            if json_info['type']=='linkcar':
                self.linkcar(json_info['ip'])
        except Exception as e:
            print ('phonerev;',e)
        if self.link:
            self.link.request.send(data)
       
    def linkcar(self,ip):
        for car in CARLIST:
            print (ip ,car.add)
            if ip == car.add:
                self.link = car
                car.link = self
                print ('link a car~')

    def disconect(self):
        PHONELIST.remove(self)
        if self.link:
            dic = {'type':'disconnect'} 
            js = json.dumps(dic)
            self.link.request.send(js.encode()) 
            self.link.link =None       

HOST,PORT = "172.16.31.10",8080

server=socketserver.ThreadingTCPServer((HOST,PORT),MyTCPHandler)#mutilt
server.serve_forever()