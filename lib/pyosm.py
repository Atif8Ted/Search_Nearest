#!/usr/bin/python
import xml.sax
import numpy
import logging
log = logging.getLogger("pyosm")


#################### CLASSES
class Attributes(object):
    """
    common attributes for all object types
    """
    __slot__ = ['timestamp', 'uid', 'user', 'visible', 'version', 'changeset']

    def __init__(self, attrs):
        self.timestamp = attrs.get('timestamp','')
        self.version = attrs.get('version', '')
        self.changeset = attrs.get('changeset','')
        self.uid = attrs.get('uid','')
        self.user = attrs.get('user','')
        self.visible = attrs.get('visible','')

    def set_attr(self, name, value):
        if hasattr(self, name):
            setattr(self,name, value)
        else:
            raise KeyError

    def get(self, name, default=None):
        if hasattr(self, name):
            return getattr(self,name)
        else:
            return default

    def get_all(self):
        return {'timestamp': self.timestamp,
                'version': self.version,
                'changeset': self.changeset,
                'uid': self.uid,
                'user': self.user,
                'visible': self.visible}


class Node(object):
    __slot__ = ['id', 'lat', 'lon','__attrs', '__tags']

    def __init__(self, attrs, tags=None, load_tags=True, load_attrs=True):
        self.lon = 0.0
        self.lat = 0.0
        self.__attrs = None
        self.__tags = None

        self.id = int(attrs.pop('id'))
        if attrs.get('visible', '') != 'false':
            self.lon = float(attrs.pop('lon'))
            self.lat = float(attrs.pop('lat'))

        if load_attrs:
            self.__attrs = Attributes(attrs)

        if load_tags:
            self.__tags = tags

    def __getattr__(self, name):
        if name == 'tags':
            return self.__tags
        elif self.__attrs:
            return self.__attrs.get(name)

    def __getitem__(self, name):
        if name == 'lat':
            return self.lat
        elif name == 'lon':
            return self.lon
        elif name == 'tags':
            return self.__tags
        elif name == 'id':
            return self.id

    def __cmp__(self, other):
        cmp_ref = cmp(self.tags.get('ref',''), other.tags.get('ref',''))
        if cmp_ref:
            return cmp_ref
        cmp_name = cmp(self.tags.get('name',''), other.tags.get('name',''))
        if cmp_name:
            return cmp_name
        return cmp(self.id, other.id)

    def set_attr(self, name, value):
        self.__attrs.set_attr(name, value)

    def attributes(self):
        d = {'id': repr(self.id),
             'lat': repr(self.lat),
             'lon': repr(self.lon)}
        if self.__attrs:
            d.update(self.__attrs.get_all())
        return d

    def __repr__(self):
        return "Node(attrs=%r, tags=%r)" % (self.attributes(), self.__tags)


class Way(object):
    __slot__ = ['id', '__attrs','__tags','__nodes', 'osm_parent']

    def __init__(self, attrs, tags=None, nodes=None, osm_parent=None, load_tags=True, load_attrs=True, load_nodes=True):
        self.__nodes = None
        self.__attrs = None
        self.__tags = None

        self.id = int(attrs.pop('id'))
        self.osm_parent = osm_parent

        if load_nodes:
            self.__nodes = numpy.asarray(nodes, dtype='int64')
        if load_attrs:
            self.__attrs = Attributes(attrs)
        if load_tags:
            self.__tags = tags

    def __getattr__(self, name):
        if name == 'nodes':
            return self.osm_parent.get_nodes(self.__nodes)
        elif name == 'nodeids':
            return list(self.__nodes)
        elif name == 'tags':
            return self.__tags
        elif self.__attrs:
            return self.__attrs.get(name)

    def __getitem__(self, name):
        if name == 'id':
            return self.id
        elif name == '__nodes':
            return self.__nodes

    def __cmp__(self, other):
        cmp_ref = cmp(self.tags.get('ref',''), other.tags.get('ref',''))
        if cmp_ref:
            return cmp_ref
        cmp_name = cmp(self.tags.get('name',''), other.tags.get('name',''))
        if cmp_name:
            return cmp_name
        return cmp(self.id, other.id)

    def set_attr(self, name, value):
        self.__attrs.set_attr(name, value)

    def attributes(self):
        d = {'id': repr(self.id)}
        if self.__attrs:
            d.update(self.__attrs.get_all())
        return d

    def __repr__(self):
        return "Way(attrs=%r, tags=%r, nodes=%r)" % (self.attributes(), self.__tags, list(self.__nodes))


class Relation(object):
    __slot__ = ['id', '__attrs','__tags','__members', 'osm_parent']

    def __init__(self, attrs, tags=None, members=None, osm_parent=None, load_tags=True, load_attrs=True, load_members=True):
        self.__members = None
        self.__attrs = None
        self.__tags = None

        self.id = int(attrs.pop('id'))
        self.osm_parent = osm_parent

        if load_members:
            self.__members = numpy.array(members, dtype=[('type','|S1'),('id','<i8'),('role',numpy.object_)])
        if load_attrs:
            self.__attrs = Attributes(attrs)
        if load_tags:
            self.__tags = tags

    def __getattr__(self, name):
        if name == 'members':
            return self.osm_parent.get_members(self.__members)
        elif name == 'member_data':
            return list(self.__members)
        elif name == 'tags':
            return self.__tags
        elif self.__attrs:
            return self.__attrs.get(name)

    def __getitem__(self, name):
        if name == 'id':
            return self.id
        elif name == '__members':
            return self.__members
        elif name == '__tags':
            return self.__tags

    def __cmp__(self, other):
        cmp_ref = cmp(self.tags.get('ref',''), other.tags.get('ref',''))
        if cmp_ref:
            return cmp_ref
        cmp_name = cmp(self.tags.get('name',''), other.tags.get('name',''))
        if cmp_name:
            return cmp_name
        return cmp(self.id, other.id)

    def set_attr(self, name, value):
        self.__attrs.set_attr(name, value)

    def attributes(self):
        d = {'id': repr(self.id)}
        if self.__attrs:
            d.update(self.__attrs.get_all())
        return d

    def __repr__(self):
        if self.__members != None:
            members = [(a,b,c) for a,b,c in self.__members]
        else:
            members = None
        return "Relation(attrs=%r, tags=%r, members=%r)" % (self.attributes(), self.__tags, members)


class OSMXMLFile(object):
    def __init__(self, filename=None, content=None, options={}):
        self.filename = filename

        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.osmattrs = {'version':'0.6'}
        self.options = {'load_nodes': True,
                        'load_ways': True,
                        'load_relations': True,
                        'load_way_nodes': True,
                        'load_relation_members': True,
                        'filterfunc': False}
        self.options.update(options)
        if filename:
            self.__parse()
        elif content:
            self.__parse(content)

    def get_members(self, members):
        mlist = []
        for mtype, mid, mrole in members:
            if mtype == 'r':
                obj = self.relations[mid]
            elif mtype == 'w':
                obj = self.ways[mid]
            else:
                obj = self.nodes[mid]
            mlist.append((obj, mrole))
        return mlist

    def get_nodes(self, nodes):
        return [ self.nodes[nid] for nid in nodes ]

    def __parse(self, content=None):
        """Parse the given XML file"""
        handler = OSMXMLFileParser(self)
        if content:
            xml.sax.parseString(content, handler)
        else:
            xml.sax.parse(self.filename, handler)

    def merge(self, osmxmlfile, update=True):
        self.nodes.update(osmxmlfile.nodes)
        for id, way in osmxmlfile.ways.items():
            way.osm_parent = self
            self.ways[id] = way
        for id, relation in osmxmlfile.relations.items():
            relation.osm_parent = self
            self.relations[id] = relation

    @staticmethod
    def write_tags(handler, tags):
        for name, value in tags.items():
            handler.characters('  ')
            handler.startElement('tag', {'k': name, 'v': value})
            handler.endElement('tag')
            handler.characters('\n')

    def write(self, fileobj):
        if type(fileobj) == str:
            fileobj = open(fileobj, 'wt')
        handler = xml.sax.saxutils.XMLGenerator(fileobj, 'UTF-8')
        handler.startDocument()
        handler.startElement('osm', self.osmattrs)
        handler.characters('\n')

        for id, node in sorted(self.nodes.items()):
            handler.startElement('node', node.attributes())
            self.write_tags(handler, node.tags)
            handler.endElement('node')
            handler.characters('\n')

        for id, way in sorted(self.ways.items()):
            handler.startElement('way', way.attributes())
            handler.characters('\n')
            for node in way.nodes:
                handler.characters('  ')
                handler.startElement('nd', {'ref': str(node.id)})
                handler.endElement('nd')
                handler.characters('\n')
            self.write_tags(handler, way.tags)
            handler.endElement('way')
            handler.characters('\n')

        for relationid in sorted(self.relations):
            relation = self.relations[relationid]
            handler.startElement('relation', relation.attributes())
            for mtype, mid, mrole in relation.member_data:
                obj_type = {'n': 'node', 'w': 'way', 'r': 'relation'}[mtype]
                handler.characters('  ')
                handler.startElement('member', {'type': obj_type, 'ref': str(mid), 'role': mrole})
                handler.endElement('member')
                handler.characters('\n')
            self.write_tags(handler, relation.tags)
            handler.endElement('relation')
            handler.characters('\n')

        handler.endElement('osm')
        handler.endDocument()

    def statistic(self):
        """Print a short statistic about the osm object"""
        print("Filename: %s" % self.filename)
        print("  Nodes    : %i" % len(self.nodes))
        print("  Ways     : %i" % len(self.ways))
        print("  Relations: %i" % len(self.relations))


class OSMXMLFileParser(xml.sax.ContentHandler):
    def __init__(self, containing_obj):
        self.containing_obj = containing_obj
        for key in 'load_nodes load_ways load_relations load_way_nodes load_relation_members filterfunc'.split():
            setattr(self, key, containing_obj.options[key])

        self.obj_attrs = None
        self.obj_tags = []
        self.way_nodes = []
        self.rel_members = []
        self.osm_attrs = None

    def startElement(self, name, attrs):
        dictnames = 'node way relation'.split()
        if name in dictnames:
            self.obj_attrs = dict(attrs)

        elif name == 'tag':
            self.obj_tags.append((attrs['k'], attrs['v']))

        elif name == "nd":
            self.way_nodes.append(attrs['ref'])

        elif name == "member":
            self.rel_members.append((attrs['type'][0],attrs['ref'],attrs['role']))

        elif name == "osm":
            self.osm_attrs = dict(attrs)

        elif name == "bound":
            pass

        else:
            log.warn("Don't know element %s", name)

    def endElement(self, name):
        if name == "node":
            if self.load_nodes:
                curr_node = Node(self.obj_attrs, dict(self.obj_tags))
                if self.filterfunc:
                    if self.filterfunc(curr_node):
                        self.containing_obj.nodes[curr_node.id] = curr_node
                else:
                    self.containing_obj.nodes[curr_node.id] = curr_node
            self.obj_attrs = None
            self.obj_tags = []

        elif name == "way":
            if self.load_ways:
                curr_way = Way(self.obj_attrs, dict(self.obj_tags), self.way_nodes,
                               osm_parent=self.containing_obj, load_nodes=self.load_way_nodes)
                if self.filterfunc:
                    if self.filterfunc(curr_way):
                        self.containing_obj.ways[curr_way.id] = curr_way
                else:
                    self.containing_obj.ways[curr_way.id] = curr_way
            self.obj_attrs = None
            self.obj_tags = []
            self.way_nodes = []

        elif name == "relation":
            if self.load_relations:
                curr_rel = Relation(self.obj_attrs, dict(self.obj_tags), self.rel_members,
                                    osm_parent=self.containing_obj, load_members=self.load_relation_members)
                if self.filterfunc:
                    if self.filterfunc(curr_rel):
                        self.containing_obj.relations[curr_rel.id] = curr_rel
                else:
                    self.containing_obj.relations[curr_rel.id] = curr_rel
            self.obj_attrs = None
            self.obj_tags = []
            self.rel_members = []

        elif name == "osm":
            self.containing_obj.osmattrs = self.osm_attrs
            self.curr_osmtags = None


#################### FUNCTIONS


#################### MAIN
if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    for filename in sys.argv[1:]:
        osm = OSMXMLFile(filename)
        osm.statistic()
