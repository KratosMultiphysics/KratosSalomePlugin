#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# this file sets up the testing environment and should be the first import in every testing file

import sys, os
sys.path.append(os.pardir) # needed to bring the plugin into the path, e.g. make "import ks_plugin" possible
os.environ["KS_PLUGIN_TESTING"] = "1" # this disables all logging, see "ks_plugin.plugin_logging"