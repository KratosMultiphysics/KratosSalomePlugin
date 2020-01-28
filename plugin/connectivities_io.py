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

    def AddMesh(self, mesh_group, mesh_description):
        # mesh_description = {
        #     "name" : "xxx"
        #     "add_sub_model_part" : True,
        #     "entity_creation" : {
        #         "102" : {
        #             "Elements"   : ["Element1", "ElementXYZ"],
        #             "Conditions" : ["BaseCondition", "ConditionXYZ"],
        #         },
        #         "308" : {
        #             "Elements"  : ["VolumeElement"]
        #         }
        #     }
        # }

        ALTERNATIVE:

        """ Example for the format of the "mesh_dict":
        "mesh_dict" : {
            "elements" : {
                "nodes" : {
                    "PointLoadCondition3D1N" : 0
                }
                203 : {
                    "SmallDisplacementElement2D3N" : 0
                },
                204 : {
                    "SmallDisplacementElement2D4N" : 0
                }
            "conditions" : {
                102 : {
                    "LineCondition" : 0
                }
            }
        }
        """

        if mesh_description["add_sub_model_part"]:
            model_part_to_add_to = self.model_part.CreateSubModelPart(mesh_description["name"])
        else:
            model_part_to_add_to = self.model_part

        use_geom_entities = False
        if "entity_creation" in mesh_description:
            entity_creation_keys = mesh_description["entity_creation"].keys()
            if len(entity_creation_keys) > 1 or (len(entity_creation_keys) == 1 and entity_creation_keys[0] != "nodes"):
                use_geom_entities = True

        nodes, geom_entities = mesh_group.GetNodesAndGeometricalEntities(mesh_description["entity_creation"].keys())

        # Note: NOT checking the coordinates here since this is done in the ModelPart
        for node_id, node_coords in nodes.items():
            model_part_to_add_to.CreateNewNode(node_id, node_coords[0], node_coords[1], node_coords[2])


