#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.3.0 with dump python functionality
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
domain = geompy.MakeBoxDXDYDZ(2, 5, 10)
[dirichlet] = geompy.SubShapes(domain, [31])
[neumann] = geompy.SubShapes(domain, [33])
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )
geompy.addToStudy( domain, 'domain' )
geompy.addToStudyInFather( domain, dirichlet, 'dirichlet' )
geompy.addToStudyInFather( domain, neumann, 'neumann' )

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
Number_of_Segments_1 = Regular_1D.NumberOfSegments(15)
Quadrangle_2D = domain_1.Quadrangle(algo=smeshBuilder.QUADRANGLE)
Hexa_3D = domain_1.Hexahedron(algo=smeshBuilder.Hexa)
isDone = domain_1.Compute()
dirichlet_1 = domain_1.GetSubMesh( dirichlet, 'Sub-mesh_1' )
neumann_1 = domain_1.GetSubMesh( neumann, 'Sub-mesh_2' )
group_0D_entities = domain_1.Add0DElementsToAllNodes( neumann_1, 'group_0D_entities' )


## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Hexa_3D.GetAlgorithm(), 'Hexa_3D')
smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
smesh.SetName(Number_of_Segments_1, 'Number of Segments_1')
smesh.SetName(dirichlet_1, 'dirichlet')
smesh.SetName(neumann_1, 'neumann')
smesh.SetName(domain_1.GetMesh(), 'domain')
smesh.SetName(group_0D_entities, 'group_0D_entities')

# https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
# saving the study such that it can be loaded in Salome
salome.myStudy.SaveAs("Cantilever_Hexa.hdf", False, False) # args: use_multifile, use_acsii

if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()


# from here on using the plugin to create mdpa file
sys.path.append("/home/philippb/software/KratosSalomePlugin/standalone_usage")
import create_kratos_input

mesh_description_3D = { "elements"   : {"Hexa" : {"SmallDisplacementElement3D8N" : 0} } }
mesh_description_0D = { "conditions" : {"0D"   : {"PointLoadCondition3D1N"       : 0} } }

meshes = [
    create_kratos_input.SalomeMesh(domain_1, mesh_description_3D, "domain"),
    create_kratos_input.SalomeMesh(dirichlet_1, {}, "dirichlet"), # no elements / conditions needed
    create_kratos_input.SalomeMesh(group_0D_entities, mesh_description_0D, "neumann")
]

create_kratos_input.CreateMdpaFile(meshes, "cantilever")
