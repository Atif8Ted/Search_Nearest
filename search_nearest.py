#!/usr/bin/python
import sys, filelocations
import logging
log = logging.getLogger("pyosm")
sys.path.append(filelocations.LIB_LOCATION)
import  argparse
import pyosm
from geocoder import *
from pyosm import OSMXMLFile
OSML=OSMXMLFile()
osm = pyosm.OSMXMLFile(filelocations.OSM_DATA_LOCATION)
from matplotlib import pyplot as plt
import networkx as nx

def error_info():
    e = sys.exc_info()[0]
    l = sys.exc_traceback.tb_lineno
    print 'The following error ocurred: ', e, l
    if 'exceptions.KeyError' in str(e):
		print 'You entered a value that was not found in the map.'
    elif 'exceptions.UnboundLocalError' in str(e):
		print 'You entered a value that was not found in the map.'
    elif 'sre_constants.error' in str(e):
		print 'You entered invalid symbols such as [ and ]'

"""Lets the user enter simple search key words, e.g. user enters 'cafe' and data becomes the OSM tag value 'amenity\': u\'cafe' for processing"""
def get_tag_value(dic, key):
    """find the value given a key"""
    return dic[key.lower()]
	
"""Create your own custom set of tags in osm_dict, a large set of key value pairs can be added here."""
osm_dict = {
    'cafe' : 'amenity\': u\'cafe',
    'school' : 'amenity\': u\'school',
    'college' : 'amenity\': u\'college',
    'library' : 'amenity\': u\'library',
    'restaurant' : 'amenity\': u\'restaurant',
    'bar' : 'amenity\': u\'bar',
    'bus station' : 'amenity\': u\'bus_station',
    'taxi' : 'amenity\': u\'taxi',
    'doctors' : 'amenity\': u\'doctors',
    'hospital' : 'amenity\': u\'hospital',
    'pharmacy' : 'amenity\': u\'pharmacy',
    'toilets' : 'amenity\': u\'toilets',
    'hotel' : 'tourism\': u\'hotel',
    'motel' : 'tourism\': u\'motel',
    'hostel' : 'tourism\': u\'hostel',
    'museum' : 'tourism\': u\'museum',
    'farm' : 'place\': u\'farm',
    'neighbourhood' : 'place\': u\'neighbourhood',
    'airfield' : 'military\': u\'airfield',
    'checkpoint' : 'military\': u\'checkpoint'
}

def nearest_node_tagged(nodeID, qry):
    try:
        #arbitrarily large starting distance for comparison
        nearestDist = 100000000
        for node in osm.nodes:
            match = MatchNode().match_node('\''+qry+'(.*)', str(osm.nodes[node].tags))
            newDist = distance_nodes(osm.nodes[nodeID]['lon'], osm.nodes[nodeID]['lat'], osm.nodes[node]['lon'], osm.nodes[node]['lat'])
            if match and newDist < nearestDist and node != nodeID:
                nearestDist = newDist
                nearestNode = node
                nearestTag = match.group(1)
        print '\n Your starting node is http://www.openstreetmap.org/node/'+str(nodeID)
        print '\n Nearest tagged node for your query is http://www.openstreetmap.org/node/'+str(nearestNode)
        print '\n Nearest node\'s tagged info is:'+str(nearestTag)
        graphNodes(osm.nodes[node]['lon'], osm.nodes[node]['lat'], osm.nodes[nearestNode]['lon'], osm.nodes[nearestNode]['lat'], nodeID, nearestNode, nearestTag)
    except:
        error_info()

def farthest_node_tagged(nodeID, qry):
    try:
        #arbitrarily small starting distance for comparison
        farthestDist = 0
        for node in osm.nodes:
            match = MatchNode().match_node('\''+qry+'(.*)', str(osm.nodes[node].tags))
            newDist = distance_nodes(osm.nodes[nodeID]['lon'], osm.nodes[nodeID]['lat'], osm.nodes[node]['lon'], osm.nodes[node]['lat'])
            if match and newDist > farthestDist and node != nodeID:
                farthestDist = newDist
                farthestNode = node
                farthestTag = match.group(1)
        print '\n Your starting node is http://www.openstreetmap.org/node/'+str(nodeID)
        print '\n Farthest Node for your query is http://www.openstreetmap.org/node/'+str(farthestNode)
        print '\n Farthest node\'s tagged info: '+str(farthestTag)
        graphNodes(osm.nodes[node]['lon'], osm.nodes[node]['lat'], osm.nodes[farthestNode]['lon'], osm.nodes[farthestNode]['lat'], nodeID, farthestNode, farthestTag)
    except:
        error_info()

def farthest_node(nodeID):
    farthestDist = 0
    try:
        for node in osm.nodes:
            newDist = distance_nodes(osm.nodes[nodeID]['lon'], osm.nodes[nodeID]['lat'], osm.nodes[node]['lon'], osm.nodes[node]['lat'])
            if newDist > farthestDist and node != nodeID:
                farthestDist = newDist
                farthestNode = node
        print '\n Your starting node is http://www.openstreetmap.org/node/'+str(nodeID)
        print '\n Farthest Node is http://www.openstreetmap.org/node/'+str(farthestNode)
        graphNodes(osm.nodes[node]['lon'], osm.nodes[node]['lat'], osm.nodes[farthestNode]['lon'], osm.nodes[farthestNode]['lat'], nodeID, farthestNode, 'no_tags')
    except:
        error_info()

def nearest_node(nodeID):
    # Start with arbitrarily large nearestDist and get smaller and smaller distance
    nearestDist = 100000000
    try:
        for node in osm.nodes:
            newDist = distance_nodes(osm.nodes[nodeID]['lon'], osm.nodes[nodeID]['lat'], osm.nodes[node]['lon'], osm.nodes[node]['lat'])
            if newDist < nearestDist and node != nodeID:
                nearestDist = newDist
                nearestNode = node
        print '\n Your starting node is http://www.openstreetmap.org/node/'+str(nodeID)
        print '\n Nearest Node is http://www.openstreetmap.org/node/'+str(nearestNode)
        graphNodes(osm.nodes[node]['lon'], osm.nodes[node]['lat'], osm.nodes[nearestNode]['lon'], osm.nodes[nearestNode]['lat'], nodeID, nearestNode, 'no_tags')
    except:
        error_info()

"""Plot the original node and the analyzed node, using networkx python graphical display"""
def graphNodes(X1, Y1, X2, Y2, nodeNumber1, nodeNumber2, nodeTag):
    G = nx.Graph()
    G.add_node(1,pos=(X1,Y1))
    G.add_node(2,pos=(X2,Y2))
    pos=nx.get_node_attributes(G,'pos')
    labels={}
    #Print out each node number on the graph
    labels[1]= 'YOUR STARTING POINT: Node number ', nodeNumber1
    #nodeTag must be a string
    if nodeTag != 'no_tags':
        labels[2] = 'Node number ' +str(nodeNumber2)+'\n Node tag '+str(nodeTag)
    else:
    	labels[2]= 'Node number '+str(nodeNumber2) +'\n No tags in this node operation'
    nx.draw_networkx_labels(G,pos,labels,font_size=11)
    nx.draw(G,pos)
    plt.show()        


"""Allow user to choose the function in command line
e.g. python nearest_node.py nearest_node_tagged 246512355 cafe"""
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('function')
    parser.add_argument('node_id')
    parser.add_argument('tag', nargs='?') 
    args = parser.parse_args()
    argsdict = vars(args)
    #If user input of node ID is not a digit, run geocoder function
    if not argsdict['node_id'].isdigit():
        node = geocode_node(argsdict['node_id'])
    else:
        node = int(argsdict['node_id'])
    #Take user entered node number and run one of the functions below
    if argsdict['function'] == 'nearest_node_tagged':   
        tag_value = get_tag_value(osm_dict, argsdict['tag'])
        nearest_node_tagged(node, tag_value)
    elif argsdict['function'] == 'farthest_node_tagged':   
        tag_value = get_tag_value(osm_dict, argsdict['tag'])
        farthest_node_tagged(node, tag_value)
    elif argsdict['function'] == 'nearest_node':
        nearest_node(node)
    elif argsdict['function'] == 'farthest_node':
        farthest_node(node)    
        
if __name__ == "__main__":
    main()
