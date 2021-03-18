#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import os
import time
import logging
import threading
from threading import Thread
from _thread import *
import sys
from network import *
from warehouse import *
from seller_node import *
lock = threading.Lock()
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# In[ ]:


global_ttl_value = 10


# In[ ]:


class Seller_thread:
    def run_server(self,seller_ID,seller_IP_address):
        t = threading.currentThread()
        ServerSideSocket = socket.socket()
        host = '127.0.0.1'
        host = seller_IP_address
        port = 2004
        ThreadCount = 0
        try:
            ServerSideSocket.bind((host, port))
        except socket.error as e:
            print(str(e))

        print('seller  %s Socket is listening.. on %s'%(seller_ID,seller_IP_address))
        ServerSideSocket.listen(5)

        def multi_threaded_client(connection,address):
            connection.send(str.encode('seller Server is working:'))
            for neighbor,IP in self.each_neighbor_IP.items():
                if IP == address:
                    self.neighbor_IP = address
            while True:
                time.sleep(3)
                tmp_queue = []
                lock.acquire()
                for item in self.queue:
                    tmp_queue.append(item)
                lock.release()
                for item in tmp_queue:
                    for key,value in item.items():
                        if key == self.neighbor_IP:
                            #Input = input('Hey there: ')
                            message = value
                            connection.sendall(str.encode(message))
                            lock.acquire()
                            self.queue.remove(item)
                            lock.release()
                
                #connection.sendall(str.encode(response))
#                 Input = input('Hey there: ')
                data = connection.recv(2048)
                response = 'seller Server message: ' + data.decode('utf-8')
                if not data:
                    print("we got no data!")
                    break
                self.received_handler(data)
                
            connection.close()

        while True:
            time.sleep(3)
            Client, address = ServerSideSocket.accept()
            print('seller Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(multi_threaded_client, (Client,address ))
            ThreadCount += 1
            print('seller Thread Number: ' + str(ThreadCount))
        ServerSideSocket.close()
    def start_selling(self,seller_ID):
        self.my_ID = seller_ID
        self.cause = {'test':'test'}
        self.back_propagated = {'test':'test'}
        self.queue = []
        network = Network()
        self.neighbors = network.get_neighbors(seller_ID)
        seller_IP = network.get_node_IP(seller_ID)
        self.each_neighbor_IP = {}
        for neighbor in self.neighbors:
            self.each_neighbor_IP[neighbor] = network.get_neighbors(neighbor)
        t = threading.currentThread()
        t = threading.Thread(target=self.run_server,args=([seller_ID,str(seller_IP)]))
        t.setDaemon(True)
        t.start()
        
    def check_warehouse(self,product_name):
        return True    
    def received_handler(self,msg):
        in_data =  msg
        received_from_neighbor = in_data.decode()
        if received_from_neighbor:
            buyer_ID = received_from_neighbor.split(',')[0]
            neighbor_ID = received_from_neighbor.split(',')[1]
            product_name = received_from_neighbor.split(',')[2]
            message_type = received_from_neighbor.split(',')[3]
            ttl_value = int(msg.split(',')[4])-1
            if ttl_value <=0:
                print("this packet has expired!")
            elif message_type=='announce':
                if self.check_warehouse(product_name):
                    print(" we %s have this item %s"%(self.my_ID,product_name))
                    ttl_value = global_ttl_value
                    port_number = 8080
                    network = Network()
                    neighbors = network.get_neighbors(self.my_ID)
                    if buyer_ID+','+product_name not in self.cause:
                        try:
                            self.cause[buyer_ID+','+product_name].append(neighbor_ID)
                        except:
                            self.cause[buyer_ID+','+product_name] = [neighbor_ID]
                    else:
                        if neighbor not in self.cause[buyer_ID+','+product_name]:
                            try:
                                self.cause[buyer_ID+','+product_name].append(neighbor_ID)
                            except:
                                self.cause[buyer_ID+','+product_name] = [neighbor_ID]
                    neighbors = self.cause[buyer_ID+','+product_name]
                    for neighbor in neighbors:
                        neighbor_IP= network.get_node_IP(neighbor)
                        self.back_propagate(buyer_ID,product_name,self.my_ID,neighbor_IP,ttl_value)
                        

                else:
                    if ttl_value <=0:
                        print("this message has expired!")
                    else:
                        if buyer_ID != self.my_ID:
                            network = Network()
                            neighbor_IP= network.get_node_IP(buyer_ID)
                            neighbors = network.get_neighbors(self.my_ID)
                            for neighbor in neighbors:
                                if neighbor != buyer_ID:
                                    if buyer_ID+','+product_name not in cause:
                                        self.cause[buyer_ID+','+product_name] = neighbor_ID
                                    self.announce(buyer_ID,product_name,buyer_ID,neighbor_IP,ttl_value)

            elif message_type=='back_propagation':
                if ttl_value <=0:
                    print("this packet has expired")
                else:
                    
                    if buyer_ID+","+product_name not in self.sold_items_buyers:
                        port_number = 8080
                        network = Network()
                        neighbors = network.get_neighbors(self.my_ID)
                        neighbors = self.cause[buyer_ID+','+product_name]
                        for neighbor in neighbors:
                            neighbor_IP= network.get_node_IP(neighbor)
                            self.back_propagate(buyer_ID,product_name,seller_ID,neighbor_IP,ttl_value)
            elif message_type=='negotiate':
                if neighbor_ID ==self.my_ID:
                    lock.acquire()
                    items_to_sell[product_name]  = items_to_sell[product_name]-1
                    try:
                        self.sold_items_buyers.append(buyer_ID+","+product_name)
                    except:
                        self.sold_items_buyers = [buyer_ID+","+product_name]
                    lock.release()
                    print("we sold this item",product_name,' to ',buyer_ID)

                else:
                    if ttl_value <=0:
                        print("this message has expired!")
                    else:
                        if buyer_ID != self.my_ID:
                            network = Network()
                            neighbor_IP= network.get_node_IP(buyer_ID)
                            neighbors = network.get_neighbors(self.my_ID)
                            for neighbor in neighbors:
                                if neighbor != buyer_ID:
                                    self.relay_nogotiation(buyer_ID,product_name,buyer_ID,neighbor_IP,ttl_value)
            else:
                pass
    #                     print('this is the message we do not captuate from seller ',received_from_neighbor)
        
    def back_propagate(self,buyer_ID,target_product,neighbor,neighbor_IP,ttl_value):
        """here the buyer announce his request to all neighbors.
        for this milestone, we assume as there are only two nodes in the network, 
        we do not need to get the list of neighbors from the network script"""
        ttl_value = global_ttl_value
        new_message = buyer_ID+','+neighbor+','+target_product+','+'back_propagation'+','+str(ttl_value)
        if buyer_ID+','+target_product not in self.back_propagated:
            lock.acquire()
            self.message_queue.append({neighbor:announcement})
            lock.release()
#             self.send_message(new_message,neighbor,neighbor_IP)
            try:
                self.back_propagated[buyer_ID+','+target_product].append(neighbor)
            except:
                self.back_propagated[buyer_ID+','+target_product] =[neighbor]
        else:
            if neighbor not in self.back_propagated[buyer_ID+','+target_product]:
#                 self.send_message(new_message,neighbor,neighbor_IP)
                lock.acquire()
                self.message_queue.append({neighbor:announcement})
                lock.release()
                try:
                    self.back_propagated[buyer_ID+','+target_product].append(neighbor)
                except:
                    self.back_propagated[buyer_ID+','+target_product] =[neighbor]

