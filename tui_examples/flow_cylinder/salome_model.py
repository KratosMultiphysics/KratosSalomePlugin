#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.4.0 with dump python functionality
###

import sys
import salome

salome.salome_init()
import salome_notebook
notebook = salome_notebook.NoteBook()
sys.path.insert(0, r'/home/philipp/software/KratosSalomePlugin/tui_examples/flow_cylinder')

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
Vertex_1 = geompy.MakeVertex(0, 0, 0)
Vertex_2 = geompy.MakeVertex(7, 0, 0)
Vertex_3 = geompy.MakeVertex(7, 2, 0)
Vertex_4 = geompy.MakeVertex(0, 2, 0)
Vertex_5 = geompy.MakeVertex(2.5, 1, 0)
Vertex_6 = geompy.MakeVertex(1.5, 0.5, 0)
Vertex_7 = geompy.MakeVertex(1.5, 1.5, 0)
Vertex_8 = geompy.MakeVertex(5, 0.5, 0)
Vertex_9 = geompy.MakeVertex(5, 1.5, 0)
Circle_1 = geompy.MakeCircle(Vertex_5, None, 0.15)
outer_boundary = geompy.MakePolyline([Vertex_1, Vertex_4, Vertex_3, Vertex_2], True)
inner_boundary = geompy.MakePolyline([Vertex_6, Vertex_7, Vertex_9, Vertex_8], True)
Face_1 = geompy.MakeFaceWires([Circle_1, outer_boundary], 1)
domain = geompy.MakePartition([Face_1], [inner_boundary], [], [], geompy.ShapeType["FACE"], 0, [], 0)
[domain_inner] = geompy.SubShapes(domain, [21])
[outlet,inlet,cyl_boundary] = geompy.SubShapes(domain, [11, 4, 24])
walls = geompy.CreateGroup(domain, geompy.ShapeType["EDGE"])
geompy.UnionIDs(walls, [7, 9])
boundary_inner = geompy.CreateGroup(domain, geompy.ShapeType["EDGE"])
geompy.UnionIDs(boundary_inner, [20, 18, 13, 16])
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( Vertex_1, 'Vertex_1' )
geompy.addToStudy( Vertex_2, 'Vertex_2' )
geompy.addToStudy( Vertex_3, 'Vertex_3' )
geompy.addToStudy( Vertex_4, 'Vertex_4' )
geompy.addToStudy( Vertex_5, 'Vertex_5' )
geompy.addToStudy( Vertex_6, 'Vertex_6' )
geompy.addToStudy( Vertex_7, 'Vertex_7' )
geompy.addToStudy( Vertex_8, 'Vertex_8' )
geompy.addToStudy( Vertex_9, 'Vertex_9' )
geompy.addToStudyInFather( domain, inlet, 'inlet' )
geompy.addToStudy( outer_boundary, 'outer_boundary' )
geompy.addToStudyInFather( domain, domain_inner, 'domain_inner' )
geompy.addToStudyInFather( domain, outlet, 'outlet' )
geompy.addToStudy( Circle_1, 'Circle_1' )
geompy.addToStudy( Face_1, 'Face_1' )
geompy.addToStudy( inner_boundary, 'inner_boundary' )
geompy.addToStudy( domain, 'domain' )
geompy.addToStudyInFather( domain, cyl_boundary, 'cyl_boundary' )
geompy.addToStudyInFather( domain, boundary_inner, 'boundary_inner' )
geompy.addToStudyInFather( domain, walls, 'walls' )

###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()
#smesh.SetEnablePublish( False ) # Set to False to avoid publish in study if not needed or in some particular situations:
                                 # multiples meshes built in parallel, complex and numerous mesh edition (performance)

domain_1 = smesh.Mesh(domain)
Regular_1D = domain_1.Segment()
Max_Size_domain = Regular_1D.MaxSize(0.728011)
MEFISTO_2D = domain_1.Triangle(algo=smeshBuilder.MEFISTO)
Regular_1D_1 = domain_1.Segment(geom=domain_inner)
mesh_domain_inner = Regular_1D_1.GetSubMesh()
Max_Size_domain_inner = Regular_1D_1.MaxSize(0.05)
MEFISTO_2D_1 = domain_1.Triangle(algo=smeshBuilder.MEFISTO,geom=domain_inner)
Regular_1D_2 = domain_1.Segment(geom=inlet)
Local_Length_outter_boundary = Regular_1D_2.LocalLength(0.1,None,1e-07)
Regular_1D_3 = domain_1.Segment(geom=outlet)
status = domain_1.AddHypothesis(Local_Length_outter_boundary,outlet)
Regular_1D_4 = domain_1.Segment(geom=walls)
status = domain_1.AddHypothesis(Local_Length_outter_boundary,walls)
Regular_1D_5 = domain_1.Segment(geom=cyl_boundary)
Local_Length_cyl = Regular_1D_5.LocalLength(0.03,None,1e-07)
Regular_1D_6 = domain_1.Segment(geom=boundary_inner)
smeshObj_1 = Regular_1D_6.GetSubMesh()
#status = domain_1.AddHypothesis(smeshObj_2,boundary_inner) ### smeshObj_2 has not been yet created
isDone = domain_1.SetMeshOrder( [ [ smeshObj_1, mesh_domain_inner ] ])
Max_Size_domain.SetLength( 0.75 )
Max_Size_domain_inner.SetLength( 0.06 )
Local_Length_cyl.SetLength( 0.025 )
Local_Length_cyl.SetPrecision( 1e-07 )
domain_1.GetMesh().RemoveSubMesh( smeshObj_1 )
status = domain_1.RemoveHypothesis(MEFISTO_2D)
NETGEN_2D = domain_1.Triangle(algo=smeshBuilder.NETGEN_2D)
isDone = domain_1.Compute()
mesh_inlet = Regular_1D_2.GetSubMesh()
mesh_outlet = Regular_1D_3.GetSubMesh()
mesh_walls = Regular_1D_4.GetSubMesh()
mesh_cyl_boundary = Regular_1D_5.GetSubMesh()

## some objects were removed
aStudyBuilder = salome.myStudy.NewBuilder()
SO = salome.myStudy.FindObjectIOR(salome.myStudy.ConvertObjectToIOR(smeshObj_1))
if SO: aStudyBuilder.RemoveObjectWithChildren(SO)

## Set names of Mesh objects
smesh.SetName(mesh_domain_inner, 'mesh_domain_inner')
smesh.SetName(mesh_walls, 'mesh_walls')
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(MEFISTO_2D.GetAlgorithm(), 'MEFISTO_2D')
smesh.SetName(NETGEN_2D.GetAlgorithm(), 'NETGEN 2D')
smesh.SetName(domain_1.GetMesh(), 'domain')
smesh.SetName(Local_Length_outter_boundary, 'Local Length_outter_boundary')
smesh.SetName(Max_Size_domain_inner, 'Max Size_domain_inner')
smesh.SetName(Max_Size_domain, 'Max Size_domain')
smesh.SetName(Local_Length_cyl, 'Local Length_cyl')
smesh.SetName(mesh_outlet, 'mesh_outlet')
smesh.SetName(mesh_cyl_boundary, 'mesh_cyl_boundary')
smesh.SetName(mesh_inlet, 'mesh_inlet')


# https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
# saving the study such that it can be loaded in Salome
salome.myStudy.SaveAs("flow_cylinder.hdf", False, False) # args: use_multifile, use_acsii

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()


# from here on using the plugin to create mdpa file
sys.path.append("../../") # adding root folder of plugin to path
import create_kratos_input_tui

mesh_description_domain = { "elements"   : {"Triangle" : {"Element2D3N" : 0} } }
mesh_description_wall   = { "conditions" : {"Edge"     : {"WallCondition2D2N" : 0} } }

meshes = [
    create_kratos_input_tui.SalomeMesh(domain_1, mesh_description_domain, "domain"),
    create_kratos_input_tui.SalomeMesh(mesh_inlet, mesh_description_wall, "inlet"),
    create_kratos_input_tui.SalomeMesh(mesh_outlet, mesh_description_wall, "outlet"),
    create_kratos_input_tui.SalomeMesh(mesh_walls, mesh_description_wall, "walls"),
    create_kratos_input_tui.SalomeMesh(mesh_cyl_boundary, mesh_description_wall, "cyl_boundary"),
]

create_kratos_input_tui.CreateMdpaFile(meshes, "flow_cylinder")
