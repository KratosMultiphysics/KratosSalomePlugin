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
The baseclass of the Applications, which defines the interface
"""

# python imports
from pathlib import Path
from typing import Tuple
from abc import ABCMeta, abstractmethod


class Application(metaclass=ABCMeta):

    ### public methods ###
    @abstractmethod
    def WriteCalculationFiles(self, path: Path) -> bool:
        """Write the files necessary for running the case"""
        pass

    @abstractmethod
    def Serialize(self) -> Tuple[bool, dict]:
        """Serialize the current status of the application
        such that it can be loaded again. This is used for saving.
        """
        pass

    @abstractmethod
    def Deserialize(self, serialized_obj: dict) -> bool:
        """Deserialize the application which has been serialized before.
        This is used for loading a previously saved case.
        """
        pass


    ### protected class methods ###
    @classmethod
    def _ClassName(cls) -> str:
        """returns the name of the class"""
        return cls.__name__