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
The function ReadMdpa reads an mdpa file into a ModelPart
"""

# python imports
import time
import os
import logging
logger = logging.getLogger(__name__)

def _LineIsEmpty(line):
    return line == ""

def _LineStartsWith(line, string):
    return line.startswith(string) # remove leading whitespaces before check

def _LineIsComment(line):
    return _LineStartsWith(line, "//")

def _CleanReadLine(file):
    # removing comments, replacing tabs with spaces and trailing & leading whitespaces
    return file.readline().split("//")[0].replace("\t", " ").strip()

def _CheckExpectedKeyword(expected_keyword, read_keyword):
    if expected_keyword != read_keyword:
        raise Exception('Read wrong keyword, expected "{}", read "{}"'.format(expected_keyword, read_keyword))

def _CheckEndBlock(line, block_keyword):
    if _LineStartsWith(line, "End"):
        keyword = line.split()[1]
        _CheckExpectedKeyword(block_keyword, keyword)
        return True
    else:
        return False

def _SkipBlock(block_keyword, file):
    while True:
        line = _CleanReadLine(file)
        if _CheckEndBlock(line, block_keyword):
            break

def _ReadNodesBlock(model_part, file):
    while True:
        line = _CleanReadLine(file)
        if _CheckEndBlock(line, "Nodes"):
            break

        line_splitted = line.split()
        model_part.CreateNewNode(int(line_splitted[0]), float(line_splitted[1]), float(line_splitted[2]), float(line_splitted[3]))


def _ReadBlock(model_part, block_name, file):
    if block_name == "Nodes":
        _ReadNodesBlock(model_part, file)
    elif block_name == "Elements":
        _ReadElementsBlock(model_part, file)
    elif block_name == "Conditions":
        _ReadConditionsBlock(model_part, file)
    elif block_name == "Properties":
        _ReadPropertiesBlock(model_part, file)
    elif block_name == "NodalData":
        _ReadNodalDataBlock(model_part, file)
    elif block_name == "ElementalData":
        _ReadElementalDataBlock(model_part, file)
    elif block_name == "ConditionalData":
        _ReadConditionalDataBlock(model_part, file)
    elif block_name == "SubModelPart":
        _ReadSubModelPartBlock(model_part, file)
    else:
        logger.warning('Skipping reading block with unknown name "%s"', block_name)
        _SkipBlock(block_name, file)


def ReadMdpa(model_part, file_name):
    logger.info('Starting to read ModelPart "%s" from file "%s"', model_part.Name, file_name)
    start_time = time.time()

    with open(file_name, 'r') as mdpa_file:
        # reading line by line in case of large files
        while True:
            # Get next line from file
            line = _CleanReadLine(mdpa_file)

            if not line: # eof
                break

            # skip empty lines
            if _LineIsEmpty(line):
                continue

            # skip comment lines, i.e. lines starting with "//"
            if _LineIsComment(line):
                continue

            if _LineStartsWith(line, "Begin"):
                block_name = line.split()[1]
                _ReadBlock(model_part, block_name, mdpa_file)

    logger.info('Reading ModelPart took {0:.{1}f} [s]'.format(time.time()-start_time,2))
