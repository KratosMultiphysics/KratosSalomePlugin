#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

from base_application import Application

class GenericApplication(Application):
    def __init__(self):
        self.mesh_groups = []
        self.mesh_definitions = []

    def WriteCalculationFiles(self, path):
        pass


        mesh_description = {
            "203" : {
                "Element" : ["Element2D3N"],
                "Condition" : ["SurfaceCondition2D3N"]
            }
        }


    def Serialize(self):
        serialized_obj = {}
        serialized_obj["mesh_identifiers"] = [mg.mesh_identifier for mg in self.mesh_groups]


        return serialized_obj

    def Deserialize(self, serialized_obj):
        self.mesh_groups = [MeshGroup(m_id) for m_id in serialized_obj["mesh_identifiers"]]
