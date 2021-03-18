#!/usr/bin/env python
# coding: utf-8

# In[ ]:


number_of_nodes= 2
number_of_neighbors = 1
read_from_file_or_create_random = True # change this if you do want to read from provided files

# In[ ]:


class Conf:
    def get_n_k(self):
        """get the value of k and n"""
        return 1,2
    
    def get_timeout_value(self):
        "this fucntion returns the number of seconds that the buyer can wait until it decides there is no seller in the network that has the item"
        return 6
    
    def get_read_from_file_or_create_random(self):
        """here you can set if we should read from provided files or create the input for the system randomly"""
        """ we will not create the network topology. We only will assing the role of each node in the network and assing different items to but or sell for each node"""
        return read_from_file_or_create_random

