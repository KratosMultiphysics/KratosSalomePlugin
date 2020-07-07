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
This file contains functions for interacting with the Salome Study
NOTE: This file must NOT have dependencies on other files in the plugin!
"""

# python imports
import os
import logging
logger = logging.getLogger(__name__)

# salome imports
from salome import myStudy


def GetNumberOfObjectsInComponent(component):
    """Counts the number of objects in a component (e.g. GEOM, SMESH)
    adapted from "KERNEL/lib/python3.6/site-packages/salome/salome_study.py"
    """
    num_objs_in_comp = 0
    it = myStudy.NewChildIterator(component)
    while it.More():
        component_child = it.Value()
        num_objs_in_comp += 1 + GetNumberOfObjectsInComponent(component_child) # +1 bcs recursion
        it.Next()
    return num_objs_in_comp

def GetNumberOfObjectsInStudy():
    """Counts the number of objects in the study, for all components
    adapted from "KERNEL/lib/python3.6/site-packages/salome/salome_study.py"
    """
    # myStudy.DumpStudy() # for debugging

    itcomp = myStudy.NewComponentIterator()
    num_objs_in_study = 0
    while itcomp.More(): # loop components (e.g. GEOM, SMESH)
        component = itcomp.Value()
        num_objs_in_study += GetNumberOfObjectsInComponent(component)
        itcomp.Next()
    return num_objs_in_study

def IsStudyModified():
    """returns whether the study has unsaved modifications
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    return myStudy.GetProperties().IsModified()

def SaveStudy(file_name):
    """saves the study as a single file, non-ascii
    returns whether saving the study was successful
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    if not file_name:
        raise NameError('"file_name" cannot be empty!')

    if not file_name.endswith(".hdf"):
        file_name += ".hdf"

    # create folder if necessary
    # required bcs otherwise Salome an crash if the folder to save the study in does not yet exist
    save_dir = os.path.split(file_name)[0]
    if not os.path.isdir(save_dir) and save_dir:
        os.makedirs(save_dir)

    save_successful = myStudy.SaveAs(file_name, False, False) # args: use_multifile, use_acsii
    return save_successful

def OpenStudy(file_name):
    """opens a study
    returns whether opening the study was successful
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    if not file_name:
        raise NameError('"file_name" cannot be empty!')

    if not os.path.isfile(file_name):
        raise FileNotFoundError('File "{}" does not exist!'.format(file_name))

    if not file_name.endswith(".hdf"):
        logger.warning('Opening study from file without "*.hdf" extension: "{}"'.format(file_name))

    if IsStudyModified():
        logger.warning('Opening study when current study has unsaved changes')

    open_successful = myStudy.Open(file_name)
    return open_successful

def ResetStudy():
    """resets the study, no objects are left afterwards
    see https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
    """
    myStudy.Clear()
    myStudy.Init()
