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
"""

# python imports
import os
import sys
import json
import time
import logging
logger = logging.getLogger(__name__)

# plugin imports
from ..version import GetVersions as GetVersionsPlugin
from kratos_salome_plugin import salome_utilities

class GroupsManager(object):
    def __init__(self):
        pass

    def Serialize(self):
        return []

    def Deserialize(self, serialized_obj):
        pass

class ProjectManager(object):
    def __init__(self):
        logger.critical("Initializing ProjectManager!")

        self.application = None
        self.groups_manager = GroupsManager()

    def SaveProject(self, save_path):
        if not save_path.endswith(".ksp"):
            save_path += ".ksp"

        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        # save study
        save_successful = salome_utilities.SaveStudy(os.path.join(save_path, "salome_study"))
        if not save_successful:
            logger.critical("Saving study was not successful!!!:") # TODO add study save path as abspath!

        # save project
        project_dict = {}

        # general information
        project_dict["version_plugin"] = GetVersionsPlugin()
        project_dict["version_salome"] = salome_utilities.GetVersions()

        localtime = time.asctime( time.localtime(time.time()) )
        project_dict["creation_time"] = localtime

        project_dict["operating_system"] = sys.platform

        # groups
        project_dict["groups"] = self.groups_manager.Serialize()

        # application
        if self.application:
            project_dict["application"]["application_module"] = mod(self.application) # necessary for deserialization
            project_dict["application"]["application_data"] = self.application.Serialize()

        with open(os.path.join(save_path, "plugin_data.json"),"w") as data_file:
            json.dump(project_dict, data_file, indent=4)

        logger.warning("SaveProject: %s", save_path)

    def OpenProject(self, open_path):
        if not self.__WarnIfUnsavedChangesExist():
            return

        # check if study is empty
        # if not empty check if is modified
        # if is modified then ask if proceed
        logger.warning("OpenProject: %s", open_path)

    def ResetProject(self):
        if not self.__WarnIfUnsavedChangesExist():
            return

        self.application = None
        logger.warning("ResetProject")

    def HasForUnsavedChanges(self):
        # check Salome Study
        # is modified?
        # number of things in study => if nothing is there I don't need to check anything

        # check GroupsManager

        # check Application

        return False

    def __WarnIfUnsavedChangesExist(self):
        return True