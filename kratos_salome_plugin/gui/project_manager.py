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
from kratos_salome_plugin import salome_study_utilities

class GroupsManager(object):
    """Temp implementation"""
    def __init__(self):
        pass

    def Serialize(self):
        return []

    def Deserialize(self, serialized_obj):
        pass


class ProjectManager(object):
    def __init__(self):
        self.__InitializeMembers()

    def __InitializeMembers(self):
        self.groups_manager = GroupsManager()
        self.application = None

    def SaveProject(self, save_path):
        if not save_path.endswith(".ksp"):
            save_path += ".ksp"

        # fixing potential issues with path
        save_path = os.path.abspath(save_path)

        logger.info('saving project: "%s" ...', save_path)

        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        # save study
        salome_study_path = os.path.abspath(os.path.join(save_path, "salome_study.hdf"))
        save_successful = salome_study_utilities.SaveStudy(salome_study_path)
        if not save_successful:
            logger.critical('Saving study "{}" was not successful!'.format(salome_study_path))

        # save plugin data
        project_dict = {"general":{}}

        # general information
        general = project_dict["general"]
        general["version_plugin"] = GetVersionsPlugin()
        general["version_salome"] = salome_utilities.GetVersions()

        localtime = time.asctime( time.localtime(time.time()) )
        general["creation_time"] = localtime

        general["operating_system"] = sys.platform

        # groups
        project_dict["groups"] = self.groups_manager.Serialize()

        # application
        if self.application:
            project_dict["application"] = {}
            project_dict["application"]["application_module"] = mod(self.application) # necessary for deserialization
            project_dict["application"]["application_data"] = self.application.Serialize()

        # dump to json
        plugin_data_path = os.path.abspath(os.path.join(save_path, "plugin_data.json"))
        with open(plugin_data_path, "w") as data_file:
            json.dump(project_dict, data_file, indent=4)

        logger.info("saved project")

    def OpenProject(self, open_path):
        logger.info('opening project: "%s" ...', open_path)

        # fixing potential issues with path
        open_path = os.path.abspath(open_path)

        # check the necessary files exist
        if not os.path.isdir(open_path):
            raise Exception('Attempting to open project "{}" failed, it does not exist!'.format(open_path))

        salome_study_path = os.path.abspath(os.path.join(open_path, "salome_study.hdf"))
        plugin_data_path = os.path.abspath(os.path.join(open_path, "plugin_data.json"))

        if not os.path.isdir(open_path):
            raise Exception('Attempting to open project "{}" failed, it does not exist!'.format(open_path))

        if not os.path.isfile(salome_study_path):
            raise Exception('Salome study does not exist in project "{}"'.format(open_path))

        if not os.path.isfile(plugin_data_path):
            raise Exception('Plugin data file does not exist in project "{}"'.format(open_path))

        # clean leftovers
        self.__InitializeMembers()

        # open study
        open_successful = salome_study_utilities.OpenStudy(salome_study_path)
        if not open_successful:
            logger.critical('Opening study "{}" was not successful!'.format(salome_study_path))

        with open(plugin_data_path, 'r') as plugin_data_file:
            plugin_data = json.load(plugin_data_file)

        # check versions
        # this might be useful in the future for backwards compatibility
        logger.info("Version plugin: %s", plugin_data["general"]["version_plugin"])
        logger.info("Salome plugin: %s", plugin_data["general"]["version_salome"])
        logger.info("Creation time: %s", plugin_data["general"]["creation_time"])
        logger.debug("Operating system: %s", plugin_data["general"]["operating_system"])

        # loading groups
        logger.info('loading %d groups', len(plugin_data["groups"]))

        if "application" in plugin_data:
            application_module_name = plugin_data["application"]["application_module"]
            logger.info('loading application from module: "%s"', application_module_name)
            application_module = __import__(application_module_name)
            self.application = application_module.Create()
            self.application.Deserialize(plugin_data["application"]["application_data"])

        logger.info("opened project")

    def ResetProject(self):
        self.__InitializeMembers()
        logger.info("resetting project")

    def ProjectHasUnsavedChanges(self):
        # check if study is empty
        # if not empty check if is modified
        # if is modified then ask if proceed

        # check Salome Study
        # is modified?
        # number of things in study => if nothing is there I don't need to check anything

        # check GroupsManager

        # check Application

        return False
