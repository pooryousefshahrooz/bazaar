#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import os
from _thread import *
import socket
import os
import time
import random
import logging
import threading
from threading import Thread
from _thread import *
import sys
from network import *
from warehouse import *
from seller_node import *
from conf import *
import json
import select
from datetime import datetime
lock = threading.Lock()
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# In[ ]:


global_tll_value =100# the default value of the time to live for packets in the network for each phase


# In[ ]:


class Seller_thread:
    def server(self,seller_ID,server_IP):
        """
        this function runs a server for the seller node that continuesly listen to the requests from clients
        """
        self.my_ID = seller_ID
        self.each_item_lock = {'test':False}
        warehouse = Warehouse()
        self.items_to_sell = warehouse.get_items_to_sell(seller_ID)
        t = threading.currentThread()
        ServerSideSocket = socket.socket()
        #host = '127.0.0.5'
        host = server_IP 
        port = random_port
        ThreadCount = 0
        try:
            ServerSideSocket.bind((host, port))
        except socket.error as e:
            print(str(e))

        #print('Seller %s is listening..'%(seller_ID))
        ServerSideSocket.listen(5)

        def multi_threaded_client(connection,client_connected_to_me_IP):
            """
            for each established connection, this function is called to handle that connection
            
            """
            connection.send(str.encode('Server is working:'))
            while True:
                
                if global_out_going_queue:
                    
                    tmp_queue = []
                    lock.acquire()
                    for message in global_out_going_queue:
                        tmp_queue.append(message)
                    if len(tmp_queue)>0:
                        for message in tmp_queue:
                            json_message = json.loads(message) 
                            msg_buyer_ID = json_message['buyer_ID']
                            msg_product_name = json_message['product_name']
                            if json_message['message_type'] == 'announcement' and json_message['sender']== self.my_ID and json_message['sender_IP']==server_IP:

                                my_IP_address = network.get_node_IP(self.my_ID)
                                json_message['neighbor_IP'] = my_IP_address
                                new_dumped_message = json.dumps(json_message)
                                connection.sendall(str.encode(new_dumped_message))
                                global_out_going_queue.remove(message)
                            elif json_message['message_type'] == 'back_propagation' and json_message['sender']== self.my_ID and json_message['sender_IP']==server_IP: 

                                connection.sendall(str.encode(message))

                                global_out_going_queue.remove(message)
                    lock.release()
                """ here we use select call to avoid blocking I/O"""
                connection.setblocking(0)
                ready = select.select([connection], [], [], 0.001)
                if ready[0]:
                    data = connection.recv(2048)
                    rcvd_message = data.decode('utf-8')
                    try:
                        if rcvd_message:
                            rcvd_message_json = json.loads(rcvd_message)
                            if rcvd_message_json:
                                response = self.rcvd_message_handler(rcvd_message_json)
                                if response:
                                    connection.sendall(str.encode(response))
                    except:
                        pass

        while True:
            Client, address = ServerSideSocket.accept()
            host, port = Client.getpeername()
            start_new_thread(multi_threaded_client, (Client,host))
            ThreadCount += 1

        ServerSideSocket.close()

    def check_warehouse(self,product_name):
        """check if the seller has this item in its selling list"""
        if product_name in self.items_to_sell:
            return True
        else:
            return False
        
    def announce(self,seller_ID,rcvd_message_json):
        """
        this fuction will relay the received announcement message to all neighbors
        """
        ttl_value = rcvd_message_json["ttl_value"]
        if rcvd_message_json["message_type"] =='announcement':
            product_name = rcvd_message_json["product_name"]
            rcvd_buyer_ID = rcvd_message_json["buyer_ID"]
            rcvd_neighbor_IP = rcvd_message_json["sender_IP"]
            key = rcvd_buyer_ID+','+product_name
            if seller_ID in each_buyer_announced_messages:
                if key not in each_buyer_announced_messages[seller_ID]:
                    try:
                        each_buyer_announced_messages[seller_ID][key].append(rcvd_neighbor_IP)
                    except:
                        each_buyer_announced_messages[seller_ID][key]= []
                        each_buyer_announced_messages[seller_ID][key].append(rcvd_neighbor_IP)
                else:
                    if received_from_neighbor_IP not in each_buyer_announced_messages[seller_ID][key]:
                        each_buyer_announced_messages[seller_ID][key].append(rcvd_neighbor_IP)

            else:
                each_buyer_announced_messages[seller_ID] = {}
                each_buyer_announced_messages[seller_ID][key]= []
                each_buyer_announced_messages[seller_ID][key].append(rcvd_neighbor_IP)

            
            
            network = Network()
            if self.check_ttl(ttl_value):
                if rcvd_buyer_ID != seller_ID:
                    lock.acquire()
                    ttl_value = global_tll_value
                    ttl_value = int(ttl_value)-1
                    neighbors = network.get_neighbors(seller_ID)
                    my_IP_address = network.get_node_IP(seller_ID)
                    for neighbor in neighbors:
                        neighbor_IP = network.get_node_IP(neighbor)
                        if neighbor_IP != rcvd_neighbor_IP and neighbor != rcvd_buyer_ID:
                            announce = {"buyer_ID": rcvd_buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":product_name,
                                       "message_type":"announcement","ttl_value":str(ttl_value),"sender":self.my_ID,
                                       "sender_IP":my_IP_address} # a real dict.
                            message = json.dumps(announce)

                            global_out_going_queue.append(message)
                               
                    lock.release()
    def rcvd_message_handler(self,rcvd_message_json):
        
        """
        handles the received update message from a neighbor
        """
        if rcvd_message_json["message_type"] =='announcement':
            product_name = rcvd_message_json["product_name"]
            if self.check_warehouse(product_name):
                if product_name in self.each_item_lock:
                    if not self.each_item_lock[product_name]:
                        self.each_item_lock[product_name] = True
                        response_to_announcement = self.back_propagation(self.my_ID,rcvd_message_json,"back_propagation",True)
                    else:
                        response_to_announcement = self.back_propagation(self.my_ID,rcvd_message_json,"back_propagation",False)
                    self.announce(self.my_ID,rcvd_message_json)
                else:
                    self.each_item_lock[product_name] = True
                    response_to_announcement = self.back_propagation(self.my_ID,rcvd_message_json,"back_propagation",True)

                return response_to_announcement
            else:
                self.announce(self.my_ID,rcvd_message_json)
                response_to_announcement = self.back_propagation(self.my_ID,rcvd_message_json,"back_propagation",False)
                return response_to_announcement
        elif rcvd_message_json["message_type"] =='final':
            product_name = rcvd_message_json["product_name"]
            rcvd_seller_ID = rcvd_message_json["seller_ID"]
            if self.check_warehouse(product_name) and self.my_ID==rcvd_seller_ID:
                if rcvd_message_json["decision"] =='accepted':
                    lock.acquire()
                    self.items_to_sell.remove(product_name)
                    self.each_item_lock[product_name] = False
                    lock.release()
                else:
                    lock.acquire()
                    self.each_item_lock[product_name] = False
                    lock.release()
            else:
                product_name = rcvd_message_json["product_name"]
                rcvd_buyer_ID = rcvd_message_json["buyer_ID"]
                rcvd_neighbor_IP = rcvd_message_json["sender_IP"]
                rcvd_seller_ID = rcvd_message_json["seller_ID"]
                rcvd_decision = rcvd_message_json["decision"]
                network = Network()
                if self.check_ttl(ttl_value):
                    if rcvd_buyer_ID != self.my_ID:
                        lock.acquire()
                        ttl_value = global_tll_value
                        ttl_value = int(ttl_value)-1
                        neighbors = network.get_neighbors(self.my_ID)
                        my_IP_address = network.get_node_IP(self.my_ID)
                        for neighbor in neighbors:
                            neighbor_IP = network.get_node_IP(neighbor)
                            if neighbor_IP != rcvd_neighbor_IP and neighbor != rcvd_buyer_ID:
                                announce = {"buyer_ID": rcvd_buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":product_name,
                                           "message_type":"final","ttl_value":str(ttl_value),"sender":self.my_ID,
                                           "sender_IP":my_IP_address,"seller_ID":rcvd_seller_ID,"decision":rcvd_decision} # a real dict.
                                message = json.dumps(announce)
                                global_out_going_queue.append(message)

                        lock.release()
                
                
            
        elif rcvd_message_json["message_type"] =='back_propagation':
            ttl_value = rcvd_message_json["ttl_value"]
            ttl_value = int(ttl_value)-1
            network = Network()
            rcvd_buyer_ID = rcvd_message_json["buyer_ID"]
            rcvd_seller_ID = rcvd_message_json["seller_ID"]
            rcvd_sender_IP = rcvd_message_json["sender_IP"]
            result = rcvd_message_json["exist"]
            neighbors = network.get_neighbors(self.my_ID)
            for neighbor in neighbors:
                neighbor_IP = network.get_node_IP(neighbor)
                
                if neighbor_IP != rcvd_sender_IP and neighbor_IP !=my_IP_address:
                    back_propagation_message = {"buyer_ID": rcvd_buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":product_name,
                               "message_type":"back_propagation","ttl_value":str(ttl_value),"sender":self.my_ID,"seller_ID":rcvd_seller_ID,
                                               "sender_IP":my_IP_address,"exist":result} # a real dict.
                    message = json.dumps(back_propagation_message)
                    lock.acquire()
                    global_out_going_queue.append(message)
                    lock.release()
            
        return False
            
    def back_propagation(self,seller_ID,rcvd_message_json,message_type,exist_or_not):
        
        """
        back propagate the received update message
        """
        ttl_value = global_tll_value
        neighbors = network.get_neighbors(seller_ID)
        product_name = rcvd_message_json["product_name"]
        buyer_ID = rcvd_message_json["buyer_ID"]
        rcvd_msg_sender_IP = rcvd_message_json["sender_IP"]
        my_IP_address = network.get_node_IP(seller_ID)
        neighbor_IP = network.get_node_IP(neighbors[0])
        if exist_or_not:
            result = "yes"
        else:
            result = "no"
        back_propagation_message = {"buyer_ID": buyer_ID ,"neighbor_IP":rcvd_msg_sender_IP, "product_name":product_name,"seller_ID":seller_ID
                       ,"message_type":message_type,"ttl_value":str(ttl_value),"sender":seller_ID,
                                   "sender_IP":my_IP_address,"exist":result} # a real dict.
        message = json.dumps(back_propagation_message)
        return message
    def check_ttl(self,ttl_value):
        """
        check the ttl of the received update message 
        """
        if int(ttl_value)>0:
            return True
        else:
            return False
    def client(self,seller_ID,server_IP):
        
        """
        this funciton connect to a neighbor who is a seller or buyer
        """
        t = threading.currentThread()
        ClientMultiSocket = socket.socket()
        host = server_IP
        port = random_port

        try:
            ClientMultiSocket.connect((host, port))
        except socket.error as e:
            print("got error for client to connect to ",seller_ID,server_IP,str(e))
        network = Network()
        neighbors = network.get_neighbors(seller_ID)
        while True:
            
            if len(global_out_going_queue)>0:
                lock.acquire()
                tmp_queue = []
                for message in global_out_going_queue:
                    tmp_queue.append(message)

                if len(tmp_queue)>0:

                    for message in tmp_queue:
                        json_message = json.loads(message) 
                        if json_message['message_type'] == 'announcement' and json_message['neighbor_IP'] == server_IP and json_message['sender'] == seller_ID:
                            my_IP_address = network.get_node_IP(seller_ID)
                            json_message['neighbor_IP'] = my_IP_address 
                            json_message['sender'] = seller_ID 
                            Input = "announce sent by "+seller_ID
                            msg_buyer_ID = json_message['buyer_ID']
                            msg_product_name = json_message['product_name']
                            msg_sender_IP = json_message['sender_IP']
                            key = msg_buyer_ID+','+msg_product_name
                            if seller_ID in each_buyer_announced_messages:
                                try:
                                    each_buyer_announced_messages[seller_ID][key].append(msg_sender_IP)
                                except:
                                    each_buyer_announced_messages[seller_ID][key]= []
                                    each_buyer_announced_messages[seller_ID][key].append(msg_sender_IP)
                            else:
                                each_buyer_announced_messages[seller_ID] = {}
                                each_buyer_announced_messages[seller_ID][key]= []
                                each_buyer_announced_messages[seller_ID][key].append(msg_sender_IP)

                            new_dumped_message = json.dumps(json_message)
                            ClientMultiSocket.send(str.encode(new_dumped_message))
                            global_out_going_queue.remove(message)



                        if json_message['message_type'] == 'final' and json_message['neighbor_IP'] == server_IP and json_message['sender'] == seller_ID:
                            my_IP_address = network.get_node_IP(seller_ID)
                            json_message['neighbor_IP'] = my_IP_address 
                            json_message['sender'] = seller_ID 
                            Input = "announce sent by "+seller_ID
                            msg_buyer_ID = json_message['buyer_ID']
                            msg_product_name = json_message['product_name']
                            msg_sender_IP = json_message['sender_IP']
                            new_dumped_message = json.dumps(json_message)
                            ClientMultiSocket.send(str.encode(new_dumped_message))
                            global_out_going_queue.remove(message)



                        elif json_message['message_type'] == 'back_propagation' and json_message['neighbor_IP'] == server_IP and json_message['sender'] == seller_ID: 
                            Input = "back_propagation sent from "+json_message['seller_ID']
                            ClientMultiSocket.send(str.encode(message))
                            global_out_going_queue.remove(message)
                lock.release()
                
            try:
                ClientMultiSocket.setblocking(0)
                ready = select.select([ClientMultiSocket], [], [], 0.001)
                if ready[0]:
                    res = ClientMultiSocket.recv(1024)
                    if  "message_type" in res:
                        rcvd_message_json = json.loads(res)
                        if rcvd_message_json:
                            response = self.rcvd_message_handler(rcvd_message_json)
                            if response:
                                ClientMultiSocket.send(str.encode(response))
            except:
                pass
            
            
            
            
    def run_seller(self, seller_ID,seller_IP,server_IDs,server_client):
        
        """
        this fucntion runs a server and also a client that is connected to all neigbors of the seller node
        """
        if server_client =='server':
            t = threading.currentThread()
            t1 = threading.Thread(target=self.server,args = ([seller_ID,seller_IP]))
            t1.setDaemon(True)
            t1.start()
        else:
            for server in server_IDs:
                server_IP = each_node_IP[server]
                t2 = threading.Thread(target=self.client,args = ([seller_ID,server_IP]))
                t2.setDaemon(True)
                t2.start()


# In[ ]:


""" this are global variables in our system"""
global_out_going_queue = []
each_buyer_ongoing_item = {'test':{'test':True}}
each_buyer_announced_messages = {'test':{'test':'test'}}
network = Network()


# In[ ]:


class Buyer:
    def initializaion(self):
        self.queue = []
        self.queue.append("fish")
        self.queue.append("negotiate")
    def buyer_server(self,buyer_ID,buyer_server_IP):
        """
        this function runs a server for the buyer node. It will listen to the received connections from the neighbors
        """
        self.my_ID = buyer_ID
        t = threading.currentThread()
        ServerSideSocket = socket.socket()
        #host = '127.0.0.5'
        host = buyer_server_IP 
        port = random_port
        ThreadCount = 0
        try:
            ServerSideSocket.bind((host, port))
        except socket.error as e:
            print(str(e))

        ServerSideSocket.listen(5)

        def multi_threaded_client(connection,client_connected_to_me_IP):
            """when the server receives a connection request, this function will be called for that connection to handle that"""
            network = Network()
            connection.send(str.encode('Server is working:'))
            while True:
                try:
                    rcvd_message = connection.recv(2048)
                    if rcvd_message:
                        rcvd_message_json = json.loads(rcvd_message)
                        if rcvd_message_json:
                            self.rcvd_message_handler(buyer_ID,rcvd_message_json)
                except:
                    pass
                
                if global_out_going_queue:
                    lock.acquire()
                    tmp_queue = []

                    for message in global_out_going_queue:
                        tmp_queue.append(message)
                    if len(tmp_queue)>0:
                        for message in tmp_queue:
                            json_message = json.loads(message) 
                            msg_buyer_ID = json_message['buyer_ID']
                            msg_product_name = json_message['product_name']
                            if json_message['message_type'] == 'announcement' and json_message['neighbor_IP'] == client_connected_to_me_IP and json_message['sender']== buyer_ID:
                                Input = "announce sent by "+buyer_ID
                                
                                my_IP_address = network.get_node_IP(buyer_ID)
                                json_message['neighbor_IP'] = my_IP_address
                                
                                new_dumped_message = json.dumps(json_message)
                                connection.sendall(str.encode(new_dumped_message))
                                global_out_going_queue.remove(message)
                            elif json_message['message_type'] == 'back_propagation' and json_message['neighbor_IP'] == client_connected_to_me_IP and json_message['sender']== buyer_ID: 
                                connection.sendall(str.encode(message))
                                global_out_going_queue.remove(message)
                    lock.release()
                else:
                    response = 'Server message: ' + rcvd_message.decode('utf-8')

                    connection.sendall(str.encode(buyer_ID))

        while True:
            Client, address = ServerSideSocket.accept()
            host, port = Client.getpeername()
            start_new_thread(multi_threaded_client, (Client,host ))
            ThreadCount += 1
        ServerSideSocket.close()        
        
    def check_ttl(self,ttl_value):
        if int(ttl_value)>0:
            return True
        else:
            return False
        
    def rcvd_message_handler(self,buyer_ID,rcvd_message_json):
        ttl_value = rcvd_message_json["ttl_value"]
        if rcvd_message_json["message_type"] =='announcement':
            product_name = rcvd_message_json["product_name"]
            
            rcvd_buyer_ID = rcvd_message_json["buyer_ID"]
            rcvd_neighbor_IP = rcvd_message_json["sender_IP"]
            
            key = rcvd_buyer_ID+','+product_name
            if buyer_ID in each_buyer_announced_messages:
                if key not in each_buyer_announced_messages[buyer_ID]:
                    try:
                        each_buyer_announced_messages[buyer_ID][key].append(rcvd_neighbor_IP)
                    except:
                        each_buyer_announced_messages[buyer_ID][key]= []
                        each_buyer_announced_messages[buyer_ID][key].append(rcvd_neighbor_IP)
                else:
                    if received_from_neighbor_IP not in each_buyer_announced_messages[buyer_ID][key]:
                        each_buyer_announced_messages[buyer_ID][key].append(rcvd_neighbor_IP)

            else:
                each_buyer_announced_messages[buyer_ID] = {}
                each_buyer_announced_messages[buyer_ID][key]= []
                each_buyer_announced_messages[buyer_ID][key].append(rcvd_neighbor_IP)

            
            
            network = Network()
            if self.check_ttl(ttl_value):
                if rcvd_buyer_ID != buyer_ID:
                    lock.acquire()
                    ttl_value = global_tll_value
                    ttl_value = int(ttl_value)-1
                    neighbors = network.get_neighbors(self.my_ID)
                    my_IP_address = network.get_node_IP(buyer_ID)
                    for neighbor in neighbors:
                        neighbor_IP = network.get_node_IP(neighbor)
                        if neighbor_IP != rcvd_neighbor_IP and neighbor != rcvd_buyer_ID:
                            announce = {"buyer_ID": rcvd_buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":product_name,
                                       "message_type":"announcement","ttl_value":str(ttl_value),"sender":self.my_ID,
                                       "sender_IP":my_IP_address} # a real dict.
                            message = json.dumps(announce)

                            global_out_going_queue.append(message)
                               
                    lock.release()
                    
        if rcvd_message_json["message_type"] =='final':
            product_name = rcvd_message_json["product_name"]
            rcvd_buyer_ID = rcvd_message_json["buyer_ID"]
            rcvd_neighbor_IP = rcvd_message_json["sender_IP"]
            rcvd_seller_ID = rcvd_message_json["seller_ID"]
            rcvd_decision = rcvd_message_json["decision"]
            network = Network()
            if self.check_ttl(ttl_value):
                if rcvd_buyer_ID != buyer_ID:
                    lock.acquire()
                    ttl_value = global_tll_value
                    ttl_value = int(ttl_value)-1
                    neighbors = network.get_neighbors(self.my_ID)
                    my_IP_address = network.get_node_IP(buyer_ID)
                    for neighbor in neighbors:
                        neighbor_IP = network.get_node_IP(neighbor)
                        if neighbor_IP != rcvd_neighbor_IP and neighbor != rcvd_buyer_ID:
                            announce = {"buyer_ID": rcvd_buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":product_name,
                                       "message_type":"final","ttl_value":str(ttl_value),"sender":self.my_ID,
                                       "sender_IP":my_IP_address,"seller_ID":rcvd_seller_ID,"decision":rcvd_decision} # a real dict.
                            message = json.dumps(announce)

                            global_out_going_queue.append(message)
                               
                    lock.release()

                    
        elif rcvd_message_json["message_type"] =='back_propagation':
            product_name = rcvd_message_json["product_name"]
            rec_seller_ID = rcvd_message_json["seller_ID"]
            if buyer_ID in each_buyer_ongoing_item:
                if product_name in each_buyer_ongoing_item[buyer_ID]:
                    if each_buyer_ongoing_item[buyer_ID][product_name]:
                        if rcvd_message_json["exist"]=="yes":
                            global transaction_counter
                            print("*************** Transaction #%s: we got product %s from seller with ID %s ***************"%(transaction_counter,product_name,rec_seller_ID))
                            transaction_counter +=1
                            each_buyer_ongoing_item[buyer_ID][product_name] = False
                            self.final_message_to_seller(buyer_ID,product_name,rec_seller_ID,True)
#                         else:
#                             print("*********** we %s  were going to buy this product %s. we did not get it from %s"%(buyer_ID,product_name,rec_seller_ID))
            
                    else:
                        if rcvd_message_json["exist"]=="yes":
#                             print("*********** we %s  were going to buy this product %s but we got it from someon else not from %s"%(buyer_ID,product_name,rec_seller_ID))
                            self.final_message_to_seller(buyer_ID,product_name,rec_seller_ID,False)
            else:
                lock.acquire()
                ttl_value = int(ttl_value)-1
                network = Network()
                neighbors = network.get_neighbors(buyer_ID)
                rcvd_buyer_ID = rcvd_message_json["buyer_ID"]
                rcvd_seller_ID = rcvd_message_json["seller_ID"]
                rcvd_sender_IP = rcvd_message_json["sender_IP"]
                result = rcvd_message_json["exist"]
                key = rcvd_buyer_ID+','+product_name
                my_IP_address = network.get_node_IP(buyer_ID)
                if buyer_ID in each_buyer_announced_messages:
                    if key in each_buyer_announced_messages[buyer_ID]:
                        for neighbor_IP in each_buyer_announced_messages[buyer_ID][key]:   
                            if neighbor_IP != rcvd_sender_IP and neighbor_IP !=my_IP_address:
                                back_propagation_message = {"buyer_ID": rcvd_buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":product_name,
                                           "message_type":"back_propagation","ttl_value":str(ttl_value),"sender":buyer_ID,"seller_ID":rcvd_seller_ID,
                                                           "sender_IP":my_IP_address,"exist":result} # a real dict.
                                message = json.dumps(back_propagation_message)
                                global_out_going_queue.append(message)
                    each_buyer_announced_messages[buyer_ID] = {}
                lock.release()
                
    def final_message_to_seller(self,buyer_ID,product_name,rec_seller_ID,decision):
        """this function starts the final phase in our three phases for each transaction.
        It simply sends a final message to all of its neighbors
        """
        lock.acquire()
        ttl_value = global_tll_value
        if decision:
            result = "accepted"
        else:
            result = "not_accepted"
        network = Network()
        neighbors = network.get_neighbors(buyer_ID)
        my_IP_address = network.get_node_IP(buyer_ID)
        for neighbor in neighbors:
            neighbor_IP = network.get_node_IP(neighbor)
            final_message = {"buyer_ID": buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":product_name,
                       "message_type":"final","ttl_value":str(ttl_value),"sender":buyer_ID,
                       "sender_IP":my_IP_address,"seller_ID":rec_seller_ID,"decision":result} # a real dict.
            final_message = json.dumps(final_message)
            global_out_going_queue.append(final_message)
        lock.release()
        
    def client(self,buyer_ID,server_IP):
        t = threading.currentThread()
        ClientMultiSocket = socket.socket()
        host = server_IP
        port = random_port

        try:
            ClientMultiSocket.connect((host, port))
        except socket.error as e:
            print("got error for client to connect to ",buyer_ID,server_IP,str(e))

        network = Network()
        neighbors = network.get_neighbors(buyer_ID)
        while True:
            if len(global_out_going_queue)>0:
                
                tmp_queue = []
                
                for message in global_out_going_queue:
                    tmp_queue.append(message)
                if len(tmp_queue)>0:
                    lock.acquire()
                    for message in tmp_queue:
                        json_message = json.loads(message) 
                        if json_message['message_type'] == 'announcement' and json_message['neighbor_IP'] == server_IP and json_message['sender'] == buyer_ID:
                            my_IP_address = network.get_node_IP(buyer_ID)
                            json_message['neighbor_IP'] = my_IP_address 
                            json_message['sender'] = buyer_ID 
                            msg_buyer_ID = json_message['buyer_ID']
                            msg_product_name = json_message['product_name']
                            msg_sender_IP = json_message['sender_IP']
                            key = msg_buyer_ID+','+msg_product_name
                            if buyer_ID in each_buyer_announced_messages:
                                try:
                                    each_buyer_announced_messages[buyer_ID][key].append(msg_sender_IP)
                                except:
                                    each_buyer_announced_messages[buyer_ID][key]= []
                                    each_buyer_announced_messages[buyer_ID][key].append(msg_sender_IP)
                            else:
                                each_buyer_announced_messages[buyer_ID] = {}
                                each_buyer_announced_messages[buyer_ID][key]= []
                                each_buyer_announced_messages[buyer_ID][key].append(msg_sender_IP)

                            new_dumped_message = json.dumps(json_message)
                            ClientMultiSocket.send(str.encode(new_dumped_message))
                            global_out_going_queue.remove(message)
                            
                            
                            
                        if json_message['message_type'] == 'final' and json_message['neighbor_IP'] == server_IP and json_message['sender'] == buyer_ID:
                            my_IP_address = network.get_node_IP(buyer_ID)
                            json_message['neighbor_IP'] = my_IP_address 
                            json_message['sender'] = buyer_ID 
                            Input = "announce sent by "+buyer_ID
                            msg_buyer_ID = json_message['buyer_ID']
                            msg_product_name = json_message['product_name']
                            msg_sender_IP = json_message['sender_IP']
                            new_dumped_message = json.dumps(json_message)
                            ClientMultiSocket.send(str.encode(new_dumped_message))

                            global_out_going_queue.remove(message)
                            
                            
                            
                        elif json_message['message_type'] == 'back_propagation' and json_message['neighbor_IP'] == server_IP and json_message['sender'] == buyer_ID: 
                            Input = "back_propagation sent from "+json_message['seller_ID']
                            ClientMultiSocket.send(str.encode(message))
                            global_out_going_queue.remove(message)
                        
                    lock.release()
            
            ClientMultiSocket.setblocking(0)
            ready = select.select([ClientMultiSocket], [], [], 0.001)
            if ready[0]:
                res = ClientMultiSocket.recv(1024)
                if "message_type" in res:
                    rcvd_message_json = json.loads(res)
                    if rcvd_message_json:
                        self.rcvd_message_handler(buyer_ID,rcvd_message_json)


        
        ClientMultiSocket.close()
    def run_buyer(self, buyer_ID,buyer_IP,server_IDs,server_client):
        
        """this function runs a server for the buyer node to get the connection requests from the neighbors
        
        and also establish a connection between the node and its neighbors as a client
        
        It then starts the announcement phase for each item that it needs to buy
        """
        
        if server_client =='server':
            t = threading.currentThread()
            t1 = threading.Thread(target=self.buyer_server,args = ([buyer_ID,buyer_IP]))
            t1.setDaemon(True)
            t1.start()
        else:
            for server in server_IDs:
                server_IP = each_node_IP[server]
                t2 = threading.Thread(target=self.client,args = ([buyer_ID,server_IP]))
                t2.setDaemon(True)
                t2.start()
            time.sleep(2)
            
            self.queue = []
            warehouse = Warehouse()
            network = Network()
            buying_items = warehouse.get_required_items(buyer_ID)
            neighbors = network.get_neighbors(buyer_ID)
            my_IP_address = network.get_node_IP(buyer_ID)
            print("buying_items",buying_items)
            for item in buying_items:
                start = datetime.now()
                t_start = round(time.time()*1000)
                t_end = time.time() +10
                start = round(time.time() * 1000)
                lock.acquire()
                self.ongoing_shopping = True
                try:
                    each_buyer_ongoing_item[buyer_ID][item] = True
                except:
                    each_buyer_ongoing_item[buyer_ID] = {}
                    each_buyer_ongoing_item[buyer_ID][item] = True
                self.queue = []
                ttl_value = global_tll_value
                for neighbor in neighbors:   
                    neighbor_IP = network.get_node_IP(neighbor)
                    announce = {"buyer_ID": buyer_ID ,"neighbor_IP":neighbor_IP, "product_name":item,
                               "message_type":"announcement","ttl_value":str(ttl_value),"sender":buyer_ID,
                               "sender_IP":my_IP_address} # a real dict.
                    message = json.dumps(announce)
                    #print("we as %s are going to announce this %s to %s"%(buyer_ID,message,neighbor_IP))
                    global_out_going_queue.append(message)
                lock.release()
                while(each_buyer_ongoing_item[buyer_ID][item] and (time.time() <t_end)):
                    waiting = True
                global transaction_counter
                if not each_buyer_ongoing_item[buyer_ID][item]:
                    end = datetime.now()
                    end = round(time.time() * 1000)
                    print("*************** We bougth this product (%s) in %s milliseconds *************** \n"%(item,str(end-start)))
                elif time.time() >=t_end:
                    print(" Transaction ID # %s: Oops! None of the sellers had item %s for us (our ID: %s) or the transaction time took more than 6 seconds \n"%(transaction_counter,item,buyer_ID))
                    transaction_counter +=1
        


# In[ ]:


transaction_counter = 1

node_role_values = {'1':'client','2':'client','4':'client','5':'server'}

each_node_IP = {'1':'127.0.0.1',
               '2':'127.0.0.2',
               '3':'127.0.0.3',
               '4':'127.0.0.4',
               '5':'127.0.0.5'}
each_node_neighbors = {
                        '1':['2'],
                        '2':['1','4'],
                        '4':['2','5'],
                        '5':['4']
}
each_node_neighbors = {
                        '1':['2'],
                        '2':['1','4'],
                         '4':['2','5'],
                        '5':['4']}
random_port = random.randint(2000,4000)

for item,role in node_role_values.items():
    #time.sleep(2)
    if role =='server':
        seller = Seller_thread()
        t1 = threading.Thread(target=seller.run_seller,args = (item,each_node_IP[item],each_node_neighbors[item],'server'))
        t1.setDaemon(True)
        t1.start()
    else:
        buyer = Buyer()
        t2 = threading.Thread(target=buyer.run_buyer,args = (item,each_node_IP[item],each_node_neighbors[item],'server'))
        t2.setDaemon(True)
        t2.start()
time.sleep(2)
for item,role in node_role_values.items():
    
    if role =='server':
        t3 = threading.Thread(target=seller.run_seller,args = (item,each_node_IP[item],each_node_neighbors[item],'client'))
        t3.setDaemon(True)
        t3.start()
    if role !='server':
        buyer = Buyer()
        t4 = threading.Thread(target=buyer.run_buyer,args = (item,each_node_IP[item],each_node_neighbors[item],'client'))
        t4.setDaemon(True)
        t4.start()
        
        
        
main_thread = threading.current_thread()
for t in threading.enumerate():
    if t is main_thread:
        continue
logging.debug('joining %s', t.getName())
t.join()

