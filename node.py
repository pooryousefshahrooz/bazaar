#!/usr/bin/env python
# coding: utf-8

# In[ ]:



class seller:
    
    def item_selection():
        """pick one of three items to sell"""
        pass
    def announcement(product_name):
        """reduce the hop count value and if hop count>0 find buyers by announcing what you wish to sell"""
        pass
    def reply(buyerID, sellerID):
        """this is a reply message to buyerID with the peerID of the seller"""
    
    def receive(item):
        """check if you have this item, sends back a response that traverses in the reverse direction back to the buyer. 
        otherwise pass it to neighbors if --hop count is not zero"""
        pass
    def sell(self)
        """Each seller starts with m items (e.g., m boars) to sell;
        upon selling all m items, the seller picks another item at random and 
        becomes a seller of that item"""
        """a seller waits for lookup requests from other peers and sends back a reply for each match. 
        Each lookup request is also propagated to all its neighbors."""
        
        
    
    
class buyer:
    def lookup (product_name,hopcount):
        """this procedure should search the network; 
        all matching sellers respond to this message with their IDs using a reply(buyerID, sellerID) call.
        The hop count is decremented at each hop and the message is discarded when it reaches 0.
        """
        pass
    def item_selection():
        """randomly pick an item and attempt to purchase it"""
        pass

    def announce(product_name):
        """find sellers by announcing what you wish to buy"""
        pass
    def buy(sellerID):
        """if multiple sellers respond, the buyer picks one at random
        and contacts it directly with the buy message. 
        
        A buy causes the seller to decrement the number of items in stock.
        """
        pass
    
    def buy_process():
        product_name = item_selection()
        """then waits a random amount of time, then picks another item to buy and so on"""
        """the buyer specifies a product_name using lookup. 
           Upon receiving replies, the buyer peer picks one matching seller
           and then connects directly to that peer to finish the transaction."""
        
    


# In[ ]:





# In[ ]:




