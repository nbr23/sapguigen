import re

class SAPRoot:
    def __init__(self):
        self.children = []
        self.nodes = []
        self.uuid = ''
        self.category = None
        self.expanded = '0'

class SAPNode:
    def __init__(self):
        self.label = ""
        self.node_type = ""
        self.children = []
        self.nodes = []
        self.uuid = ''
        self.category = None
        self.expanded = '0'

class SAPInstance:
    def __init__(self):
        self.SncName = ""
        self.Description = ""
        self.Address = ""
        self.CodepageIndex = ""
        self.Router2 = ""
        self.EntryKey = ""
        self.Database = ""
        self.Utf8Off = ""
        self.MSSrvName = ""
        self.RouterChoice = ""
        self.SncChoice = ""
        self.SessManKey = ""
        self.System = 3
        self.SncNoSSO = ""
        self.ShortcutType = 0
        self.MSLast = ""
        self.ShortcutString = ""
        self.Server = ""
        self.Codepage = ""
        self.MSSysName = None
        self.ShortcutBy = ""
        self.Configuration = ""
        self.MSSrvPort = None
        self.LowSpeedConnection = ""
        self.EncodingID = ""
        self.Origin = ""
        self.Router = ""
        self.ShortcutTo = ""
        self.uuid = ''
        self.category = ''
        self.Hostname = ''



class SAPUtils:

    @classmethod
    def add_instances(cls, root, instances):
        return root

#    @classmethod
#    def parseCat(cls, inifile):
#        cat_reg = re.compile("^\[(.*)\]$")
#        cat = []
#        for line in inifile.readlines():
#            catmatch = cat_reg.match(line)
#            if catmatch:
#                cat.append(catmatch.group(1))
#        return cat

    @classmethod
    def pretty_print_ini(cls, data):
        if len(data) <=0:
            return ''
        s = ''
        for key in data[0].__dict__:
            s = '{0}[{1}]\n'.format(s, key)
            i = 1
            for elt in data:
                s = '{0}Item{1}={2}\n'.format(s, i, elt.__getattribute__(key))
                i += 1
        return s

    @classmethod
    def create_sap_instances(cls, serv_dict):
        servers = []
        for server in serv_dict:
            instance = SAPInstance()
            for field in serv_dict[server]:
                if field in instance.__dict__:
                    instance.__setattr__(field, serv_dict[server][field])
            servers.append(instance)
        return servers

    @classmethod
    def parse_ini(cls, inifile):
        item_reg = re.compile("^Item([0-9]+)=(.*)")
        cat_reg = re.compile("^\[(.*)\]$")
        cat = ""
        itemno = 0
        dataarray = {}
        for line in inifile.split('\r\n'):
            catmatch = cat_reg.match(line)
            itemmatch = item_reg.match(line)
            if catmatch:
                cat = catmatch.group(1)
            elif itemmatch:
                itemno = int(itemmatch.group(1))
                if not itemno in dataarray.keys():
                    dataarray[itemno] = {}
                dataarray[itemno][cat] = itemmatch.group(2)
        return dataarray

    @classmethod
    def host_file(cls, instances):
        s = ''
        for instance in instances:
            if instance.Hostname and instance.Server:
                s = ''.format(s, instance.Server, instance.Hostname)
        return s

