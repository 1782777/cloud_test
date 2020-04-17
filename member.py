import threading
import json
from abc import ABCMeta, abstractmethod
import struct

import numpy as np
#from server import server

class member(object):
    __metaclass__ = ABCMeta

    def __init__(self,socket,ip,server,name,mtype):
        #self.type =type
        self.name = name
        self.type = mtype
        self.ip=ip
        self.socket = socket
        self.server = server
        self.inconnect = False
        self.link = None
        self.rev_thread = threading.Thread(target=self.rev)
        self.rev_thread.setDaemon(True)
        self.rev_thread.start()
        
        print name+'    ip:'+ip[0]+' is login server'
    

    def rev(self):
        while True:
              #print self.socket
            msg_len = 0
            try:
                bytes_len = self.socket.recv(4)
                msg_len = struct.unpack('i',bytes_len)[0]
                
                #print msg_len
                
            except:
                print 'socket broken!'
                # msg_dic ={'type':'disconnect'}
                # msg_js =json.dumps(msg_dic)
                # if self.link:
                #     self.link.send(msg_js)
                #     self.link =None
            
            if len(bytes_len) ==0:
                msg_dic ={'type':'disconnect'}
                msg_js =json.dumps(msg_dic)
                if self.link:
                    self.link.send(msg_js)
                    self.link =None

                self.disconnect()
                
                return

            if msg_len>50000 or msg_len<1:
                continue
            
            oncelen =0
            res =''
            while oncelen < msg_len:
                msg = self.socket.recv(msg_len)
                oncelen += len(msg)
                res += msg
            #print res
            # data = np.fromstring(res, dtype='uint8')
            # self.image = cv2.imdecode(data, 1)
            # cv2.imshow(self.name, self.image) 
            # cv2.waitKey(0)==27
            #print len(res)
            
            #print rev_msg
            
            try:
                
                json_info = json.loads(res)
                #print json_info
            except:
                #print res
                #print 'json faild=========================================================='
                if self.link!=None:
                    self.link.send(res)
                continue
            
            self.analysis_json(json_info)

    @abstractmethod
    def send(self,data):
        pass

    @abstractmethod
    def analysis_json(self,info):
        pass
        # '''
        # set init car and phone base
        # '''
        # if info['type'] =='init':
        #     self.type =info['which']
        #     self.name = info['name']
        #     if self.type =='car':
        #         self.server.add_carlist(self)
        #     else:
        #         self.server.add_phone_list(self)
        #     print 'a '+ self.type +' login server name:'+ self.name

    @abstractmethod
    def disconnect(self):
        pass

    def setlink(self,link):
        self.link = link
    

class Car(member):
    def __init__(self,socket,ip,server,name,mtype):
        super(Car, self).__init__(socket,ip,server,name,mtype)
         
    def analysis_json(self,info): 
        if self.link!=None:
            #print self.link
            self.link.send(json.dumps(info).encode())

    def DropPhone(self):
        self.link =None  

    def send(self,data):
        self.socket.sendall(data) 

    def disconnect(self):
        print 'car::' + str(self.ip)+' is disconnect!'
        self.server.remove_car(self)
        if self.link !=None:
            dic = {'type':'disconnect'}
            js = json.dumps(dic)
            self.link.socket.sendall(js.encode())


class Phone(member):
    def __init__(self,socket,ip,server,name,mtype):
        super(Phone, self).__init__(socket,ip,server,name,mtype)

    def send(self,data):
        try:
            ret =struct.pack('i',len(data))
            self.socket.sendall(ret)
            self.socket.sendall(data)
            #print ret,data
        except:
            #self.disconnect()
            print 'phone send fald'
    
    def analysis_json(self,info): 
        print 'phone rev json::'
        if info['type'] == 'getcarlist':
            dic_list = []
            for name in self.server.getcarlist():
                print name
                dic_name ={'name':name}
                dic_list.append(dic_name)
            dic = {'type':'carlist'}
            dic.update({'carlist':dic_list})
            js = json.dumps(dic)
            print js
            self.send(js.encode())
        if info['type'] == 'linkcar':
            car_ip= info['ip'].split(':')[1]
            self.link_car(car_ip)
        else:
            self.say_to_car(info)

    def link_car(self,carip):
        for car in self.server.car_list:
            print carip ,car.ip[0]
            if carip == car.ip[0]:
                self.link = car
                car.link = self
                dic = {'type':'phonelink'}
                js = json.dumps(dic)
                self.link.send(js.encode())
                print 'link a car~'

    def say_to_car(self,word):
        if self.link !=None:
            print word
            self.link.send(json.dumps(word).encode())

    def disconnect(self):
        print 'phone::' + str(self.ip)+' is disconnect!'
        self.server.remove_phone(self)
        if self.link !=None:
            self.link.DropPhone()
            dic = {'type':'disconnect'}
            js = json.dumps(dic)
            self.link.socket.sendall(js.encode())