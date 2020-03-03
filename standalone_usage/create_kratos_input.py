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
import os, sys
import logging

# adding the plugin-path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "plugin")))

# logging
from plugin_logging import InitializeLogging
InitializeLogging(log_file_path=os.getcwd()) # log in the current directory

logger = logging.getLogger(__name__)
logger.debug('loading module')

# plugin imports
from model_part import ModelPart
import geometries_io
from utilities import salome_utilities
from mesh_interface import MeshInterface
from write_mdpa import WriteMdpa

# salome imports
import salome


class SalomeMesh(geometries_io.Mesh):
    def __init__(self, salome_mesh, mesh_description, model_part_name=""):

        if salome_utilities.IsMesh(salome_mesh) or salome_utilities.IsSubMesh(salome_mesh) or salome_utilities.IsMeshGroup(salome_mesh):
            mesh_identifier = salome_utilities.GetSalomeID(salome_mesh)
        elif isinstance(salome_mesh, salome.smesh.smeshBuilder.Mesh):
            mesh_identifier = salome_utilities.GetSalomeID(salome_mesh.GetMesh())
        else:
            raise Exception("Unrecognized")

        mesh_interface = MeshInterface(mesh_identifier)

        super().__init__(mesh_interface, mesh_description, model_part_name)


def CreateModelPart(meshes):
    logger.debug('Calling "CreateModelPart"')
    model_part = ModelPart()
    geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

    return model_part


def CreateMdpaFile(meshes, mdpa_file_name):
    logger.debug('Calling "CreateMdpaFile"')
    model_part = CreateModelPart(meshes)
    WriteMdpa(model_part, mdpa_file_name)
