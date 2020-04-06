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
import os
import logging

# logging
from ks_plugin.plugin_logging import InitializeLogging
InitializeLogging(log_file_path=os.getcwd()) # log in the current working directory

logger = logging.getLogger(__name__)
logger.debug('loading module')

# plugin imports
from ks_plugin.model_part import ModelPart
from ks_plugin import geometries_io
from ks_plugin.utilities import salome_utilities
from ks_plugin.mesh_interface import MeshInterface
from ks_plugin.write_mdpa import WriteMdpa


class SalomeMesh(geometries_io.Mesh):
    def __init__(self, salome_mesh, mesh_description, model_part_name=""):

        if isinstance(salome_mesh, str):
            mesh_identifier = salome_mesh
        elif any([salome_utilities.IsMeshProxy(salome_mesh), salome_utilities.IsSubMeshProxy(salome_mesh), salome_utilities.IsMeshGroup(salome_mesh)]):
            mesh_identifier = salome_utilities.GetSalomeID(salome_mesh)
        elif salome_utilities.IsMesh(salome_mesh):
            mesh_identifier = salome_utilities.GetSalomeID(salome_mesh.GetMesh())
        else:
            err_msg  = 'Type of argument "salome_mesh" not permitted: {}\n'.format(type(salome_mesh))
            err_msg += 'No mesh can be retrieved from this input!'.format(type(salome_mesh))
            logger.error(err_msg)
            raise Exception(err_msg)

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
