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
import logging
logger = logging.getLogger(__name__)
logger.debug('loading module')

class Mesh(object):
    def __init__(self, model_part_name, mesh_interface, mesh_description):
        self.model_part_name = model_part_name
        self.mesh_interface = mesh_interface
        self.mesh_description = mesh_description

    def __str__(self):
        string_buf  = "Mesh\n"
        string_buf += "  ModelPart name: {}\n".format(self.model_part_name)
        string_buf += "  MeshInterface : {}\n".format(self.mesh_interface.PrintData("  "))
        string_buf += "  Mesh description: {}\n".format(self.mesh_description)
        return string_buf


class GeometriesIO(object):
    @staticmethod
    def AddMeshes(model_part, meshes):
        if model_part.GetRootModelPart().NumberOfNodes() != 0:
            err_msg  = 'The Root-ModelPart "{}" is not empty!\n'.format(model_part.GetRootModelPart().Name)
            err_msg += 'This is required because otherwise the numbering of entities can get messed up'
            raise RuntimeError(err_msg)

        for mesh in meshes:
            print(mesh)
            # 1. Get ModelPart to add the entities to
            # 2. Get Properties => See "read_materials_utility.cpp" function "AssignPropertyBlock"



    def __init__(self, model_part):
        self.model_part = model_part
        if self.model_part.GetRootModelPart().NumberOfNodes() != 0:
            # if nodes already exist then the numbering might get screwed up!
            raise RuntimeError("The Root-ModelPart has to be empty!")

    def AddMesh(self, mesh_name, mesh_interface, mesh_description):
        """ Example for the format of the "mesh_description":
        {
            "add_sub_model_part" : True

            "elements" : {
                "0D"         : { "PointLoadCondition3D1N"   : 0,
                                 "PointMomentCondition3D1N" : 1
                               }
                "Triangle"   : [["SmallDisplacementElement2D3N", 0]]
                "Quadrangle" : [["SmallDisplacementElement2D4N", 0]]

            "conditions" : {
                "Line" : [["LineCondition", 0]]
            }
        }
        """

        default_mesh_description = {
            "add_sub_model_part" : True,
            "elements" : { },
            "conditions" : { }
        }

        for k,v in default_mesh_description.items():
            if k not in mesh_description:
                mesh_description[k] = v


        # TODO how to handle the overwritting?

        if mesh_description["add_sub_model_part"]:
            model_part_to_add_to = self.model_part.CreateSubModelPart(mesh_name) # this enforces the names to be unique
        else:
            model_part_to_add_to = self.model_part

        unique_keys = list(set(list(mesh_description["elements"].keys()) + list(mesh_description["conditions"].keys())))
        nodes, geom_entities = mesh_interface.GetNodesAndGeometricalEntities(unique_keys)

        self.__AddNodes(model_part_to_add_to, nodes)

        if len(mesh_description["elements"]) > 0:
            self.__AddElements(model_part_to_add_to, geom_entities, mesh_description["elements"])
        if len(mesh_description["conditions"]) > 0:
            self.__AddConditions(model_part_to_add_to, geom_entities, mesh_description["conditions"])

    @staticmethod
    def __AddNodes(model_part_to_add_to, new_nodes):
        # Note: NOT checking the coordinates here since this is done in the ModelPart
        for node_id, node_coords in new_nodes.items():
            model_part_to_add_to.CreateNewNode(node_id, node_coords[0], node_coords[1], node_coords[2])

    def __AddElements(self, model_part_to_add_to, geom_entities, entity_creation):
        counter = 0
        for entity_type, entities_dict in entity_creation.items():
            print(entity_type, entities_dict)
            for entities_name, props_id in entities_dict.items():
                print(entities_name, props_id)
                props = model_part_to_add_to.GetRootModelPart().GetProperties(props_id)
                for geom_entity_id, geom_entity_connectivities in geom_entities[entity_type].items():
                    print(geom_entity_id, geom_entity_connectivities)
                    counter += 1
                    model_part_to_add_to.CreateNewElement(entities_name, counter, geom_entity_connectivities, props)

    def __AddConditions(self, model_part_to_add_to, geom_entities, entity_creation):
        pass