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
import time
import logging
logger = logging.getLogger(__name__)
logger.debug('loading module')

def _WriteHeaderMdpa(model_part, additional_header, file_stream):
    def WriteSubModelPartInfo(model_part,
                              file_stream,
                              level):
        SPACE = "    "
        for smp in model_part.SubModelParts:
            file_stream.write("// " + SPACE*level + "SubModelPart " + smp.Name + "\n")
            file_stream.write("// " + SPACE*level + "Number of Nodes: " + str(smp.NumberOfNodes()) + "\n")
            file_stream.write("// " + SPACE*level + "Number of Elements: " + str(smp.NumberOfElements()) + "\n")
            file_stream.write("// " + SPACE*level + "Number of Conditions: " + str(smp.NumberOfConditions()) + "\n")
            file_stream.write("// " + SPACE*level + "Number of SubModelParts: " + str(smp.NumberOfSubModelParts()) + "\n")
            WriteSubModelPartInfo(smp,file_stream, level+1)

    localtime = time.asctime( time.localtime(time.time()) )
    file_stream.write("// File created on " + localtime + "\n")
    if additional_header != "":
        file_stream.write("// {}\n".format(additional_header))
    file_stream.write("// Mesh Information:\n")
    file_stream.write("// Number of Nodes: " + str(model_part.NumberOfNodes()) + "\n")
    file_stream.write("// Number of Elements: " + str(model_part.NumberOfElements()) + "\n")
    file_stream.write("// Number of Conditions: " + str(model_part.NumberOfConditions()) + "\n")
    file_stream.write("// Number of SubModelParts: " + str(model_part.NumberOfSubModelParts()) + "\n")
    WriteSubModelPartInfo(model_part,file_stream, level=0)
    file_stream.write("\n")

def _WriteNodesMdpa(nodes, file_stream):
    file_stream.write("Begin Nodes\n")
    precision = 10
    for node in nodes:
        file_stream.write('\t{0}\t{1:.{4}f}\t{2:.{4}f}\t{3:.{4}f}\n'.format(node.Id, node.X, node.Y, node.Z, precision))
    file_stream.write("End Nodes\n\n")

def _WriteEntitiesMdpa(entities, entities_name, file_stream):
    current_entity_name = next(iter(entities)).name # get name of first entity

    file_stream.write("Begin {}s {}\n".format(entities_name, current_entity_name))

    for entity in entities:
        entity_name = entity.name
        if entity_name != current_entity_name:
            file_stream.write("End {}s // {}\n\n".format(entities_name, current_entity_name))
            current_entity_name = entity_name
            file_stream.write("Begin {}s {}\n".format(entities_name, current_entity_name))

        file_stream.write('\t{}\t{}\t{}\n'.format(entity.Id, entity.properties.Id, "\t".join([str(node.Id) for node in entity.nodes])))
    file_stream.write("End {}s // {}\n\n".format(entities_name, current_entity_name))

def _WriteEntityDataMdpa(entities, entities_name, file_stream):
    pass
    # file_stream.write("Begin {}alData {}\n".format(entities_name))
    # # for
    # file_stream.write("End {}alData {}\n".format(entities_name))

def __WriteDataValueContainer(container, file_stream, level=0):
    def ListToString(the_list):
        return ",".join([str(v) for v in the_list if v!=" "]) # also strips the whitespaces inbetween

    def MatrixToString(the_matrix):
        return ",".join(["({})".format(ListToString(v)) for v in the_matrix])

    for key in sorted(container): # sorting to make reading and testing easier
        val = container[key]
        if isinstance(val, list):
            if len(val) == 0:
                raise Exception('Data {} of type "vector" cannot be empty!')
            if isinstance(val[0], list): # matrix
                str_val = '[{},{}] ({})'.format(len(val), len(val[0]), MatrixToString(val))
            else: # vector
                str_val = '[{}] ({})'.format(len(val), ListToString(val))
        else: # other type
            str_val = str(val)

        file_stream.write("{}{}\t{}\n".format("\t"*(level+1), key, str_val))

def _WritePropertiesMdpa(properties, file_stream):
    for props in properties:
        file_stream.write("Begin Properties {}\n".format(props.Id))
        __WriteDataValueContainer(props.GetData(), file_stream)
        file_stream.write("End Properties // {}\n".format(props.Id))

def _WriteModelPartDataMdpa(model_part, file_stream, level=0):
    # level 0 means Main-ModelPart
    # level 1... means SubModelPart
    pre_identifier = ""
    if level > 0:
        pre_identifier = "Sub"

    file_stream.write("{}Begin {}ModelPartData\n".format("\t"*level, pre_identifier))
    __WriteDataValueContainer(model_part.GetData(), file_stream, level)
    file_stream.write("{}End {}ModelPartData\n".format("\t"*level, pre_identifier))

def _WriteSubModelPartsMdpa(sub_model_part, file_stream, level=0):
    def WriteSubModelPartEntities(entities, entities_name, file_stream, level):
        file_stream.write("{}Begin SubModelPart{}\n".format("\t"*level, entities_name))
        for entity in entities:
            file_stream.write("{}{}\n".format("\t"*(level+1), entity.Id))
        file_stream.write("{}End SubModelPart{}\n".format("\t"*level, entities_name))

    file_stream.write("{}Begin SubModelPart {}\n".format("\t"*level, sub_model_part.Name))

    if sub_model_part.HasData():
        _WriteModelPartDataMdpa(sub_model_part, file_stream, level+1)

    if sub_model_part.NumberOfNodes() > 0:
        WriteSubModelPartEntities(sub_model_part.Nodes, "Nodes", file_stream, level+1)
    if sub_model_part.NumberOfElements() > 0:
        WriteSubModelPartEntities(sub_model_part.Elements, "Elements", file_stream, level+1)
    if sub_model_part.NumberOfConditions() > 0:
        WriteSubModelPartEntities(sub_model_part.Conditions, "Conditions", file_stream, level+1)

    # write SubModelParts recursively
    for smp in sub_model_part.SubModelParts:
        _WriteSubModelPartsMdpa(smp, file_stream, level+1)
    file_stream.write("{}End SubModelPart // {}\n".format("\t"*level, sub_model_part.Name))


def WriteMdpa(model_part, file_name, additional_header=""):
    if not file_name.endswith(".mdpa"):
        file_name += ".mdpa"

    logger.info('Starting to write ModelPart "{}" to file "{}"'.format(model_part.Name, file_name))
    start_time = time.time()

    with open(file_name, 'w') as mdpa_file:
        _WriteHeaderMdpa(model_part, additional_header, mdpa_file)

        if model_part.HasData():
            _WriteModelPartDataMdpa(model_part, mdpa_file)

        _WritePropertiesMdpa(model_part.Properties, mdpa_file)

        _WriteNodesMdpa(model_part.Nodes, mdpa_file)
        _WriteEntitiesMdpa(model_part.Elements, "Element", mdpa_file)
        _WriteEntitiesMdpa(model_part.Conditions, "Condition", mdpa_file)

        _WriteEntityDataMdpa(model_part.Nodes, "Nod", mdpa_file)
        _WriteEntityDataMdpa(model_part.Elements, "Element", mdpa_file)
        _WriteEntityDataMdpa(model_part.Conditions, "Condition", mdpa_file)

        for smp in model_part.SubModelParts:
            _WriteSubModelPartsMdpa(smp, mdpa_file)

    logger.info('Writing ModelPart took {0:.{1}f} [s]'.format(time.time()-start_time,2))
