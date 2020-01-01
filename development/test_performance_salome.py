#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.2.1 with dump python functionality
###

'''Script to test the performance of different methods for extracting the mesh from salome'''

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/philipp')
sys.path.insert(0, r'../kratos_plugin')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS
from time import time
import kratos_mesh_converter as kmc
from multiprocessing.dummy import Pool


geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
Box_1 = geompy.MakeBoxDXDYDZ(200, 200, 200)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Box_1, 'Box_1' )

###
### SMESH component
###

def ReadDatFile(file_name):
    nodes = [] # TODO preallocate?
    geom_entities = {}

    with open(file_name,"r") as f:
        lines = f.readlines()
        # .dat header
        line = lines[0].split()
        num_nodes = int(line[0])
        # num_elems = int(line[1])
        # nodes = lines[1:num_nodes+1]

        if num_nodes == 0:
            raise RuntimeError("File is empty")

        # Reading Nodes
        for line in lines[1:num_nodes+1]:
            words = line.split()
            nodes.append(kmc.MeshNode(
                    int(words[0]),   # Id
                    float(words[1]), # X
                    float(words[2]), # Y
                    float(words[3])  # Z
                ))

        # Reading Geometric Objects (Lines, Triangles, Quads, ...)
        for line in lines[num_nodes+1:]:
            words = line.split()
            geom_id = int(words[0])
            geometry_identifier = int(words[1]) # get the salome identifier

            if geometry_identifier not in geom_entities: # geom entities with this identifier are already existing # TODO don't I have to use .key() here?
                geom_entities[geometry_identifier] = []

            node_list = [int(words[i]) for i in range(2, len(words))]

            # self.node_reorder_function(node_list) # needed bcs the mesh-connectivity might be different

            geom_entities[geometry_identifier].append(kmc.MeshConnectivity(geom_id, node_list))

    return nodes, geom_entities

def PrintObjectInfo(label, obj, print_python_methods=False):
    sys.stdout.flush()
    print('\nPrinting information for object "{}" of type: {}'.format(label, type(obj)))

    print('Methods:')
    methods = [m for m in dir(obj) if not m.startswith('__') and callable(getattr(obj,m))]
    for method in sorted(methods):
        print('\t' + str(method))

    print('\nAttributes:')
    attributes = [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj,a))]
    for attribute in sorted(attributes):
        print('\t' + str(attribute))

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

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
Mesh_1 = smesh.Mesh(Box_1)
Regular_1D = Mesh_1.Segment()
Max_Size_1 = Regular_1D.MaxSize(2.7)
MEFISTO_2D = Mesh_1.Triangle(algo=smeshBuilder.MEFISTO)
NETGEN_3D = Mesh_1.Tetrahedron()
start_time = time()
isDone = Mesh_1.Compute()
print("\nMesh computation time took: {}[s]".format(time()-start_time))

for i in range(10):
    Mesh_1.Add0DElement( i+1 )
for i in range(12):
    ballElem = Mesh_1.AddBall( i+3, 1+i )

print("Mesh Information:")
print("Number of Nodes: {}".format(Mesh_1.NbNodes()))
print("Number of Tetras: {}".format(Mesh_1.NbTetras()))


def GetElemNodesWrapper(elem_id):
    return Mesh_1.GetMesh().GetElemNodes(elem_id)

# def GetNodeXYZWrapper(node_id):
#     return Mesh_1.GetMesh().GetNodeXYZ(node_id)

# # for e in sorted(SMESH.EntityType._items):
# #   print(e)

# start_time = time()
# # filter_tri = smesh.GetFilter(SMESH.BALL, SMESH.FT_EntityType,'=', SMESH.Entity_Ball )
# filter_tri = smesh.GetFilter(SMESH.ALL, SMESH.FT_EntityType,'=', SMESH.Entity_Tetra)
# ids_tri = Mesh_1.GetIdsFromFilter(filter_tri)
# print("\nApplying filter took: {}[s]".format(time()-start_time))

# # print("Number of Tetras:", len(ids_tri))

# # PrintObjectInfo("SMESH", SMESH)


# start_time = time()
# elem_ids = []
# for i, e_id in enumerate(ids_tri):
#     # ddd = Mesh_1.GetElemNodes(e_id)
#     # ddd = Mesh_1.GetElementGeomType(e_id)
#     elem_ids.append(Mesh_1.GetElemNodes(e_id))
# print("\nGetting Element Nodes took: {}[s]".format(time()-start_time))

# # for i in range(1,9):
# #     start_time = time()
# #     pool = Pool(i)

# #     # PrintObjectInfo("pool", pool)
# #     elem_ids_map = pool.map(DUmmyFct, ids_tri)
# #     #close the pool and wait for the work to finish
# #     pool.close()
# #     pool.join()
# #     print("\nGetting Element Nodes with Pool-Map {} took: {}[s]".format(i, time()-start_time))

# # kmc.MeshNode()

# # GetNodeXYZ
# start_time = time()
# node_ids = Mesh_1.GetNodesId()
# print("\nGettig the node ids took: {}[s]".format(time()-start_time))

# print("Number of Nodes:", len(node_ids))

# # PrintObjectInfo("Mesh", Mesh_1.GetMesh())

# start_time = time()
# nodes = []
# for i, n_id in enumerate(node_ids):
#     nodes.append(Mesh_1.GetNodeXYZ(n_id))
# print("\nGetting Nodes took: {}[s]".format(time()-start_time))

# start_time = time()
# nodes_2 = [Mesh_1.GetNodeXYZ(n_id) for n_id in node_ids]
# print("\nGetting Nodes with list-comprehension took: {}[s]".format(time()-start_time))

# # for i in range(1,9):
# #     start_time = time()
# #     pool = Pool(i)

# #     # PrintObjectInfo("pool", pool)
# #     node_ids_map = pool.map(GetNodeXYZWrapper, node_ids)
# #     #close the pool and wait for the work to finish
# #     pool.close()
# #     pool.join()
# #     print("\nGetting Nodes with Pool-Map {} took: {}[s]".format(i, time()-start_time))

# # start_time = time()
# # elem_ids = [None] *len(ids_tri)
# # for i, e_id in enumerate(ids_tri):
# #     elem_ids[i] = Mesh_1.GetElemNodes(e_id)
# # print("\nGetting Element Nodes with preallocation took: {}[s]".format(time()-start_time))

# # start_time = time()
# # elem_ids = [Mesh_1.GetElemNodes(e_id) for e_id in ids_tri]
# # print("\nGetting Element Nodes took (using list comprehension): {}[s]".format(time()-start_time))

# start_time = time()
# try:
#     Mesh_1.ExportDAT( r'/home/philipp/Mesh_1.dat' )
# except:
#     print('ExportDAT() failed. Invalid file name?')
# print("\nExporting the Mesh to dat took: {}[s]".format(time()-start_time))

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

in_mem_start_time = time()
# Node Ids
start_time = time()
node_ids = Mesh_1.GetNodesId()
print("\nGetting the NodeIDs took: {}[s]".format(time()-start_time))

# Node Coords
start_time = time()
nodes = [Mesh_1.GetNodeXYZ(n_id) for n_id in node_ids]
print("\nGetting Nodes took: {}[s]".format(time()-start_time))

# Element Ids
start_time = time()
filter_tri = smesh.GetFilter(SMESH.ALL, SMESH.FT_EntityType,'=', SMESH.Entity_Tetra)
ids_tri = Mesh_1.GetIdsFromFilter(filter_tri)
print("\nApplying filter for tetras (=> getting Element Ids) took: {}[s]".format(time()-start_time))

# Element Connectivities
start_time = time()
use_multithreading = True
if use_multithreading:
    pool = Pool(2)
    elem_node_ids = pool.map(GetElemNodesWrapper, ids_tri)
    #close the pool and wait for the work to finish
    pool.close()
    pool.join()
else:
    elem_node_ids = [Mesh_1.GetElemNodes(e_id) for e_id in ids_tri]

print("\nGetting Element Nodes took: {}[s]".format(time()-start_time))

### Creating the Converter Mesh
# Creating the MeshNodes:
start_time = time()
mesh_nodes = [kmc.MeshNode(n_id, n_coords[0], n_coords[1], n_coords[2]) for n_id, n_coords in zip(node_ids, nodes)]
print("\nCreating MeshNodes took: {}[s]".format(time()-start_time))

# Creating the MeshConnectivity:
start_time = time()
mesh_cons = [kmc.MeshConnectivity(e_id, elem_node_ids_list) for e_id, elem_node_ids_list in zip(ids_tri, elem_node_ids)]
print("\nCreating MeshConnectivities took: {}[s]".format(time()-start_time))

in_mem_time = time()-in_mem_start_time
print("\n\tCreating the entities in Memory took: {}[s]".format(in_mem_time))



through_file_start_time = time()

start_time = time()
try:
    Mesh_1.ExportDAT( r'/home/philipp/Mesh_1.dat' )
except:
    print('ExportDAT() failed. Invalid file name?')
print("\nExporting the Mesh to dat took: {}[s]".format(time()-start_time))

start_time = time()
mesh_nodes_2, mesh_cons_2 = ReadDatFile(r'/home/philipp/Mesh_1.dat')
print("\nReading DAT file took: {}[s]".format(time()-start_time))

through_file_time = time()-through_file_start_time
print("\n\tCreating the entities through file took: {}[s]".format(through_file_time))

print("\n\tTime relation: {}".format(in_mem_time/through_file_time))

print("num_nodes_mem: {}; num_nodes_file: {}".format(len(mesh_nodes), len(mesh_nodes_2)))
print("num_cons_mem: {}; num_cons_file: {}".format(len(mesh_cons), len(mesh_cons_2[304])))

assert(len(mesh_nodes) == len(mesh_nodes_2))
assert(len(mesh_cons) == len(mesh_cons_2[304]))



## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(NETGEN_3D.GetAlgorithm(), 'NETGEN 3D')
smesh.SetName(MEFISTO_2D.GetAlgorithm(), 'MEFISTO_2D')
smesh.SetName(Max_Size_1, 'Max Size_1')
smesh.SetName(Mesh_1.GetMesh(), 'Mesh_1')

import numpy # works => good to know

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
