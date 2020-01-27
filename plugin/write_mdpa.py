#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

def _WriteHeaderMdpa(self, additional_header, file_stream):
    pass

def _WriteNodesMdpa(self, nodes, file_stream):
    pass

def _WriteEntitiesMdpa(self, entities, entity_name, file_stream):
    pass

def _WriteEntityDataMdpa(self, entities, entity_name, file_stream):
    pass

def _WriteSubModelPartMdpa(self, sub_model_part, file_stream):
    # ...

    # write SubModelParts recursively
    for smp in sub_model_part.SubModelParts:
        _WriteSubModelPartMdpa(smp, file_stream)


def WriteMdpa(model_part, file_name, additional_header=""):
    if not file_name.endswith(".mdpa"):
        file_name += ".mdpa"

    with open(file_name, 'w') as mdpa_file:
        _WriteHeaderMdpa(additional_header, mdpa_file)

        _WriteNodesMdpa(model_part.Nodes, mdpa_file)
        _WriteEntitiesMdpa(model_part.Elements, "element", mdpa_file)
        _WriteEntitiesMdpa(model_part.Conditions, "condition", mdpa_file)

        _WriteEntityDataMdpa(model_part.Nodes, "node", mdpa_file)
        _WriteEntityDataMdpa(model_part.Elements, "element", mdpa_file)
        _WriteEntityDataMdpa(model_part.Conditions, "condition", mdpa_file)

        for smp in model_part.SubModelParts:
            _WriteSubModelPartMdpa(smp, mdpa_file)
