#!/usr/bin/env python
# coding: utf-8

# In[ ]:


class Warehouse:
    def get_required_items(self,node_ID):
        items = []
        each_node_required_items_file = open('each_node_required_items.txt', "r")
        for line in each_node_required_items_file:
            if line:
                if node_ID in line:
                    item = line.split(':')[1]
                    item = item.replace('\n','')
                    item = item.replace('\t','')
                    item = item.replace('"', '')
                    items.append(item)   
        return items
    
    
    def get_items_to_sell(self,node_ID):
        items = []
        each_node_selling_items_file = open('each_node_selling_items.txt', "r")
        for line in each_node_selling_items_file:
            if line:
                node_in_file = line.split(':')[0]
                if node_ID in node_in_file:
                    item = line.split(':')[1]
                    item = item.replace('\n','')
                    item = item.replace('\t','')
                    item = item.replace('"', '')
                    items.append(item)   
        return items
    
    
        

