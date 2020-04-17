#coding=utf8
import socket
import threading
import gc
import time
import json
import sys
from member import member,Car,Phone

reload(sys)
sys.setdefaultencoding('utf8')

class ZXServer:
    def __init__(self):
        self.car_list =[]
        self.phone_list =[]
        self.tcp_socket_host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        # 服务器端口回收操作（释放端口）
        self.tcp_socket_host.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,True)

        # 2绑定端口
        self.tcp_socket_host.bind(('172.16.31.10',8080))
        #self.tcp_socket_host.bind(('222.240.49.2',8080))

        # 3监听  变为被动套接字
        self.tcp_socket_host.listen(256)    #128可以监听的最大数量，最大链接数
        self.listen()

    def listen(self):
        while True:
            print 'wait and listening'
            socket_fuwu,addr_client=self.tcp_socket_host.accept()  #accept(new_socket,addr)
            '''
                set init car and phone base
            '''
            try:
                rev_msg_ = socket_fuwu.recv(4)
                rev_msg = socket_fuwu.recv(1024)
                # print 'server_rev_msg_::'+rev_msg_
                # print 'server_rev_msg::'+rev_msg
                json_info = json.loads(rev_msg)
            except:
                print 'init menber fail!'
                continue

            if json_info['type'] =='init':
                mtype =json_info['which']
                name = json_info['name']
                if mtype =='car':
                    _car = Car(socket_fuwu,addr_client,self,name,mtype)
                    for car in self.car_list:
                        if car.ip==addr_client:
                            car_list.remove(car)
                    self.add_carlist(_car)
                else:
                    _phone = Phone(socket_fuwu,addr_client,self,name,mtype)
                    self.add_phonelist(_phone)


            

    

    def add_carlist(self,car):
        self.car_list.append(car)
        print 'carlist == ',len(self.car_list)

    def add_phonelist(self,phone):
        self.phone_list.append(phone)
        print 'phonelist == ',len(self.phone_list)

    def remove_car(self,car):
        self.car_list.remove(car)
        print 'carlist == ',len(self.car_list)

    def remove_phone(self,phone):
        self.phone_list.remove(phone)
        print 'phonelist == ',len(self.phone_list)

    def getcarlist(self):
        names =[]
        for cars in self.car_list:
            print cars.name,cars.ip
            names.append(cars.name+":"+cars.ip[0])
        return names

    def del_member(self,member):
        
        del member
        gc.collect()
        print('断开')

if __name__ == '__main__':
    ZXServer()