#!/usr/bin/env python

###
### This file is generated automatically by SALOME v9.5.0 with dump python functionality
###

mesh_size_fluid_domain = 0.05

mesh_sizes_fluid = {
    "inlet" : 0.05,
    "outlet" : 0.05,
    "top" : 0.05,
    "bottom" : 0.05,
    "interface" : 0.015
}

mesh_sizes_structure = {
    "top_bottom" : 0.002,
    "left_right" : 0.02
}

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
    (1.3, 0.3, 0)
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
fluid_bottom_right_with_fillet = geompy.MakeFillet1D(fluid_bottom_right, 1, [4])

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
    "interface" : [3, 6, 8],
    "top_bottom" : [6, 10],
    "left_right" : [3, 8]
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


###
### SMESH component
###

import  SMESH, SALOMEDS
from salome.smesh import smeshBuilder

smesh = smeshBuilder.New()

# create fluid mesh
fluid_mesh = smesh.Mesh(fluid_domain)
NETGEN_2D_Parameters = smesh.CreateHypothesisByAverageLength( 'NETGEN_Parameters_2D', 'NETGENEngine', mesh_size_fluid_domain, 0 )
NETGEN_1D_2D = fluid_mesh.Triangle(algo=smeshBuilder.NETGEN_1D2D)
fluid_mesh.AddHypothesis( fluid_domain, NETGEN_2D_Parameters )

fluid_sub_meshes = {}
for name, group in  fluid_groups.items():
    mesh_size = mesh_sizes_fluid[name]

    mesh_algorithm = fluid_mesh.Segment(geom=group)
    local_length = mesh_algorithm.LocalLength(mesh_size,None,1e-07)
    smesh.SetName(local_length, f"local_length_fluid_{name}")

    fluid_sub_meshes[name] = mesh_algorithm.GetSubMesh()

is_done_fluid = fluid_mesh.Compute()
if not is_done_fluid:
    raise Exception("Fluid mesh could not be computed!")

# create structure mesh
structure_mesh = smesh.Mesh(structure_domain)
Quadrangle_2D_2 = structure_mesh.Quadrangle(algo=smeshBuilder.QUADRANGLE)

structure_sub_meshes = {}
for name, mesh_size in  mesh_sizes_structure.items():
    group = structure_groups[name]
    mesh_algorithm = structure_mesh.Segment(geom=group)
    local_length = mesh_algorithm.LocalLength(mesh_size,None,1e-07)
    smesh.SetName(local_length, f"local_length_structure_{name}")

    structure_sub_meshes[name] = mesh_algorithm.GetSubMesh()

for name, group in structure_groups.items():
    # adding groups that don't have an explicit mesh but use the existing one
    if name in mesh_sizes_structure:
        continue

    structure_sub_meshes[name] = structure_mesh.GetSubMesh(group, name)

is_done_structure = structure_mesh.Compute()
if not is_done_structure:
    raise Exception("Structure mesh could not be computed!")

# TODO this should be done automatically!
aCriterion = [smesh.GetCriterion(SMESH.ALL,SMESH.FT_EntityType,'=',SMESH.Entity_Quadrangle)]
isDone = structure_mesh.ReorientObject( structure_mesh )

## Set names of Mesh objects
smesh.SetName(NETGEN_1D_2D.GetAlgorithm(), 'NETGEN 1D-2D')
smesh.SetName(fluid_mesh.GetMesh(), 'fluid_mesh')
for name, sub_mesh in fluid_sub_meshes.items():
    smesh.SetName(sub_mesh, name)

smesh.SetName(Quadrangle_2D_2, 'Quadrangle_2D_2')
smesh.SetName(structure_mesh.GetMesh(), 'structure_mesh')
for name, sub_mesh in structure_sub_meshes.items():
    smesh.SetName(sub_mesh, name)


# from here on using the plugin to create mdpa file
sys.path.append("../../") # adding root folder of plugin to path
import create_kratos_input_tui
from kratos_salome_plugin.write_mdpa import WriteMdpa

# fluid mesh
fluid_mesh_description_domain = { "elements"   : {"Triangle" : {"Element2D3N"       : 1} } }
fluid_mesh_description_wall   = { "conditions" : {"Edge"     : {"WallCondition2D2N" : 0} } }

meshes_fl = [
    create_kratos_input_tui.SalomeMesh(fluid_mesh, fluid_mesh_description_domain, "Parts_Fluid")
]

for name, sub_mesh in fluid_sub_meshes.items():
    meshes_fl.append(create_kratos_input_tui.SalomeMesh(sub_mesh, fluid_mesh_description_wall, name))

model_part_fluid = create_kratos_input_tui.CreateModelPart(meshes_fl)
props = model_part_fluid.GetProperties(1)
props.SetValue("DENSITY", 956.0)
props.SetValue("DYNAMIC_VISCOSITY", 0.145)

mdpa_info_fluid = "mdpa for fluid model FSI Mok"
WriteMdpa(model_part_fluid, "Mok_CFD", mdpa_info_fluid)

# structure mesh
structure_mesh_description_domain = { "elements" : {"Quadrangle" : {"TotalLagrangianElement2D4N" : 0} } }

meshes_str = [
    create_kratos_input_tui.SalomeMesh(structure_mesh, structure_mesh_description_domain, "Parts_Structure")
]

for name, sub_mesh in structure_sub_meshes.items():
    meshes_str.append(create_kratos_input_tui.SalomeMesh(sub_mesh, {}, name))

model_part_structure = create_kratos_input_tui.CreateModelPart(meshes_str)


# Creating PointLoad Conditions
conditions_smp = model_part_structure.CreateSubModelPart("point_load_conditions")
conditions_smp.AddNodes([node.Id for node in model_part_structure.GetSubModelPart("interface").Nodes])
props = model_part_structure.GetProperties(0)
for i, node in enumerate(model_part_structure.GetSubModelPart("interface").Nodes):
    conditions_smp.CreateNewCondition("PointLoadCondition3D1N", i+1, [node.Id], props)

mdpa_info_structure = "mdpa for structure model FSI Mok"
WriteMdpa(model_part_structure, "Mok_CSM", mdpa_info_structure)


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()
