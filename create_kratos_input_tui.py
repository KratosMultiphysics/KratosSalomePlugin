#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

"""
This file contains simple to use functionalities for creating
Kratos input based on Salome meshes.
"""

# python imports
import os
import logging

# specify logging path
# needs to be done before importing the plugin bcs logging is initialized
# when importing the plugin for the first time (inside "__init__.py")
os.environ["KRATOS_SALOME_PLUGIN_LOG_FILE_PATH"] = os.getcwd()

# plugin imports
from kratos_salome_plugin.model_part import ModelPart
from kratos_salome_plugin import geometries_io
from kratos_salome_plugin.mesh_interface import MeshInterface
from kratos_salome_plugin.write_mdpa import WriteMdpa
from kratos_salome_plugin import salome_utilities
from kratos_salome_plugin import salome_mesh_utilities

logger = logging.getLogger(__name__) # done after importing the plugin, which initializes the logging


class SalomeMesh(geometries_io.Mesh):
    """Specialized version of Mesh to make access to Salome-meshes easier"""

    def __init__(self, salome_mesh, mesh_description, model_part_name=""):
        """Keyword arguments:
        salome_mesh -- the Salome mesh to access. Depending on the type the corresponding conversion is performed before creating a MeshInterface that is then passed to the base class
        mesh_description -- see base class
        model_part_name -- see base class
        """

        if isinstance(salome_mesh, str):
            mesh_identifier = salome_mesh
        elif any([salome_mesh_utilities.IsMeshProxy(salome_mesh), salome_mesh_utilities.IsSubMeshProxy(salome_mesh), salome_mesh_utilities.IsMeshGroup(salome_mesh)]):
            mesh_identifier = salome_utilities.GetSalomeID(salome_mesh)
        elif salome_mesh_utilities.IsMesh(salome_mesh):
            mesh_identifier = salome_utilities.GetSalomeID(salome_mesh.GetMesh())
        else:
            err_msg  = 'Type of argument "salome_mesh" not permitted: {}\n'.format(type(salome_mesh))
            err_msg += 'No mesh can be retrieved from this input!'.format(type(salome_mesh))
            raise Exception(err_msg)

        mesh_interface = MeshInterface(mesh_identifier)

        super().__init__(mesh_interface, mesh_description, model_part_name)


def CreateModelPart(meshes):
    """Creates a ModelPart given meshes as input"""
    logger.debug('Calling "CreateModelPart"')
    model_part = ModelPart()
    geometries_io.GeometriesIO.AddMeshes(model_part, meshes)

    return model_part


def CreateMdpaFile(meshes, mdpa_file_name):
    """Creates a mdpa-file given meshes as input"""
    logger.debug('Calling "CreateMdpaFile"')
    model_part = CreateModelPart(meshes)
    WriteMdpa(model_part, mdpa_file_name)
