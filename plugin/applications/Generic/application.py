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
from mesh_group import MeshGroup
from write_model_part import WriteModelPart

class GenericApplication(Application):
    def __init__(self):
        self.mesh_groups = {} # mesh-identifier - MeshGroup
        self.mesh_descriptions = {} # mesh-name - tuple (MeshGroup - mesh-description)


    def WriteCalculationFiles(self, path):
        WriteModelPart(self.mesh_descriptions, path)


    def Serialize(self):
        serialized_obj = {}
        serialized_obj["mesh_identifiers"] = list(self.mesh_groups.keys())
        serialized_obj["mesh_descriptions"] = {mesh_name : [mesh_descr[0].mesh_identifier, mesh_descr[1]] for mesh_name, mesh_descr in self.mesh_descriptions.items()}

        return serialized_obj

    def Deserialize(self, serialized_obj):
        self.mesh_groups = {m_id : MeshGroup(m_id) for m_id in serialized_obj["mesh_identifiers"]}
        self.mesh_descriptions = {mesh_name : (self.mesh_groups[mesh_descr[0]], mesh_descr[1]) for mesh_name, mesh_descr in serialized_obj["mesh_descriptions"].items()}
