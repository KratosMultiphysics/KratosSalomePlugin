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
import copy
logger = logging.getLogger(__name__)
logger.debug('loading module')

def _WriteHeaderMdpa(model_part, additional_header, file_stream):
    def WriteSubModelPartInfo(model_part,
                              file_stream,
                              level):
        SPACE = "    "
        for smp in model_part.SubModelParts:
            file_stream.write("// {}SubModelPart: {}\n".format(SPACE*level, smp.Name))
            file_stream.write("// {}Number of Nodes: {}\n".format(SPACE*level, smp.NumberOfNodes()))
            file_stream.write("// {}Number of Elements: {}\n".format(SPACE*level, smp.NumberOfElements()))
            file_stream.write("// {}Number of Conditions: {}\n".format(SPACE*level, smp.NumberOfConditions()))
            file_stream.write("// {}Number of Properties: {}\n".format(SPACE*level, smp.NumberOfProperties()))
            file_stream.write("// {}Number of SubModelParts: {}\n".format(SPACE*level, smp.NumberOfSubModelParts()))
            WriteSubModelPartInfo(smp,file_stream, level+1)

    localtime = time.asctime( time.localtime(time.time()) )
    file_stream.write("// File created on " + localtime + "\n")
    if additional_header != "":
        file_stream.write("// {}\n".format(additional_header))
    file_stream.write("// Mesh Information:\n")
    file_stream.write("// Number of Nodes: {}\n".format(model_part.NumberOfNodes()))
    file_stream.write("// Number of Elements: {}\n".format(model_part.NumberOfElements()))
    file_stream.write("// Number of Conditions: {}\n".format(model_part.NumberOfConditions()))
    file_stream.write("// Number of Properties: {}\n".format(model_part.NumberOfProperties()))
    file_stream.write("// Number of SubModelParts: {}\n".format(model_part.NumberOfSubModelParts()))
    WriteSubModelPartInfo(model_part,file_stream, level=1)
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

        file_stream.write('\t{}\t{}\t{}\n'.format(entity.Id, entity.properties.Id, "\t".join([str(node.Id) for node in entity.GetNodes()])))
    file_stream.write("End {}s // {}\n\n".format(entities_name, current_entity_name))

def __VariableFormatter(val):
    def ListToString(the_list):
        return ",".join([str(v) for v in the_list if v!=" "]) # also strips the whitespaces inbetween

    def VectorToString(val):
        return '[{}] ({})'.format(len(val), ListToString(val))

    def MatrixToString(val):
        matrix_as_string = ",".join(["({})".format(ListToString(v)) for v in val])
        return '[{},{}] ({})'.format(len(val), len(val[0]), matrix_as_string)

    if isinstance(val, list):
        if len(val) == 0:
            raise Exception('Data {} of type "vector" cannot be empty!')
        if isinstance(val[0], list): # matrix
            return MatrixToString
        else: # vector
            return VectorToString
    else: # other type
        return str

def _WriteEntityDataMdpa(entities, entities_name, file_stream):
    def WriteDataBlock(entities, entities_name, variable_name, variable_formatter, file_stream):
        if entities_name == "Nod": # nodes also need the fixity specified, currently hardcoded to 0
            format_string = "\t{} 0\t{}\n"
        else:
            format_string = "\t{}\t{}\n"

        file_stream.write("Begin {}alData {}\n".format(entities_name, variable_name))
        for entity in entities:
            if entity.Has(variable_name):
                file_stream.write(format_string.format(entity.Id, variable_formatter(entity.GetValue(variable_name))))
        file_stream.write("End {}alData // {}\n\n".format(entities_name, variable_name))

    written_variables = []
    # creating two indepentent iterators, since we iterate twice at the same time
    entities_iter = iter(entities)
    inner_entities_iter = copy.copy(entities_iter)

    for entity in entities_iter:
        for var_name in sorted(entity.GetData()): # sorting to make reading and testing easier
            if var_name not in written_variables:
                written_variables.append(var_name)
                WriteDataBlock(inner_entities_iter, entities_name, var_name, __VariableFormatter(entity.GetValue(var_name)), file_stream)

def __WriteDataValueContainer(container, file_stream, level=0):
    for key in sorted(container): # sorting to make reading and testing easier
        val = container[key]
        variable_formatter = __VariableFormatter(val)

        file_stream.write("{}{}\t{}\n".format("\t"*(level+1), key, variable_formatter(val)))

def _WritePropertiesMdpa(properties, file_stream):
    for props in properties:
        file_stream.write("Begin Properties {}\n".format(props.Id))
        __WriteDataValueContainer(props.GetData(), file_stream)
        file_stream.write("End Properties // {}\n\n".format(props.Id))

def _WriteModelPartDataMdpa(model_part, file_stream, level=0):
    # level 0 means Main-ModelPart
    # level 1... means SubModelPart
    pre_identifier = ""
    if level > 0:
        pre_identifier = "Sub"

    file_stream.write("{}Begin {}ModelPartData\n".format("\t"*level, pre_identifier))
    __WriteDataValueContainer(model_part.GetData(), file_stream, level)
    file_stream.write("{}End {}ModelPartData\n".format("\t"*level, pre_identifier))
    if level == 0:
        file_stream.write("\n")

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
