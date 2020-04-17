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
        else:
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
                break
            #print(self.add,data)
            self.rev(data)

    @abstractmethod
    def rev(self,data):
        pass 

    def send_data(self,data):
        # self.request.send(data)  
        
        try:
            ret =struct.pack('i',len(data))
            self.request.send(ret)
            self.request.send(data)
            #print ret,data
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
        self.send_data(js.encode())
           

class Car(Manager):
    def __init__(self,resquest,address):
        print('join a car')
        CARLIST.append(self)
        super(Car, self).__init__(resquest,address)

    def rev(self,data):
        if len(data)==4:
            self.buff_len = struct.unpack('i',data)[0]
            print(self.buff_len)
            if self.link:
                ret =struct.pack('i',self.buff_len)
                self.link.request.send(ret)

        tmplen = 0
        
        while tmplen<self.buff_len:
            try:
                data=self.request.recv(self.buff_len)
                if self.link:
                    self.link.request.send(data)
                tmplen+=len(data)
            except Exception as e:
                print(self.add,"disconnect",e)
                self.request.close()
            if not data:
                print("connection lost")
       
       
    


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
                # dic = {'type':'phonelink'}
                # js = json.dumps(dic)
                # self.link.send(js.encode())
                print ('link a car~')
            

HOST,PORT = "172.16.31.10",8080

server=socketserver.ThreadingTCPServer((HOST,PORT),MyTCPHandler)#mutilt
server.serve_forever()