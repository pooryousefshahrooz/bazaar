#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from network import *
from node import *
from conf import *
import socket
import time
import random
import sys
import logging
import threading
from threading import Thread


# In[5]:





# In[6]:


# init()


# In[ ]:


import trace 
import threading 
import time 
class thread_with_trace(threading.Thread): 
    def __init__(self, *args, **keywords): 
        threading.Thread.__init__(self, *args, **keywords) 
        self.killed = False
  
    def start(self): 
        self.__run_backup = self.run 
        self.run = self.__run       
        threading.Thread.start(self) 
  
    def __run(self): 
        sys.settrace(self.globaltrace) 
        self.__run_backup() 
        self.run = self.__run_backup 
  
    def globaltrace(self, frame, event, arg): 
        if event == 'call': 
            return self.localtrace 
        else: 
            return None
  
    def localtrace(self, frame, event, arg): 
        if self.killed: 
            if event == 'line': 
                raise SystemExit() 
        return self.localtrace 
  
    def kill(self): 
        self.killed = True


# In[ ]:


global start_time
start_time = round(time.time() * 1000)
def bazaar():  
    # first get the configuration parameters and network topology etc.
    conf = Conf()
    network = Network()
    n,k = conf.get_n_k()
    nodes = network.get_nodes()
    port_number = 8080
    
    # the list of test cases
    test_cases = ['test case 1','test case 2','test case 3']
    
    # list of items
    items_on_market = ['fish','boar','salt']

    for test_case in test_cases:
        each_node_role = {}
        if test_case == 'test case 1':
            each_node_role['1'] = 'buyer'
            each_node_role['2'] = 'seller'
            item_to_sell = 'fish'
            item_to_buy = 'fish'
            buyer_ID = '1'
            seller_ID = '2'
        elif test_case =='test case 2':
            each_node_role['1'] = 'buyer'
            each_node_role['2'] = 'seller'
            item_to_sell = 'boar'
            item_to_buy = 'fish'
            buyer_ID = '1'
            seller_ID = '2'
        else:
            test_counter = 1
            while(True):
                # we wait for 1 seconds between each test for the third test case
                
                time.sleep(1)
                for node in nodes:
                    random_value = random.randint(1,10)
                    if random_value<5:
                        each_node_role['1'] = 'buyer'
                        each_node_role['2'] = 'seller'
                        buyer_ID = '1'
                        seller_ID = '2'
                    else:
                        each_node_role['1'] = 'seller'
                        each_node_role['2'] = 'buyer'
                        buyer_ID = '2'
                        seller_ID = '1'
                print('setup for ',str(test_counter),'th test of ',test_case,':')
                test_counter +=1
                item_to_sell = items_on_market[random.randint(0,len(items_on_market)-1)]
                item_to_buy = items_on_market[random.randint(0,len(items_on_market)-1)]
                neighbor_IPs = network.get_neighbors(buyer_ID)
                print("buyer (buyer ID:%s) wants to purchase %s and seller (seller ID %s) has %s for selling"%(buyer_ID,item_to_buy,seller_ID,item_to_sell))
                thread1 = thread_with_trace(target=seller,args=(seller_ID,item_to_sell,neighbor_IPs,port_number))
                thread2 = thread_with_trace(target=buyer,args= (buyer_ID,item_to_buy,neighbor_IPs,port_number))
                thread1.start()
                #time.sleep(1)
                thread2.start()
                time.sleep(1)
                thread1.kill()
                thread1.join()
                thread2.kill()
                thread2.join()
        neighbor_IPs = network.get_neighbors(buyer_ID)
        print('setup for ',test_case,':')
        print("buyer (buyer ID:%s) wants to purchase %s and seller (seller ID %s) has %s for selling"%(buyer_ID,item_to_buy,seller_ID,item_to_sell))
        thread1 = thread_with_trace(target=seller,args=(seller_ID,item_to_sell,neighbor_IPs,port_number))
        thread2 = thread_with_trace(target=buyer,args= (buyer_ID,item_to_buy,neighbor_IPs,port_number))
        thread1.start()
        thread2.start()
        time.sleep(1)
        thread1.kill()
        thread1.join()
        thread2.kill()
        thread2.join()


# In[ ]:


bazaar()

