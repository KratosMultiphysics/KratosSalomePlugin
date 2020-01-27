#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#


# plugin imports
from model_part import ModelPart
from connectivities_io import ConnectivitiesIO

from write_mdpa import WriteMdpa

def CreateModelPartFromMesh(mesh_definition):
    model_part = ModelPart("dummy")

    connectivities_io = ConnectivitiesIO(model_part)

    for mesh_def in mesh_definition:
        connectivities_io.AddMesh(mesh_def[0], mesh_def[1])


def WriteModelPart(mesh_definition, path, file_format="mdpa"):
    if file_format == "mdpa":
        WriteMdpa(CreateModelPartFromMesh(mesh_definition), path)
    else:
        raise NotImplementedError('The requested file format "{}" is not available'.format(file_format))