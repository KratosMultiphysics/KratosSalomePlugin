#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.4.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()

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
Face_1 = geompy.MakeFaceHW(100, 100, 1)
Circle_1 = geompy.MakeCircle(None, None, 25)
Partition_1 = geompy.MakePartition([Face_1], [Circle_1], [], [], geompy.ShapeType["FACE"], 0, [], 0)
[support,Face_3] = geompy.ExtractShapes(Partition_1, geompy.ShapeType["FACE"], True)
[Vertex_1,Vertex_2,Vertex_3,Vertex_4,Vertex_5] = geompy.ExtractShapes(Face_3, geompy.ShapeType["VERTEX"], True)
support = geompy.CreateGroup(Face_3, geompy.ShapeType["EDGE"])
geompy.UnionIDs(support, [6])
load1 = geompy.CreateGroup(Face_3, geompy.ShapeType["VERTEX"])
geompy.UnionIDs(load1, [5])
load2 = geompy.CreateGroup(Face_3, geompy.ShapeType["VERTEX"])
geompy.UnionIDs(load2, [9])
shell = geompy.CreateGroup(Face_3, geompy.ShapeType["FACE"])
geompy.UnionIDs(shell, [1])
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Face_1, 'Face_1' )
geompy.addToStudy( Circle_1, 'Circle_1' )
geompy.addToStudy( Partition_1, 'Partition_1' )
geompy.addToStudyInFather( Partition_1, Face_3, 'Face_3' )
geompy.addToStudyInFather( Face_3, support, 'support' )
geompy.addToStudyInFather( Face_3, load1, 'load1' )
geompy.addToStudyInFather( Face_3, load2, 'load2' )
geompy.addToStudyInFather( Face_3, shell, 'shell' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

plate_with_hole = smesh.Mesh(Face_3)
NETGEN_1D_2D = plate_with_hole.Triangle(algo=smeshBuilder.NETGEN_1D2D)
NETGEN_2D_Parameters_1 = NETGEN_1D_2D.Parameters()
NETGEN_2D_Parameters_1.SetSecondOrder( 0 )
NETGEN_2D_Parameters_1.SetOptimize( 1 )
NETGEN_2D_Parameters_1.SetFineness( 2 )
NETGEN_2D_Parameters_1.SetChordalError( -1 )
NETGEN_2D_Parameters_1.SetChordalErrorEnabled( 0 )
NETGEN_2D_Parameters_1.SetUseSurfaceCurvature( 1 )
NETGEN_2D_Parameters_1.SetFuseEdges( 1 )
NETGEN_2D_Parameters_1.SetWorstElemMeasure( 0 )
NETGEN_2D_Parameters_1.SetUseDelauney( 193 )
NETGEN_2D_Parameters_1.SetQuadAllowed( 0 )
NETGEN_2D_Parameters_1.SetMaxSize( 5 )
NETGEN_2D_Parameters_1.SetMinSize( 2.5 )
NETGEN_2D_Parameters_1.SetCheckChartBoundary( 0 )
support_1 = plate_with_hole.GetSubMesh( support, 'support' )
load1_1 = plate_with_hole.GetSubMesh( load1, 'load1' )
load2_1 = plate_with_hole.GetSubMesh( load2, 'load2' )
isDone = plate_with_hole.Compute()


## Set names of Mesh objects
smesh.SetName(NETGEN_1D_2D.GetAlgorithm(), 'NETGEN 1D-2D')
smesh.SetName(NETGEN_2D_Parameters_1, 'NETGEN 2D Parameters_1')
smesh.SetName(load2_1, 'load2')
smesh.SetName(load1_1, 'load1')
smesh.SetName(plate_with_hole.GetMesh(), 'plate_with_hole')
smesh.SetName(support_1, 'support')


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
