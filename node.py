#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import socket
import time
import logging
import threading
from threading import Thread


# In[ ]:


start_time = 0.0


# In[ ]:


def seller(node_ID,product_to_sell,neighbor_IPs,port_number):
    class ClientThread(threading.Thread):
        def __init__(self,clientAddress,clientsocket):
            threading.Thread.__init__(self)
            self.csocket = clientsocket
            #print ("New connection added: ", clientAddress)
        def run (self):
            """waits for lookup requests"""
            #print ("Connection from : ", clientAddress)
            #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
            msg = ''
            while True:
                data = self.csocket.recv(2048)
                msg = data.decode()
                if msg:
                    #print('this is the message arrived from buyer ',msg)
                    #print(msg.split(','))
                    buyer_ID = msg.split(',')[0]

                    neighbor_ID = msg.split(',')[1]
                    product_name = msg.split(',')[2]
                    message_type = msg.split(',')[3]

                    if message_type=='bye':
                        break
                    #print ("from client", msg)
                    if product_name ==product_to_sell and message_type =='announce':
                        """seller receives the announcement form neighbor"""
                        new_message = node_ID+','+node_ID+','+product_name+','+'negotiate'
                    elif product_name ==product_to_sell and message_type =='negotiate':
                        """the buyer contacted me about buying the product that I have"""
                        new_message = node_ID+','+node_ID+','+product_name+','+'sold'
                    elif product_name !=product_to_sell and message_type =='announce':
                        """we do not have this item on the market"""
                        new_message = node_ID+','+node_ID+','+product_name+','+'not_exist'
                    self.csocket.send(bytes(new_message,'UTF-8'))
    
    seller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    seller_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # lets listen to the neighbors
    for neighbor_IP in neighbor_IPs:
        seller_socket.bind((neighbor_IP, port_number))
    seller_socket.listen(1)
    clientsock, clientAddress = seller_socket.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
        
def announce(node_ID,target_product,neighbor_IPs,port_number):
    
    """here the buyer announce his request to all neighbors.
    for this milestone, we assume as there are only two nodes in the network, 
    we do not need to get the list of neighbors from the network script"""
    
    global start_time
    # we set the begining of the announcement phase as start time 
    start_time = round(time.time() * 1000) 
    for neighbor_IP in neighbor_IPs:
        buyer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        buyer_socket.connect((neighbor_IP, port_number))
        new_message = node_ID+','+node_ID+','+target_product+','+'announce'
        buyer_socket.sendall(bytes(new_message,'UTF-8'))
    return buyer_socket
    
def buyer(node_ID,target_product,neighbor_IPs,port_number):
    """
    buyer process starts with announcing the item that he/she wishes to buy
    """
    buyer_socket =announce(node_ID,target_product,neighbor_IPs,port_number)
    bought_target_item = False
    global start_time
    
    """waiting to receive reply messages from neighbors"""
    
    while not bought_target_item:
        in_data =  buyer_socket.recv(1024)
        received_from_neighbor = in_data.decode()
        if received_from_neighbor:
            buyer_ID = received_from_neighbor.split(',')[0]
            neighbor_ID = received_from_neighbor.split(',')[1]
            product_name = received_from_neighbor.split(',')[2]
            message_type = received_from_neighbor.split(',')[3]
            if message_type=='negotiate':# means the seller has the item and wants to sell it
                new_message = node_ID+','+node_ID+','+target_product+','+'negotiate'
                buyer_socket.sendall(bytes(new_message,'UTF-8'))
                waiting_flag = True
            elif message_type=='sold':# means the seller has sold the item to me.
                
                end_time = round(time.time() * 1000)
                print("buyer bought ",target_product,'from ',neighbor_ID)
                end_time = round(time.time() * 1000)
                print(" **** Transaction time: %s milliseconds ****"%(end_time - start_time))
                bought_target_item = True
                break
            elif message_type=='not_exist':# means the seller does not have this item!
                end_time = round(time.time() * 1000)
                print("buyer could not buy ",target_product,'from ',neighbor_ID,'. Seller did not have it!')
                end_time = round(time.time() * 1000)
                print(" **** Transaction time: %s milliseconds ****"%(end_time - start_time))
                bought_target_item = True
                break
            else:
                #pass
                print('this is the message we do not captuate from seller ',received_from_neighbor)
    buyer_socket.close()


# In[ ]:





# In[ ]:




