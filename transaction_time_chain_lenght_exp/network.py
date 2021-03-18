#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os


# In[ ]:


class Network:
    
    def build(self,n,k):
        """this function creates a random connected network 
        with and n nodes and maximum number of k neighbors for each node"""
        pass 
    
    def get_nodes(self):
        """returns a list of nodes in the network"""
        
        """for this milestone, we return a hardcoded list"""
        
        return ['1','2']
    
    def get_node_IP(self,node_ID):
        
        """
        this fucntion returns the IP address of each node in the network
        """
        
        network_topology_file = open('DNS_server_cache.txt', "r")
        for line in network_topology_file:
            if line:
                IP_in_cache = line.split(":")[1]
                IP_in_cache = IP_in_cache.replace('\n','')
                IP_in_cache = IP_in_cache.replace('\t','')
                IP_in_cache = IP_in_cache.replace('"', '')
                node_value = line.split(":")[0]
                node_value = node_value.replace('\n','')
                node_value = node_value.replace('\t','')
                node_value = node_value.replace('"', '')
                if node_ID == node_value:
                    return IP_in_cache
                
    def get_neighbors(self,node_ID):
        """
        this fucntion returns the list of neighbors of the node_ID in the network
        """
        neighbors = []
        network_topology_file = open('network_topology.txt', "r")
        for line in network_topology_file:
            if line:
                edge = line.split(',')
                neighbor1 = edge[0]
                neighbor1 = neighbor1.replace('\n','')
                neighbor1 = neighbor1.replace('\t','')
                neighbor2 = edge[1]
                neighbor2 = neighbor2.replace('\n','')
                neighbor2 = neighbor2.replace('\t','')   
                neighbor1 = neighbor1.replace('"', '')
                neighbor2 = neighbor2.replace('"', '')
                if node_ID == neighbor1 or node_ID == neighbor2:
                    if neighbor1==node_ID:
                        if neighbor2 not in neighbors:
                            neighbors.append(neighbor2)
                    else:
                        if neighbor1 not in neighbors:
                            neighbors.append(neighbor1)
                        
        #neighbor_IPs = ["127.0.0.1"]
        return neighbors

