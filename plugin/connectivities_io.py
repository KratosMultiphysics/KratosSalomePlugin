#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

class ConnectivitiesIO(object):
    def __init__(self, model_part):
        self.model_part = model_part

    def AddMesh(self, mesh_name, mesh_interface, mesh_description):
        """ Example for the format of the "mesh_description":
        "mesh_dict" : {
            "add_sub_model_part" : True
            "elements" : {
                "nodes" : ["PointLoadCondition3D1N", "PointMomentCondition"]
                "203" : ["SmallDisplacementElement2D3N"]# I think keys have to be sth different ...
                "204" : ["SmallDisplacementElement2D4N"]
            "conditions" : {
                "102" : ["LineCondition"]
            }
        }
        """
        # TODO how to handle the overwritting?

        # TODO add defaults

        if mesh_description["add_sub_model_part"]:
            model_part_to_add_to = self.model_part.CreateSubModelPart(mesh_name)# this enforces the names to be unique
        else:
            model_part_to_add_to = self.model_part

        unique_keys = set(list(mesh_description["elements"].keys()) + list(mesh_description["conditions"]).keys())
        nodes, geom_entities = mesh_interface.GetNodesAndGeometricalEntities(unique_keys)

        # Note: NOT checking the coordinates here since this is done in the ModelPart
        for node_id, node_coords in nodes.items(): # todo sort this? otherwise order will be random => will probably have an impact on performance, hence do I need it? Anyway we have no control since it comes from the preprocessor...
            model_part_to_add_to.CreateNewNode(node_id, node_coords[0], node_coords[1], node_coords[2])

        if len(mesh_description["elements"] > 0):
            self.__AddElements(model_part_to_add_to, geom_entities, mesh_description["elements"])
        if len(mesh_description["conditions"] > 0):
            self.__AddConditions(model_part_to_add_to, geom_entities, mesh_description["conditions"])


    def __AddElements(model_part_to_add_to, geom_entities, entity_creation):
        pass

    def __AddConditions(model_part_to_add_to, geom_entities, entity_creation):
        pass