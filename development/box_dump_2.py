#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.4.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/philipp/software/KratosSalomePlugin/development')

###
### GEOM component
###

import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS


geompy = geomBuilder.New()

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
Box_1 = geompy.MakeBoxDXDYDZ(200, 200, 200)
[Face_1,Face_2] = geompy.SubShapes(Box_1, [13, 23])
[Edge_1,Edge_2] = geompy.SubShapes(Box_1, [18, 26])
Group_1 = geompy.CreateGroup(Box_1, geompy.ShapeType["FACE"])
geompy.UnionIDs(Group_1, [33, 31])
Group_2 = geompy.CreateGroup(Box_1, geompy.ShapeType["EDGE"])
geompy.UnionIDs(Group_2, [25, 12, 29, 22])
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Box_1, 'Box_1' )
geompy.addToStudyInFather( Box_1, Face_1, 'Face_1' )
geompy.addToStudyInFather( Box_1, Face_2, 'Face_2' )
geompy.addToStudyInFather( Box_1, Edge_1, 'Edge_1' )
geompy.addToStudyInFather( Box_1, Edge_2, 'Edge_2' )
geompy.addToStudyInFather( Box_1, Group_1, 'Group_1' )
geompy.addToStudyInFather( Box_1, Group_2, 'Group_2' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)


def IsGroupOnGeom(obj):
    return isinstance(obj, SMESH._objref_SMESH_GroupOnGeom)
def IsGroup(obj):
    return isinstance(obj, SMESH._objref_SMESH_Group)
def IsGroupBase(obj):
    return isinstance(obj, SMESH._objref_SMESH_GroupBase)
def IsGroupOnFilter(obj):
    return isinstance(obj, SMESH._objref_SMESH_GroupOnFilter)

def CheckTypes(label, obj):
  print("Checking",         label)
  print("IsGroupBase:",     IsGroupBase(obj))
  print("IsGroup:",         IsGroup(obj))
  print("IsGroupOnGeom:",   IsGroupOnGeom(obj))
  print("IsGroupOnFilter:", IsGroupOnFilter(obj))
  print(obj.GetIDs())
  print(obj.GetListOfID())
  print(obj.GetMeshInfo())
  print()

Mesh_Tetra = smesh.Mesh(Box_1)
Regular_1D = Mesh_Tetra.Segment()
Max_Size_1 = Regular_1D.MaxSize(60)
MEFISTO_2D = Mesh_Tetra.Triangle(algo=smeshBuilder.MEFISTO)
NETGEN_3D = Mesh_Tetra.Tetrahedron()
isDone = Mesh_Tetra.Compute()
Mesh_Hexa = smesh.Mesh(Box_1)
Regular_1D_1 = Mesh_Hexa.Segment()
Number_of_Segments_1 = Regular_1D_1.NumberOfSegments(8,None,[])
Quadrangle_2D = Mesh_Hexa.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Hexa_3D = Mesh_Hexa.Hexahedron(algo=smeshBuilder.Hexa)
isDone = Mesh_Hexa.Compute()
ballElem = Mesh_Tetra.AddBall( 5, 1 )
elem0d = Mesh_Tetra.Add0DElement( 24 )

gbj = Mesh_Tetra.CreateEmptyGroup( SMESH.ELEM0D, 'gbj' )
nbAdd = gbj.Add( [ 1885 ] )
CheckTypes("gbj", gbj)

standalone = Mesh_Tetra.CreateEmptyGroup( SMESH.VOLUME, 'standalone' )
nbAdd = standalone.Add( [ 1068, 1661, 1772 ] )
CheckTypes("standalone", standalone)

Group_3 = Mesh_Tetra.GroupOnGeom(Face_2,'Group_3',SMESH.NODE)
Edge_2_1 = Mesh_Tetra.GroupOnGeom(Edge_2,'Edge_2',SMESH.EDGE)
Edge_2_2 = Mesh_Tetra.GroupOnGeom(Edge_2,'Edge_2',SMESH.NODE)
CheckTypes("Group_3", Group_3)
CheckTypes("Edge_2_1", Edge_2_1)
CheckTypes("Edge_2_2", Edge_2_2)

aCriteria = []
aCriterion = smesh.GetCriterion(SMESH.EDGE,SMESH.FT_Length,SMESH.FT_LessThan,150)
aCriteria.append(aCriterion)
aFilter_1 = smesh.GetFilterFromCriteria(aCriteria)
aFilter_1.SetMesh(Mesh_Tetra.GetMesh())
Group_4 = Mesh_Tetra.GroupOnFilter( SMESH.EDGE, 'Group_4', aFilter_1 )
CheckTypes("Group_4", Group_4)

Sub_mesh_1 = Mesh_Tetra.GetSubMesh( Face_1, 'Sub-mesh_1' )
Sub_mesh_2 = Mesh_Tetra.GetSubMesh( Face_2, 'Sub-mesh_2' )
Sub_mesh_3 = Mesh_Tetra.GetSubMesh( Edge_1, 'Sub-mesh_3' )
Sub_mesh_4 = Mesh_Tetra.GetSubMesh( Edge_2, 'Sub-mesh_4' )
Sub_mesh_5 = Mesh_Tetra.GetSubMesh( Group_1, 'Sub-mesh_5' )
Sub_mesh_6 = Mesh_Tetra.GetSubMesh( Group_2, 'Sub-mesh_6' )
Sub_mesh_7 = Mesh_Hexa.GetSubMesh( Face_1, 'Sub-mesh_7' )
Sub_mesh_8 = Mesh_Hexa.GetSubMesh( Face_2, 'Sub-mesh_8' )
Sub_mesh_9 = Mesh_Hexa.GetSubMesh( Edge_1, 'Sub-mesh_9' )
Sub_mesh_10 = Mesh_Hexa.GetSubMesh( Edge_2, 'Sub-mesh_10' )
Sub_mesh_11 = Mesh_Hexa.GetSubMesh( Group_1, 'Sub-mesh_11' )
Sub_mesh_12 = Mesh_Hexa.GetSubMesh( Group_2, 'Sub-mesh_12' )


## Set names of Mesh objects
smesh.SetName(gbj, 'gbj')
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(NETGEN_3D.GetAlgorithm(), 'NETGEN 3D')
smesh.SetName(MEFISTO_2D.GetAlgorithm(), 'MEFISTO_2D')
smesh.SetName(Hexa_3D.GetAlgorithm(), 'Hexa_3D')
smesh.SetName(Number_of_Segments_1, 'Number of Segments_1')
smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
smesh.SetName(Max_Size_1, 'Max Size_1')
smesh.SetName(Sub_mesh_1, 'Sub-mesh_1')
smesh.SetName(Sub_mesh_8, 'Sub-mesh_8')
smesh.SetName(Sub_mesh_2, 'Sub-mesh_2')
smesh.SetName(Sub_mesh_11, 'Sub-mesh_11')
smesh.SetName(Sub_mesh_7, 'Sub-mesh_7')
smesh.SetName(Sub_mesh_12, 'Sub-mesh_12')
smesh.SetName(Mesh_Tetra.GetMesh(), 'Mesh_Tetra')
smesh.SetName(Mesh_Hexa.GetMesh(), 'Mesh_Hexa')
smesh.SetName(Sub_mesh_9, 'Sub-mesh_9')
smesh.SetName(Sub_mesh_10, 'Sub-mesh_10')
smesh.SetName(Sub_mesh_6, 'Sub-mesh_6')
smesh.SetName(Sub_mesh_5, 'Sub-mesh_5')
smesh.SetName(standalone, 'standalone')
smesh.SetName(Edge_2_1, 'Edge_2')
smesh.SetName(Group_4, 'Group_4')
smesh.SetName(Edge_2_2, 'Edge_2')
smesh.SetName(Group_3, 'Group_3')
smesh.SetName(Sub_mesh_4, 'Sub-mesh_4')
smesh.SetName(Sub_mesh_3, 'Sub-mesh_3')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
