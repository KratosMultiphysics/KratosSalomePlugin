#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

def __CheckIfIsExecutedInSalome():
    """This module can only be imported when running inside of Salome
    It is a "private" function to not pollute the global namespace
    """
    from ..utilities import IsExecutedInSalome
    if not IsExecutedInSalome():
        raise ImportError("This module can only be imported when running inside of Salome!")

__CheckIfIsExecutedInSalome()
