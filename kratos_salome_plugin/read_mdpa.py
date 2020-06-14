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

def _ReadCleanLine(file):
    # removing comments, replacing tabs with spaces and trailing & leading whitespaces
    return file.readline().split("//")[0].replace("\t", " ").strip()

def _CheckExpectedKeyword(expected_keyword, read_keyword):
    if expected_keyword != read_keyword:
        raise Exception('Read wrong keyword, expected "{}", read "{}"'.format(expected_keyword, read_keyword))

def _ReadNodesBlock(model_part, file):
    while True:
        line = _ReadCleanLine(file)
        if _LineStartsWith(line, "End"):
            keyword = line.split()[1]
            _CheckExpectedKeyword("Nodes", keyword)
            break

        line_splitted = line.split()
        model_part.CreateNewNode(int(line_splitted[0]), float(line_splitted[1]), float(line_splitted[2]), float(line_splitted[3]))

def _ReadBlock(model_part, file, line):
    keyword = line.split()[1]
    if keyword == "Nodes":
        _ReadNodesBlock(model_part, file)
    else: raise NotImplementedError


def ReadMdpa(model_part, file_name):
    logger.info('Starting to read ModelPart "%s" from file "%s"', model_part.Name, file_name)
    start_time = time.time()

    with open(file_name, 'r') as mdpa_file:
        # reading line by line in case of large files
        while True:
            # Get next line from file
            line = _ReadCleanLine(mdpa_file)

            if not line: # eof
                break

            # skip empty lines
            if _LineIsEmpty(line):
                continue

            # skip comment lines, i.e. lines starting with "//"
            if _LineIsComment(line):
                continue

            if _LineStartsWith(line, "Begin"):
                _ReadBlock(model_part, mdpa_file, line)

    logger.info('Reading ModelPart took {0:.{1}f} [s]'.format(time.time()-start_time,2))
