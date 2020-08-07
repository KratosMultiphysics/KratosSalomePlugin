#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.5.0 with dump python functionality
###

import sys
import salome

salome.salome_init()

from salome import myStudy

myStudy.Clear()
myStudy.Init()

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


def CreateVerticesFromCoords(coords_list):
    return [geompy.MakeVertex(*coords) for coords in coords_list]

def CreateEdgeGroups(father, groups_definition):
    groups = {}
    for name, ids in groups_definition.items():
        new_group = geompy.CreateGroup(father, geompy.ShapeType["EDGE"])
        geompy.UnionIDs(new_group, ids)
        groups[name] = new_group
    return groups

def AddGroupsToFatherStudy(father, groups):
    for name, group in groups.items():
        geompy.addToStudyInFather(father, group, name)

# coordinates of the corners of the interface and the structural domain
interface_coords = [
    (0.4965, 0, 0),
    (0.4965, 0.25, 0),
    (0.5015, 0.25, 0),
    (0.5015, 0, 0)
]

# coordinates of the corners of the fluid domain
fluid_domain_coords = [
    (0, 0, 0),
    (0, 0.5, 0),
    (1.75, 0.5, 0),
    (1.75, 0.3, 0),
    (1.4, 0.3, 0)
]

# create vertices from the coordinates
interface_vertices = CreateVerticesFromCoords(interface_coords)
fluid_domain_vertices = CreateVerticesFromCoords(fluid_domain_coords)

# create interface
interface = geompy.MakePolyline([interface_vertices[0], interface_vertices[1], interface_vertices[2], interface_vertices[3]])

# create fluid boundaries
fluid_inlet = geompy.MakePolyline([fluid_domain_vertices[0], fluid_domain_vertices[1]])
fluid_outlet = geompy.MakePolyline([fluid_domain_vertices[2], fluid_domain_vertices[3]])
fluid_top = geompy.MakePolyline([fluid_domain_vertices[1], fluid_domain_vertices[2]])
fluid_bottom_left = geompy.MakePolyline([fluid_domain_vertices[0], interface_vertices[0]])
fluid_bottom_right = geompy.MakePolyline([fluid_domain_vertices[3], fluid_domain_vertices[4], interface_vertices[3]])
fluid_bottom_right_with_fillet = geompy.MakeFillet1D(fluid_bottom_right, 0.3, [4])

# create structure boundary
structure_bottom = geompy.MakePolyline([interface_vertices[0], interface_vertices[3]])

# create fluid domain
fluid_domain = geompy.MakeFaceWires([fluid_inlet, fluid_outlet, fluid_top, fluid_bottom_left, fluid_bottom_right_with_fillet, interface], 1)

# create fluid groups
fluid_groups_definitions = {
    "inlet" : [3],
    "outlet" : [8],
    "top" : [6],
    "bottom" : [10,12,14,22],
    "interface" : [16,18,20]
}

fluid_groups = CreateEdgeGroups(fluid_domain, fluid_groups_definitions)

# create structure domain
structure_domain = geompy.MakeFaceWires([interface, structure_bottom], 1)

# create structure groups
structure_groups_definitions = {
    "bottom" : [10],
    "interface" : [3, 6, 8]
}

structure_groups = CreateEdgeGroups(structure_domain, structure_groups_definitions)


# adding models to the study
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )

folder_interface_vertices = geompy.NewFolder("interface_vertices")
for i, v_f in enumerate(interface_vertices):
    geompy.addToStudy( v_f, f'Vertex_interface_{i}' )
    geompy.PutToFolder(v_f, folder_interface_vertices)

folder_fluid_domain_vertices = geompy.NewFolder("fluid_domain_vertices")
for i, v_f in enumerate(fluid_domain_vertices):
    geompy.addToStudy( v_f, f'Vertex_fluid_{i}' )
    geompy.PutToFolder(v_f, folder_fluid_domain_vertices)

geompy.addToStudy( fluid_inlet, "fluid_inlet" )
geompy.addToStudy( fluid_outlet, "fluid_outlet" )
geompy.addToStudy( fluid_top, "fluid_top" )
geompy.addToStudy( fluid_bottom_left, "fluid_bottom_left" )
geompy.addToStudy( fluid_bottom_right_with_fillet, "fluid_bottom_right" )
geompy.addToStudy( interface, "interface" )
geompy.addToStudy( structure_bottom, "structure_bottom" )

geompy.addToStudy( fluid_domain, "fluid_domain" )
AddGroupsToFatherStudy(fluid_domain, fluid_groups)

geompy.addToStudy( structure_domain, "structure_domain" )
AddGroupsToFatherStudy(structure_domain, structure_groups)



if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
