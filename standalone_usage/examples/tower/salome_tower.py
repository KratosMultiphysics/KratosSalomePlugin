# taken from: https://www.salome-platform.org/user-section/tui-examples

import salome
salome.salome_init()

#########################################
#
# Tower Geometry
#
#########################################

import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()
import math

# global coordinate system
OO = geompy.MakeVertex(0, 0, 0)
Ox = geompy.MakeVectorDXDYDZ(1, 0, 0)
Oy = geompy.MakeVectorDXDYDZ(0, 1, 0)
Oz = geompy.MakeVectorDXDYDZ(0, 0, 1)
global_CS = geompy.MakeMarker(0,0,0, 1,0,0, 0,1,0) # OO, Ox, Oy

Oxy = geompy.MakeVectorDXDYDZ(1, 1, 0)

pln_YOZ = geompy.MakePlane(OO, Ox, 200.0)
pln_Oxy = geompy.MakePlane(OO, Oxy, 200.0)

geompy.addToStudy(OO, "OO" )
geompy.addToStudy(Ox, "Ox" )
geompy.addToStudy(Oy, "Oy" )
geompy.addToStudy(Oz, "Oz" )
geompy.addToStudy(global_CS, "global_CS" )
geompy.addToStudy(Oxy, "Oxy" )
geompy.addToStudy(pln_YOZ, "pln_YOZ" )
geompy.addToStudy(pln_Oxy, "pln_Oxy" )

# tower parameters
thickness   = 10.0 # thickness of tower walls

size_arc    = 30.0 # size of lower arc block along front
size_corner = 40.0 # size of corner block along front

# tower wall angle
tg_betta  = 0.0
ctg_betta = 0.0
sin_betta = 0.0
cos_betta = 0.0
def SetBetta(hh, ww):
	global tg_betta, ctg_betta, sin_betta, cos_betta
	tg_betta  = hh / ww
	ctg_betta = ww / hh
	sin_betta = tg_betta / math.sqrt(1.0 + tg_betta*tg_betta)
	cos_betta = 1.0      / math.sqrt(1.0 + tg_betta*tg_betta)
	pass

# arc
def MakeArcs (a_width, a_height, nb_segm):
	arcs = []

	w_arc = a_width
	h_arc = a_height
	r_arc = 0.0
	dca   = 0.0

	alpha = math.pi/8.0

	if h_arc > 0.01:
		r_arc = h_arc / (1.0 - math.sin(alpha))
		dca   = r_arc * math.sin(alpha)
		w_arc = r_arc * math.cos(alpha)
	else:
		r_arc = w_arc / math.cos(alpha)
		dca   = r_arc * math.sin(alpha)
		h_arc = r_arc - dca
		pass

	alpha_3_4 = alpha * 3.0 / nb_segm

	ax_arc = geompy.MakeTranslation(Oz, 0, -dca, 0)

	pa_0 = geompy.MakeVertex(r_arc, -dca, 0)
	pa_1 = geompy.MakeRotation(pa_0, ax_arc, alpha)
	pa_1_c = geompy.MakeRotation(pa_1, ax_arc, alpha_3_4/2.0)
	pa_2 = geompy.MakeRotation(pa_1, ax_arc, alpha_3_4)

	arc_1 = geompy.MakeArc(pa_1, pa_1_c, pa_2)
	arcs.append(arc_1)

	for ii in range(nb_segm - 1):
		arc_ii = geompy.MakeRotation(arc_1, ax_arc, alpha_3_4*(ii+1))
		arcs.append(arc_ii)
		pass

	return [arcs, w_arc, h_arc, r_arc]

def BuildFloor (floor_index, z0, a_width, a_height, nb_segm_vert, nb_segm_hori):
	# 1. Build arc points in global coordinate system
	nb_arc = nb_segm_vert + nb_segm_hori
	[arcs, w_arc, h_arc, ra] = MakeArcs(a_width, a_height, nb_arc)

	w_mid  = w_arc + size_arc    # start point for wall between arc and corner
	width  = w_mid + size_corner # tower half width at floor basement
	height = (h_arc + size_arc + size_corner) * sin_betta # height of tower floor

	dxy = height/nb_segm_vert * ctg_betta

	# 2. Create local CS for arc
	arc_CS = geompy.MakeMarker(0,-width,z0, 1,0,0, 0,1,tg_betta) # OO, Ox, Oy
	geompy.addToStudy(arc_CS, "arc_" + str(floor_index) + "_CS" )

	# 3. Build faces
	arc_faces = []
	f_ind = 1
	for arc in arcs:
		# 2.2. Position arc on its real place
		arc_real = geompy.MakePosition(arc, global_CS, arc_CS)
		# 2.3. Build face
		face_arc = geompy.MakePrismVecH(arc_real, Oy, thickness)
		arc_faces.append(face_arc)
		f_ind += 1
		pass

	# 4. Build corner and middle points
	pc1 = geompy.MakeVertex(width, -width, z0)
	pc1_inside = geompy.MakeTranslation(pc1, -thickness, thickness, 0)

	pm1 = geompy.MakeVertex(w_mid, -width, z0)
	pm1_inside = geompy.MakeTranslation(pm1, 0, thickness, 0)

	corner_pts        = [pc1]
	corner_pts_inside = [pc1_inside]
	middle_pts        = [pm1]
	middle_pts_inside = [pm1_inside]

	dh = height/nb_segm_vert

	for ii in range(nb_segm_vert):
		pc_ii_1        = geompy.MakeTranslation(corner_pts[ii]       , -dxy, dxy, dh)
		pm_ii_1        = geompy.MakeTranslation(middle_pts[ii]       , -dxy, dxy, dh)
		pc_ii_1_inside = geompy.MakeTranslation(corner_pts_inside[ii], -dxy, dxy, dh)
		pm_ii_1_inside = geompy.MakeTranslation(middle_pts_inside[ii], -dxy, dxy, dh)

		corner_pts.append(pc_ii_1)
		middle_pts.append(pm_ii_1)
		corner_pts_inside.append(pc_ii_1_inside)
		middle_pts_inside.append(pm_ii_1_inside)
		pass

	xy_corner_top = width - nb_segm_vert*dxy
	xy_corner_top_inside = xy_corner_top - thickness

	xy_mid_top = xy_corner_top - size_corner
	xy_arc_top = xy_mid_top - size_arc

	he_glob = z0 + height

	dw = xy_arc_top/(nb_segm_hori - 1)
	xx = xy_arc_top
	for ii in range(nb_segm_hori):
		pm        = geompy.MakeVertex(xx, -xy_corner_top       , he_glob)
		pm_inside = geompy.MakeVertex(xx, -xy_corner_top_inside, he_glob)

		middle_pts.append(pm)
		middle_pts_inside.append(pm_inside)

		xx -= dw
		pass

	# 5. Build corner and middle faces
	fcs = []
	for ii in range(nb_segm_vert):
		fc_ii = geompy.MakeQuad4Vertices(corner_pts[ii]  , corner_pts_inside[ii],
						 corner_pts[ii+1], corner_pts_inside[ii+1])
		fcs.append(fc_ii)
		pass

	fms = []
	for ii in range(nb_arc):
		fm_ii = geompy.MakeQuad4Vertices(middle_pts[ii]  , middle_pts_inside[ii],
						 middle_pts[ii+1], middle_pts_inside[ii+1])
		fms.append(fm_ii)
		pass

	# 6. Build blocks
	bcms = []
	for ii in range(nb_segm_vert):
		bcm_ii = geompy.MakeHexa2Faces(fms[ii], fcs[ii])
		bcms.append(bcm_ii)
		pass

	bmas = []
	for ii in range(nb_arc):
		bma_ii = geompy.MakeHexa2Faces(fms[ii], arc_faces[ii])
		bmas.append(bma_ii)
		pass

	# gather blocks
	floor_blocks = bcms + bmas

	# fill top faces
	xy_corner_top_center = xy_corner_top - thickness/2.0
	p_corner_top_center = geompy.MakeVertex(xy_corner_top_center - size_corner/2.0,
						- xy_corner_top_center, he_glob)
	top_corner_face = geompy.GetFaceNearPoint(bcms[nb_segm_vert - 1], p_corner_top_center)

	top_faces = [top_corner_face, fms[nb_segm_vert]]

	return [w_arc, w_mid, width, height, floor_blocks, top_faces]

# floor 1
SetBetta(30.0, 10.0)
nb_segm_vert_1 = 4
nb_segm_hori_1 = 4
z0_1 = 0.0
[w_arc_1, w_mid_1, width_1, height_1,
 blocks_1, top_faces_1] = BuildFloor(1, z0_1, 0.0, 300.0, nb_segm_vert_1, nb_segm_hori_1)

w_arc_1_top = w_arc_1 - height_1 * ctg_betta

# floor 2
SetBetta(30.0, 8.5)

height_pre_2 = height_1 * 0.5
dxy_pre_2 = height_pre_2 * ctg_betta
w_arc2 = w_arc_1_top - dxy_pre_2

blocks_pre_2 = []
for top_face in top_faces_1:
	opposite = geompy.MakeTranslation(top_face, - dxy_pre_2, dxy_pre_2, height_pre_2)
	block = geompy.MakeHexa2Faces(top_face, opposite)
	blocks_pre_2.append(block)
	pass

nb_segm_vert_2 = 3
nb_segm_hori_2 = 3
z0_2 = z0_1 + height_1 + height_pre_2
[w_arc_2, w_mid_2, width_2, height_2,
 blocks_2, top_faces_2] = BuildFloor(2, z0_2, w_arc2, 0.0, nb_segm_vert_2, nb_segm_hori_2)

w_arc_2_top = w_arc_2 - height_2 * ctg_betta

# floor 3
SetBetta(30.0, 7.0)

height_pre_3 = height_2 * 1.0
dxy_pre_3 = height_pre_3 * ctg_betta
w_arc3 = w_arc_2_top - dxy_pre_3

blocks_pre_3 = []
for top_face in top_faces_2:
	opposite = geompy.MakeTranslation(top_face, - dxy_pre_3, dxy_pre_3, height_pre_3)
	block = geompy.MakeHexa2Faces(top_face, opposite)
	blocks_pre_3.append(block)
	pass

nb_segm_vert_3 = 2
nb_segm_hori_3 = 2
z0_3 = z0_2 + height_2 + height_pre_3
[w_arc_3, w_mid_3, width_3, height_3,
 blocks_3, top_faces_3] = BuildFloor(3, z0_3, w_arc3, 0.0, nb_segm_vert_3, nb_segm_hori_3)

w_arc_3_top = w_arc_3 - height_3 * ctg_betta

# floor 4
SetBetta(30.0, 6.0)

height_pre_4 = (height_3 + height_pre_3) * 0.6
nb_segm_pre_4 = 6
dh_pre_4 = height_pre_4/nb_segm_pre_4
dxy_pre_4 = dh_pre_4 * ctg_betta
z0_4 = z0_3 + height_3

blocks_pre_4 = []
for top_face in top_faces_3:
	opposite = geompy.MakeTranslation(top_face, - dxy_pre_4, dxy_pre_4, dh_pre_4)
	block = geompy.MakeHexa2Faces(top_face, opposite)
	ind = geompy.LocalOp.GetSubShapeIndex(block, top_face)
	block123 = geompy.MakeMultiTransformation1D(block, ind, 0, nb_segm_pre_4)
	blocks_pre_4.append(block123)
	pass

comp_blocks_pre_4 = geompy.MakeCompound(blocks_pre_4)

w_arc4 = w_arc_3_top - height_pre_4 * ctg_betta
yy_4 = w_arc4 + size_arc + size_corner
z0_5 = z0_4 + height_pre_4

pp = geompy.MakeVertex(w_arc4 + dxy_pre_4/2.0, -yy_4 - dxy_pre_4/2.0 + thickness/2.0, z0_5 - dh_pre_4/2.0)
top_arc_side_face = geompy.GetFaceNearPoint(comp_blocks_pre_4, pp)

nb_segm_arc_4 = int(math.floor(w_arc4/size_arc))
if nb_segm_arc_4 < 2:
	print("Invalid parameters: too small 4th floor")
	nb_segm_arc_4 = 2
	pass

opposite = geompy.MakeTranslation(top_arc_side_face, -w_arc4/nb_segm_arc_4, 0, 0)
block = geompy.MakeHexa2Faces(top_arc_side_face, opposite)
ind = geompy.LocalOp.GetSubShapeIndex(block, top_arc_side_face)
block123 = geompy.MakeMultiTransformation1D(block, ind, 0, nb_segm_arc_4 - 1)
blocks_pre_4.append(block123)

pp = geompy.MakeTranslation(pp, -w_arc4*(nb_segm_arc_4 - 1)/nb_segm_arc_4, 0, 0)
face_x0_opp = geompy.GetFaceNearPoint(block123, pp)

pp1 = geompy.MakeVertex(0, -yy_4, z0_5)
pp2 = geompy.MakeVertex(0, -yy_4 + thickness, z0_5)
pp3 = geompy.MakeVertex(0, -yy_4 + thickness - dxy_pre_4, z0_5 - dh_pre_4)
pp4 = geompy.MakeVertex(0, -yy_4 - dxy_pre_4, z0_5 - dh_pre_4)
face_x0 = geompy.MakeQuad4Vertices(pp1, pp2, pp3, pp4)

block = geompy.MakeHexa2Faces(face_x0_opp, face_x0)
blocks_pre_4.append(block)

comp_blocks_pre_4 = geompy.MakeCompound(blocks_pre_4)
geompy.addToStudy(comp_blocks_pre_4, "comp_blocks_pre_4")

# floor 4'
blocks_4_ = []
pnt1 = geompy.MakeVertex(0, 0, z0_5)
pnt2 = geompy.MakeVertex(0, 0, z0_5 + 1)
anAx1 = geompy.MakeVector(pnt1, pnt2)
faces_4_ = geompy.GetShapesOnPlane(comp_blocks_pre_4, geompy.ShapeType["FACE"], anAx1, GEOM.ST_ON)
for ff in faces_4_:
	block_4_ = geompy.MakePrismVecH(ff, Oz, thickness)
	blocks_4_.append(block_4_)
	pass

# floor 5
dxy_5 = []
for ii in range(nb_segm_arc_4):
	dxy_5.append(w_arc4/nb_segm_arc_4)
	pass

dxy_5 += [size_arc, size_corner - thickness, 0.0]

points_5 = []
nb_points = nb_segm_arc_4 + 2

blocks_5 = []
faces_5 = []

x0 = 0.0
for ix in range(nb_points + 1):
	dx = dxy_5[ix]
	y0 = 0.0
	points_5.append([])
	for iy in range(nb_points + 1):
		pp = geompy.MakeVertex(x0, -y0, z0_5)
		points_5[ix].append(pp)
		if ix > 0 and iy > 0:
			face = geompy.MakeQuad4Vertices(points_5[ix-1][iy-1],
							points_5[ix-1][iy],
							points_5[ix][iy],
							points_5[ix][iy-1])
			faces_5.append(face)
			pass
		dy = dxy_5[iy]
		y0 += dy
		pass
	x0 += dx
	pass

for ff in faces_5:
	block_5 = geompy.MakePrismVecH(ff, Oz, thickness)
	blocks_5.append(block_5)
	pass

# floor 5'
z0_5_ = z0_5 + thickness

dh_5 = size_arc*2.0

face_5_0_top = geompy.MakeTranslation(faces_5[0], 0, 0, thickness)
block_5_0 = geompy.MakePrismVecH(face_5_0_top, Oz, dh_5)
ind = geompy.LocalOp.GetSubShapeIndex(block_5_0, face_5_0_top)
block_5_ = geompy.MakeMultiTransformation1D(block_5_0, ind, 0, 10)
blocks_5.append(block_5_)

comp_blocks_5 = geompy.MakeCompound(blocks_5)

# cylinder
pp0_cyl = geompy.MakeVertex(0, 0, z0_5_ + dh_5 * 5.0)
pp1_cyl = geompy.MakeVertex(0, - 3.0 * dxy_5[0], z0_5_ + dh_5 * 5.0)
pp2_cyl = geompy.MakeRotation(pp1_cyl, Oz, math.pi/8.0)
pp3_cyl = geompy.MakeRotation(pp1_cyl, Oz, math.pi/4.0)
arc_cyl = geompy.MakeArc(pp1_cyl, pp2_cyl, pp3_cyl)
ee1_cyl = geompy.MakeEdge(pp0_cyl, pp1_cyl)
ee2_cyl = geompy.MakeEdge(pp0_cyl, pp3_cyl)
www_cyl = geompy.MakeWire([ee1_cyl, arc_cyl, ee2_cyl])
fff_cyl = geompy.MakeFace(www_cyl, 1)
sol_cyl = geompy.MakePrismVecH(fff_cyl, Oz, dh_5)
blo_cyl = geompy.MakeCut(sol_cyl, block_5_)

#################################################

arc_floors_blocks = blocks_1 + blocks_pre_2 + blocks_2 + blocks_pre_3 + blocks_3
part_1_8_arc = geompy.MakeCompound(arc_floors_blocks)

part_1_8 = geompy.MakeCompound([part_1_8_arc, comp_blocks_pre_4, blo_cyl] + blocks_4_)
geompy.addToStudy(part_1_8, "part_1_8")

# mirror 1/8
part_1_8_mirr = geompy.MakeMirrorByPlane(part_1_8, pln_Oxy)

# build 1/4
part_1_4 = geompy.MakeCompound([part_1_8, part_1_8_mirr, comp_blocks_5])
part_1_4 = geompy.MakeGlueFaces(part_1_4, 0.00001)
geompy.addToStudy(part_1_4, "part_1_4")

# build whole tower from 1/4
tower_whole = geompy.MultiRotate1DNbTimes(part_1_4, Oz, 4)
tower_whole = geompy.MakeGlueFaces(tower_whole, 0.00001)
geompy.addToStudy(tower_whole, "tower_whole")


# Find two edges to do special discretisation on them
# and on their opposite edges, using hypotheses propagation

thickness_edge_1 = geompy.GetEdge(tower_whole, pp1, pp2)
geompy.addToStudyInFather(tower_whole, thickness_edge_1, "thickness_edge_1")

pp0_low = points_5[0][0]
pp0_hig = geompy.MakeTranslation(pp0_low, 0, 0, thickness)

thickness_edge_2 = geompy.GetEdge(tower_whole, pp0_low, pp0_hig)
geompy.addToStudyInFather(tower_whole, thickness_edge_2, "thickness_edge_2")

#########################################
#
# Tower Mesh
#
#########################################

import SMESH
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New()

# Assign hypotheses and algorithms
tower_mesh = smesh.Mesh(tower_whole)
algo1D = tower_mesh.Segment()
algo1D.NumberOfSegments(5)
tower_mesh.Quadrangle()
tower_mesh.Hexahedron()

algo_local_1 = tower_mesh.Segment(thickness_edge_1)
algo_local_1.NumberOfSegments(1)
algo_local_1.Propagation()

algo_local_2 = tower_mesh.Segment(thickness_edge_2)
algo_local_2.NumberOfSegments(1)
algo_local_2.Propagation()

# Compute the 3D mesh
isDone = tower_mesh.Compute()
if not isDone: print('Mesh computation failed')

# https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html
# saving the study such that it can be loaded in Salome
salome.myStudy.SaveAs("tower.hdf", False, False) # args: use_multifile, use_acsii

# Update Object Browser
if salome.sg.hasDesktop():
	salome.sg.updateObjBrowser()
