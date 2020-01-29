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

def CreateModelPartFromMesh(mesh_descriptions):
    model_part = ModelPart("dummy")

    connectivities_io = ConnectivitiesIO(model_part)

    for mesh_name, mesh_descr in mesh_descriptions.items():
        connectivities_io.AddMesh(mesh_name, mesh_descr[0], mesh_descr[1])

    return model_part


def WriteModelPart(mesh_descriptions, path, file_format="mdpa"):
    if file_format == "mdpa":
        WriteMdpa(CreateModelPartFromMesh(mesh_descriptions), path)
    else:
        raise NotImplementedError('The requested file format "{}" is not available'.format(file_format))