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
from abc import ABCMeta, abstractmethod


class Application(metaclass=ABCMeta):

    ### public methods ###
    @abstractmethod
    def WriteCalculationFiles(self, path):
        pass

    @abstractmethod
    def Serialize(self):
        pass

    @abstractmethod
    def Deserialize(self, serialized_obj):
        pass


    # protected class methods ###
    @classmethod
    def _ClassName(cls):
        return cls.__name__