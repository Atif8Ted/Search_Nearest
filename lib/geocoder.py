import logging 
log = logging.getLogger("pyosm")
import sys, filelocations
sys.path.append(filelocations.LIB_LOCATION)
import pyosm, re
osm = pyosm.OSMXMLFile(filelocations.OSM_DATA_LOCATION)

'''Geocodes a user entered address and returns a node for processing by osmpalnodesgraph.py
or by osmpalnodesbasic.py. Geocoder will match for query in the following priority: 1. house number and street name '''
'''2. zip code/postal code and city  3. Last option is matching for site name'''

class MatchNode(object):
    def __init__(self):
		pass
		
    def match_node(self, query, tag):
		self.match = re.search(query, tag)
		return self.match

#Functions below do not belong to the MatchNode class
def distance_nodes(x1,y1,x2,y2):
    return ((x2-x1)**2+(y2-y1)**2)**0.5

def match_house_number_and_street(queryString):
    for Nid in osm.nodes:
        tag = str(osm.nodes[Nid].tags).lower()
        matchHouseTag = MatchNode().match_node(('addr:housenumber'), tag)
        houseTagContents = MatchNode().match_node('addr:housenumber\': u\'(.*?)\'', tag)
        if houseTagContents:
            houseQuery = MatchNode().match_node(str(houseTagContents.group(1)).lower(), queryString)
            if matchHouseTag and houseTagContents and houseQuery:
                matchStreetTag = MatchNode().match_node(('addr:street'),tag)
                streetTagContents = MatchNode().match_node('addr:street\': u\'(.*?)\'', tag)
                if streetTagContents:
                    streetQuery = MatchNode().match_node(str(streetTagContents.group(1)).lower(), queryString.lower())
                    if matchStreetTag and streetTagContents and streetQuery:
                        return osm.nodes[Nid]['id']

def match_postcode_and_city(queryString):
    for Nid in osm.nodes:
        tag = str(osm.nodes[Nid].tags).lower()
        matchPostcodeTag = MatchNode().match_node(('addr:postcode'), tag)
        postcodeTagContents = MatchNode().match_node('addr:postcode\': u\'(.*?)\'', tag)
        if postcodeTagContents:
            postcodeQuery = MatchNode().match_node(str(postcodeTagContents.group(1)), queryString)
            if matchPostcodeTag and postcodeTagContents and postcodeQuery:
                matchCityTag = MatchNode().match_node(('addr:city'), tag)
                cityTagContents = MatchNode().match_node('addr:city\': u\'(.*?)\'', tag)
                if cityTagContents:
                    cityQuery = MatchNode().match_node(str(cityTagContents.group(1)).lower(), queryString.lower())
                    if matchCityTag and cityTagContents and cityQuery:
                        return osm.nodes[Nid]['id']

'''Finds a site name that is in any tag in .osm file and has more than one word, e.g. Union Squre'''
def match_site_name(queryString):
    for Nid in osm.nodes:
        matchSiteName = MatchNode().match_node((queryString.lower()),str(osm.nodes[Nid].tags).lower())
        if matchSiteName:
            return osm.nodes[Nid]['id']

'''Takes string input and returns node number '''
'''Geocoder will match for query in the following priority: 1. house number and street name '''
'''2. zip code/postal code and city  3. Last option is matching for site name'''
'''geocoder will only run if there is more than one word entered in the query. '''
def geocode_node(queryString):
    try:
        if ' ' in queryString:  #if query string has space then do geocoding
            node = match_house_number_and_street(queryString)
            if node is None:
                node = match_postcode_and_city(queryString)
                if node is None:
                    node = match_site_name(queryString)
        else:
        #just match one word against first result in .osm file
            for Nid in osm.nodes:
                match = MatchNode().match_node((queryString.lower()+'?'), str(osm.nodes[Nid].tags).lower())
                if match:
                    node = osm.nodes[Nid]['id']
        return node
    except:
        e = sys.exc_info()[0]
        l = sys.exc_traceback.tb_lineno
        print 'The following error ocurred: ', e, l
