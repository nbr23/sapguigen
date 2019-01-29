from xml.parsers.expat import ParserCreate, ExpatError, errors
import xml.parsers.expat
from sapgui.saputils import SAPNode, SAPInstance, SAPRoot
import uuid
from collections import OrderedDict


class XMLElement:
    def __init__(self, tag=None, attributes=[], children=[]):
        self.tag = tag
        self.attributes = attributes
        self.children = children
        self.item_instance = None

    @classmethod
    def print_attributes(cls, attrs):
        if attrs:
            return ' '.join(map(lambda x: '{0}="{1}"'.format(x, attrs[x].replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>','&gt;')), attrs.keys()))
        return ''

    @classmethod
    def pretty_printer(cls, xml):
        s = ''
        if xml:
            if xml.children:
                s = '\n'.join(map(cls.pretty_printer, xml.children))
            if xml.tag:
                return '<{0} {1}>{2}</{0}>'.format(xml.tag,
                    cls.print_attributes(xml.attributes),
                    s)
        return s

    def __str__(self):
        return '<?xml version="1.0" encoding="utf-8"?>\n{0}'.format(self.pretty_printer(self))



class SAPXMLParser:
    def __init__(self):
        self.current = XMLElement(tag=None, attributes=[], children=[])
        self.parents = []
        self.sap_instances = None

    @classmethod
    def insert_customer(cls, root, customer, customer_name):
        cust_tree = customer_name.split('/')
        elt = None
        for folder in root.children:
            if folder.attributes['name'] == cust_tree[0] and folder.tag == 'Node':
                if len(cust_tree) > 1:
                    return cls.insert_customer(folder, customer, '/'.join(cust_tree[1:]))
                elt = folder
                break
        if not elt:
            elt = XMLElement(tag='Node',
                    attributes={'expanded': '1',
                        'name': cust_tree[0],
                        'uuid': str(uuid.uuid4())},
                    children=[])
            if len(cust_tree) > 1:
                root.children.append(elt)
                return cls.insert_customer(root, customer, customer_name)
        for entry in customer:
            child = XMLElement(tag='Item',
                    attributes={
                        'type': 'connection',
                        'uuid': str(uuid.uuid4())
                        },
                    children=[])
            child.item_instance = SAPInstance()
            for key,prop in entry.items():
                child.item_instance.__setattr__(key, ' - '.join(prop))
            child.attributes['name'] = child.item_instance.MSSysName
            child.item_instance.uuid = child.attributes['uuid']
            if child.item_instance.MSSrvPort is None:
                child.item_instance.MSSrvPort = 'sapms{0}'.format(child.item_instance.MSSysName)
            elt.children.append(child)
        root.children.append(elt)
        return 1

    def insert_customer_call(self, root, parent_name, customer, customer_name):
        if root.tag == parent_name:
            return self.insert_customer(root, customer, customer_name)
        else:
            for child in root.children:
                if self.insert_customer_call(child, parent_name, customer, customer_name):
                    return 1
        return 0


    def insert_nodes(self, root, parent_name, nodes):
        customers = {}
        categories = []
        for i,line in enumerate(nodes.split('\r\n')):
            elements = line.split('\t')
            if i == 0:
                for element in elements[1:]:
                    categories.append(element)
                continue
            if elements[0] not in customers:
                customers[elements[0]] = []
            inst = {}
            for j,element in enumerate(elements[1:]):
                if categories[j] not in inst:
                    inst[categories[j]] = []
                inst[categories[j]].append(element)
            customers[elements[0]].append(inst)

            #customers[elements[0]].append({
            #    'description': '{1} - {0}'.format(elements[1], elements[3]),
            #    'name': elements[3],
            #    'instance': elements[4],
            #    'ip': elements[5],
            #    'customer': elements[0]
            #    })
        for key, customer in customers.items():
            self.insert_customer_call(root, parent_name, customer, key)

    def parse_logon_tree(self, xmldata, instances):
        self.sap_instances = instances
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element
        parser.Parse(xmldata)
        return self.current

    def start_element(self, name, attrs):
        elt = XMLElement(tag=name, attributes=attrs, children=[])
        self.parents.append(self.current)
        self.current = elt
        if name == 'Item':
            for inst in self.sap_instances:
                if inst.Description == attrs['name']:
                    elt.item_instance = inst
                    break

    def end_element(self, name):
        parent = self.parents.pop()
        parent.children.append(self.current)
        self.current = parent

    @classmethod
    def get_instances(cls, root, instances):
        if root:
            if root.tag == 'Item':
                if root.item_instance:
                    instances.append(root.item_instance)
            else:
                for c in root.children:
                    cls.get_instances(c, instances)

    def get_workspaces(self, xml):
        s = ''
        if xml:
            if xml.children:
                s = '\n'.join(map(self.get_workspaces, xml.children))
            if xml.tag:
                if xml.tag in ['Favorites', 'Shortcuts', 'Connections', 'Nodes', 'SAPTREE']:
                    return s
                if xml.tag == 'Node':
                    attributes = 'uuid="{0}" name="{1}"' \
                            .format(str(uuid.uuid4()), xml.attributes['name'].replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>','&gt;'))
                else:
                    attributes = 'uuid="{0}" serviceid="{1}"'\
                            .format(str(uuid.uuid4()), xml.item_instance.uuid)
                return '<{0} {1} >{2}</{0}>'.format(xml.tag, attributes, s)
            return s



    def get_services(self, instances):
        if len(instances) <= 0:
            return ''
        s = ''
        for instance in instances:
            s = '{0}<Service type="SAPGUI" uuid="{1}" name="{2}" ' \
                'systemid="{3}" mode="1" server="{4}:32{5}" sncop="-1" ' \
                'sapcpg="1100" dcpg="2"/>\n' \
                .format(s, instance.uuid, instance.Description.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>','&gt;'),
                        instance.MSSysName, instance.Server,
                        instance.Database)

        return s

    def get_SAPUILandscape(self, xml, instances):
        return '<Landscape>\n<Workspaces>\n<Workspace name="Local" uuid="{0}' \
               '">{1}</Workspace></Workspaces>\n<Services>\n{2}' \
               '</Services>\n</Landscape>' \
               .format(str(uuid.uuid4()), self.get_workspaces(xml),
                       self.get_services(instances))


