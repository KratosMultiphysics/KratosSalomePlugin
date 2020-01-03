#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher
#


class Application(object):

    ### public methods ###
    def WriteCalculationFiles(self, path):
        self._RaiseNotImplementedError("WriteCalculationFiles")

    def Serialize(self):
        self._RaiseNotImplementedError("Serialize")

    def Deserialize(self, serialized_obj):
        self._RaiseNotImplementedError("Deserialize")


    # protected methods ###
    def _RaiseNotImplementedError(self, method_name):
        raise NotImplementedError('Method "{}" was not implemented in {}'.format(method_name, self._ClassName))


    # protected class methods ###
    @classmethod
    def _ClassName(cls):
        return cls.__name__