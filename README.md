# bazaar
This project will implement a peer-to-peer market (bazaar). The bazaar contains two types of people (i.e., computing nodes): buyers and sellers. Each seller sells one of the following goods: fish, salt, or boars. Each buyer in the bazaar is looking to buy one of these three items.


how to run:
For running the system just simply run script three_phases_bazar_implementation.py in the root directory.

You can change the role of each node at the end of this script also.

The provided script will test the transaction time for only one buyer in the network. It also assumes that there is only one seller in the network. 

If you want to change the seller and buyer in the network, you can do as follows. Please especify one seller and one buyer among the nodes in the network_topology.txt file and set the selling items for the seller in the each_node_required_items.txt file. For the seller, assing the items that it has in its warehouse also in the file each_node_selling_items.txt. Please note that for testing the script, there shoudl be only one seller in the network.
