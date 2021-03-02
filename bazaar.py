#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from Network import *
from node import *
from conf import *


# In[ ]:


def init():
    
    nodes = conf.get_nodes()
    each_node_role = {}
    for node in nodes:
        random = random.randint(1,10)
        if random<5:
            each_node_role[node] = 'buyer'
        else:
            each_node_role[node] = 'seller'
        

