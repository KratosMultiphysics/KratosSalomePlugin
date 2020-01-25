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

class ModelPart(object):

    def __init__(self, name="default"):
        self.__parent_model_part = None
        self.__sub_model_parts   = OrderedDict()
        self.__nodes             = OrderedDict()
        self.__elements          = OrderedDict()
        self.__conditions        = OrderedDict()

        if("." in name):
            RuntimeError("Name of the modelpart cannot contain a . (dot) Please rename ! ")
        if(name == ""):
            RuntimeError("No empty names for modelpart are allowed. Please rename ! ")

        self.Name = name

    ### Methods related to SubModelParts ###
    @property
    def SubModelParts(self):
        return self.__sub_model_parts.values()

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


    ### Methods related to Nodes ###
    @property
    def Nodes(self):
        return self.__nodes.values()

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
                new_node = Node(node_id, coord_x, coord_y, coord_z, self.__hist_variables, self.__buffer_size)
                self.__nodes[node_id] = new_node
                return new_node


    ### Methods related to Elements ###
    @property
    def Elements(self):
        return self.__elements.values()

    def NumberOfElements(self):
        return len(self.__elements)

    def GetElement(self, element_id):
        try:
            return self.__elements[element_id]
        except KeyError:
            raise RuntimeError('Element index not found: {}'.format(element_id))

    def CreateNewElement(self, element_name, element_id, node_ids, property_id):
        if self.IsSubModelPart():
            new_element = self.__parent_model_part.CreateNewElement(element_name, element_id, node_ids, property_id)
            self.__elements[element_id] = new_element
            self.AddElement(new_element)
            return new_element
        else:
            element_nodes = [self.GetNode(node_id) for node_id in node_ids]
            new_element = Element(element_id, element_nodes)
            if element_id in self.__elements:
                existing_element = self.__elements[element_id]
                if existing_element != new_element:
                    raise RuntimeError('A different element with the same Id exists already!') # TODO check what Kratos does here

                return existing_element
            else:
                self.__elements[element_id] = new_element
                return new_element


    ### Methods related to Conditions ###
    @property
    def Conditions(self):
        return self.__conditions.values()

    def NumberOfConditions(self):
        return len(self.__conditions)

    def GetCondition(self, condition_id):
        try:
            return self.__conditions[condition_id]
        except KeyError:
            raise RuntimeError('Condition index not found: {}'.format(condition_id))

    def CreateNewCondition(self, condition_name, condition_id, node_ids, property_id):
        if self.IsSubModelPart():
            new_condition = self.__parent_model_part.CreateNewCondition(condition_name, condition_id, node_ids, property_id)
            self.__conditions[condition_id] = new_condition
            self.AddCondition(new_condition)
            return new_condition
        else:
            condition_nodes = [self.GetNode(node_id) for node_id in node_ids]
            new_condition = Condition(condition_id, condition_nodes)
            if condition_id in self.__conditions:
                existing_condition = self.__conditions[condition_id]
                if existing_condition != new_condition:
                    raise RuntimeError('A different condition with the same Id exists already!') # TODO check what Kratos does here

                return existing_condition
            else:
                self.__conditions[condition_id] = new_condition
                return new_condition
