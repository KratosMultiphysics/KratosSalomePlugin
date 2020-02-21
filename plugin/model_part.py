#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# python imports
from collections import OrderedDict
import logging
logger = logging.getLogger(__name__)
logger.debug('loading module')


class DataValueContainer(object):
    def __init__(self):
        self.__var_data = {}

    def Has(self, var):
        return (var in self.__var_data)

    def GetValue(self, var):
        if not var in self.__var_data:
            raise KeyError('Variable "{}" not found!'.format(var))
        return self.__var_data[var]

    def SetValue(self, var, value):
        self.__var_data[var] = value

    def HasData(self):
        return (len(self.__var_data) > 0)

    def GetData(self):
        return self.__var_data

    def PrintInfo(self, prefix_string=""):
        return prefix_string + "DataValueContainer\n"

    def PrintData(self, prefix_string=""):
        string_buf = ""
        for key in sorted(self.__var_data): # sorting to make reading and testing easier
            val = self.__var_data[key]
            string_buf += "{}  {} : {}\n".format(prefix_string, key, val)
        return string_buf

    def __str__(self):
        string_buf = self.PrintInfo()
        string_buf += self.PrintData()
        return string_buf


class Node(DataValueContainer):
    def __init__(self, Id, X, Y, Z):
        super().__init__()
        self.Id = Id
        self.X = X
        self.Y = Y
        self.Z = Z

    def Coordinates(self):
        return [self.X, self.Y, self.Z]

    def PrintInfo(self, prefix_string=""):
        return prefix_string + "Node #{}\n".format(self.Id)

    def PrintData(self, prefix_string=""):
        string_buf = "{}  Coordinates: [{}, {}, {}]\n".format(prefix_string, *(self.Coordinates()))
        if self.HasData():
            string_buf += "{}  Nodal Data:\n".format(prefix_string)
            string_buf += super().PrintData(prefix_string+"  ")
        return string_buf


class GeometricalObject(DataValueContainer):
    def __init__(self, Id, Nodes, Name, Properties):
        super().__init__()
        self.Id = Id
        self.__nodes = Nodes
        self.name = Name
        self.properties = Properties

    def GetNodes(self):
        return self.__nodes

    def __str__(self):
        string_buf  = "GeometricalObject #{}\n".format(self.Id)
        string_buf += "  Name: {}\n".format(self.name)
        string_buf += "  Nodes:\n"
        for node in self.__nodes:
            string_buf += node.PrintInfo("    ")
            string_buf += node.PrintData("    ")
        string_buf += "  Properties:\n"
        string_buf +=  self.properties.PrintInfo("    ")
        string_buf +=  self.properties.PrintData("    ")
        if self.HasData():
            string_buf += "  GeometricalObject Data:\n"
            string_buf += self.PrintData("  ")
        return string_buf


class Properties(DataValueContainer):
    def __init__(self, Id):
        super().__init__()
        self.Id = Id

    def PrintInfo(self, prefix_string=""):
        return prefix_string + "Properties #{}\n".format(self.Id)


class ModelPart(DataValueContainer):

    class PointerVectorSet(OrderedDict):
        def __iter__(self):
            self.vals_list = iter(list(self.values()))
            return self

        def __next__(self):
            return next(self.vals_list)

        def __str__(self):
            string_buf = "PointerVectorSet:\n"
            for k,v in self.items():
                string_buf += "  {} : {}\n".format(k, v)
            return string_buf


    def __init__(self, name="default"):
        super().__init__()
        self.__parent_model_part = None
        self.__sub_model_parts   = ModelPart.PointerVectorSet()
        self.__nodes             = ModelPart.PointerVectorSet()
        self.__elements          = ModelPart.PointerVectorSet()
        self.__conditions        = ModelPart.PointerVectorSet()
        self.__properties        = ModelPart.PointerVectorSet()

        if("." in name):
            RuntimeError("Name of the modelpart cannot contain a . (dot) Please rename ! ")
        if(name == ""):
            RuntimeError("No empty names for modelpart are allowed. Please rename ! ")

        self.Name = name

    def FullName(self):
        full_name = self.Name
        if self.IsSubModelPart():
            full_name = self.GetParentModelPart().FullName() + "." + full_name
        return full_name

    ### Methods related to SubModelParts ###
    @property
    def SubModelParts(self):
        return self.__sub_model_parts

    def NumberOfSubModelParts(self):
        return len(self.__sub_model_parts)

    def CreateSubModelPart(self, name_smp):
        if name_smp in self.__sub_model_parts:
            raise RuntimeError('There is an already existing sub model part with name "{}" in model part: "{}"'.format(name_smp, self.Name))
        smp = ModelPart(name_smp)
        smp.__parent_model_part = self

        self.__sub_model_parts[name_smp] = smp
        return smp

    def HasSubModelPart(self, name_smp):
        return name_smp in self.__sub_model_parts

    def GetSubModelPart(self, smp_name):
        try:
            return self.__sub_model_parts[smp_name]
        except KeyError:
            raise RuntimeError('SubModelPart "{}" not found'.format(smp_name))

    def IsSubModelPart(self):
        return self.__parent_model_part is not None

    def GetParentModelPart(self):
        if self.IsSubModelPart():
            return self.__parent_model_part
        else:
            return self

    def GetRootModelPart(self):
        if self.IsSubModelPart():
            return self.__parent_model_part.GetRootModelPart()
        else:
            return self


    ### Methods related to Nodes ###
    @property
    def Nodes(self):
        return self.__nodes

    def NumberOfNodes(self):
        return len(self.__nodes)

    def GetNode(self, node_id):
        try:
            return self.__nodes[node_id]
        except KeyError:
            raise RuntimeError('Node index not found: {}'.format(node_id))

    def CreateNewNode(self, node_id, coord_x, coord_y, coord_z):
        if self.IsSubModelPart():
            new_node = self.__parent_model_part.CreateNewNode(node_id, coord_x, coord_y, coord_z)
            self.__nodes[node_id] = new_node
            return new_node
        else:
            existing_node = self.__nodes.get(node_id)
            if existing_node:
                if self.__Distance(existing_node.Coordinates(), [coord_x, coord_y, coord_z]) > 1E-15:
                    err_msg  = 'A node with Id #' + str(node_id) + ' already exists in the root model part with different Coordinates!'
                    err_msg += '\nExisting Coords: ' + str(existing_node.Coordinates())
                    err_msg += '\nNew Coords: '      + str([coord_x, coord_y, coord_z])
                    raise RuntimeError(err_msg)

                return existing_node
            else:
                new_node = Node(node_id, coord_x, coord_y, coord_z)
                self.__nodes[node_id] = new_node
                return new_node


    ### Methods related to Elements ###
    @property
    def Elements(self):
        return self.__elements

    def NumberOfElements(self):
        return len(self.__elements)

    def GetElement(self, element_id):
        try:
            return self.__elements[element_id]
        except KeyError:
            raise RuntimeError('Element index not found: {}'.format(element_id))

    def CreateNewElement(self, element_name, element_id, node_ids, properties):
        if self.IsSubModelPart():
            new_element = self.__parent_model_part.CreateNewElement(element_name, element_id, node_ids, properties)
            self.__elements[element_id] = new_element
            return new_element
        else:
            if element_id in self.__elements:
                raise RuntimeError('trying to construct an element with ID {} however an element with the same Id already exists'.format(element_id))

            element_nodes = [self.GetNode(node_id) for node_id in node_ids]
            new_element = GeometricalObject(element_id, element_nodes, element_name, properties)
            self.__elements[element_id] = new_element
            return new_element


    ### Methods related to Conditions ###
    @property
    def Conditions(self):
        return self.__conditions

    def NumberOfConditions(self):
        return len(self.__conditions)

    def GetCondition(self, condition_id):
        try:
            return self.__conditions[condition_id]
        except KeyError:
            raise RuntimeError('Condition index not found: {}'.format(condition_id))

    def CreateNewCondition(self, condition_name, condition_id, node_ids, properties):
        if self.IsSubModelPart():
            new_condition = self.__parent_model_part.CreateNewCondition(condition_name, condition_id, node_ids, properties)
            self.__conditions[condition_id] = new_condition
            return new_condition
        else:
            if condition_id in self.__conditions:
                raise RuntimeError('trying to construct a condition with ID {} however a condition with the same Id already exists'.format(condition_id))

            condition_nodes = [self.GetNode(node_id) for node_id in node_ids]
            new_condition = GeometricalObject(condition_id, condition_nodes, condition_name, properties)
            self.__conditions[condition_id] = new_condition
            return new_condition


    ### Methods related to Properties ###
    @property
    def Properties(self):
        return self.__properties

    def NumberOfProperties(self):
        return len(self.__properties)

    def HasProperties(self, properties_id):
        return properties_id in self.__properties

    def RecursivelyHasProperties(self, properties_id):
        if self.HasProperties(properties_id):
            return True
        else:
            if self.IsSubModelPart():
                return self.__parent_model_part.RecursivelyHasProperties(properties_id)
            else:
                return False

    def GetProperties(self, properties_id, mesh_id=0):
        # mesh_id is for compatibility with Kratos
        if self.HasProperties(properties_id):
            return self.__properties[properties_id]
        else:
            if self.IsSubModelPart():
                # check if properties exist in parent
                # if so, then add it also to this ModelPart
                props = self.__parent_model_part.GetProperties(properties_id)
                self.__properties[properties_id] = props
                return props
            else:
                raise RuntimeError('Properties index not found: {}'.format(properties_id))

    def CreateNewProperties(self, properties_id):
        if self.IsSubModelPart():
            new_properties = self.__parent_model_part.CreateNewProperties(properties_id)
            self.__properties[properties_id] = new_properties
            return new_properties
        else:
            if properties_id in self.__properties:
                raise Exception("Property #{} already existing".format(properties_id))
            new_properties = Properties(properties_id)
            self.__properties[properties_id] = new_properties
            return new_properties


    def PrintInfo(self, prefix_string=""):
        return prefix_string + 'ModelPart "{}"\n'.format(self.Name)

    def PrintData(self, prefix_string=""):
        string_buf = ""
        if self.HasData():
            string_buf += "{}  ModelPart Data:\n".format(prefix_string)
            string_buf += super().PrintData(prefix_string+"  ")
        string_buf  += "{}  Number of Nodes: {}\n".format(prefix_string, self.NumberOfNodes())
        string_buf += "{}  Number of Elements: {}\n".format(prefix_string, self.NumberOfElements())
        string_buf += "{}  Number of Conditions: {}\n".format(prefix_string, self.NumberOfConditions())
        string_buf += "{}  Number of Properties: {}\n".format(prefix_string, self.NumberOfProperties())

        string_buf += "{}  Number of SubModelparts: {}\n".format(prefix_string, self.NumberOfSubModelParts())
        for smp in self.__sub_model_parts:
            string_buf += smp.PrintInfo(prefix_string+"    ")
            string_buf += smp.PrintData(prefix_string+"    ")
        return string_buf


    ### Auxiliar Methods ###
    @classmethod
    def __Distance(cls, coords_1, coords_2):
        return ((coords_1[0]-coords_2[0])**2 +
                (coords_1[1]-coords_2[1])**2 +
                (coords_1[2]-coords_2[2])**2 )**0.5
