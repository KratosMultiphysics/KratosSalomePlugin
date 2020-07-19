#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# This file contains a collection of functionalities that are useful for developing / debugging but should not be used in production

# python imports
import sys

def PrintObjectInfo(label, obj, print_python_methods=False):
    # function to print all methods of an object
    # very useful to see what the objects of salome have to offer
    sys.stdout.flush()
    print('\nPrinting information for object "{}" of type: {}'.format(label, type(obj)))

    print('Methods:')
    methods = [m for m in dir(obj) if not m.startswith('__') and callable(getattr(obj,m))]
    for method in sorted(methods):
        print('\t' + str(method))

    print('\nAttributes:')
    attributes = [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj,a))]
    attributes_by_type = {}
    for attribute in sorted(attributes):
        attr_type = str(type(getattr(obj,attribute)))
        if attr_type not in attributes_by_type:
            attributes_by_type[attr_type] = []
        attributes_by_type[attr_type].append(attribute)

    sorted_types = sorted(list(attributes_by_type.keys()))

    for attr_type in sorted_types:
        print("\tType:", attr_type)
        for attr in attributes_by_type[attr_type]:
            print("\t\t", attr)
        print()

    if print_python_methods:
        print('\nPYTHON Methods:')
        methods = [m for m in dir(obj) if m.startswith('__') and callable(getattr(obj,m))]
        for method in sorted(methods):
            print('\t' + str(method))

        print('\nPYTHON Attributes:')
        attributes = [a for a in dir(obj) if a.startswith('__') and not callable(getattr(obj,a))]
        for attribute in sorted(attributes):
            print('\t' + str(attribute))

    sys.stdout.flush()

def print_with_flush(*args):
    print(args)
    sys.stdout.flush()