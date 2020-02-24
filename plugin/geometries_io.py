#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

# python imports
import logging
logger = logging.getLogger(__name__)
logger.debug('loading module')

class Mesh(object):
    def __init__(self, model_part_name, mesh_interface, mesh_description):
        self.model_part_name = model_part_name
        self.mesh_interface = mesh_interface
        self.mesh_description = mesh_description

    def __str__(self):
        string_buf  = "Mesh\n"
        string_buf += "  ModelPart name: {}\n".format(self.model_part_name)
        string_buf += "  MeshInterface : {}\n".format(self.mesh_interface.PrintData("  "))
        string_buf += "  Mesh description: {}\n".format(self.mesh_description)
        return string_buf


class GeometriesIO(object):
    @staticmethod
    def AddMeshes(model_part, meshes):
        if model_part.GetRootModelPart().NumberOfNodes() != 0:
            err_msg  = 'The Root-ModelPart "{}" is not empty!\n'.format(model_part.GetRootModelPart().Name)
            err_msg += 'This is required because otherwise the numbering of entities can get messed up'
            raise RuntimeError(err_msg)

        # maps to prevent recreating entities from the same geometry!
        all_elements   = {} # map: {element_names   : {origin_ids : element} }
        all_conditions = {} # map: {condition_names : {origin_ids : condition} }

        for mesh in meshes:
            default_mesh_description = {
                "elements"   : { },
                "conditions" : { }
            }

            for k, v in default_mesh_description.items():
                if k not in mesh.mesh_description:
                    mesh.mesh_description[k] = v

            GeometriesIO.__AddEntitiesToModelPart(model_part, mesh, all_elements, all_conditions)

    @staticmethod
    def __AddEntitiesToModelPart(model_part, mesh, all_elems, all_conds):
        model_part_to_add_to = GeometriesIO.__GetModelPartToAddTo(model_part, mesh.model_part_name)

        logger.info('Adding mesh to ModelPart "{}"'.format(model_part_to_add_to.FullName()))

        mesh_description = mesh.mesh_description
        mesh_interface = mesh.mesh_interface
        unique_keys = list(set(list(mesh_description["elements"].keys()) + list(mesh_description["conditions"].keys())))
        nodes, geometries = mesh_interface.GetNodesAndGeometricalEntities(unique_keys)

        GeometriesIO.__AddNodes(model_part_to_add_to, nodes)

        # Get Properties => See "read_materials_utility.cpp" function "AssignPropertyBlock"
        if len(mesh_description["elements"]) > 0:
            GeometriesIO.__AddElemensts(model_part_to_add_to, geometries, mesh_description["elements"], all_elems)
        if len(mesh_description["conditions"]) > 0:
            GeometriesIO.__AddConditions(model_part_to_add_to, geometries, mesh_description["conditions"], all_conds)

    @staticmethod
    def __GetModelPartToAddTo(model_part, model_part_name):
        if model_part_name == "": # using the root model part
            return model_part
        else: # using a sub model part
            def RecursiveCreateModelParts(model_part, model_part_name):
                model_part_name, *sub_model_part_names = model_part_name.split(".")

                # TODO add some info log saying whether using an existing smp or creating a new one
                if model_part.HasSubModelPart(model_part_name):
                    model_part = model_part.GetSubModelPart(model_part_name)
                else:
                    model_part = model_part.CreateSubModelPart(model_part_name)

                if len(sub_model_part_names) > 0:
                    model_part = RecursiveCreateModelParts(model_part, ".".join(sub_model_part_names))

                return model_part

            return RecursiveCreateModelParts(model_part, model_part_name)

    @staticmethod
    def __AddNodes(model_part_to_add_to, new_nodes):
        # Note: NOT checking the coordinates here since this is done in the ModelPart
        for node_id, node_coords in new_nodes.items():
            model_part_to_add_to.CreateNewNode(node_id, node_coords[0], node_coords[1], node_coords[2])

    @staticmethod
    def __AddElemensts(model_part_to_add_to, geometries, elements_creation, all_elements):
        element_id_counter = model_part_to_add_to.GetRootModelPart().NumberOfElements() + 1

        def CreateAndSaveNewElement(element_name, geometry_id, connectivities, properties, element_id_counter):
            new_element = model_part_to_add_to.CreateNewElement(element_name, element_id_counter, connectivities, properties)
            all_elements[element_name][geometry_id] = new_element
            return element_id_counter+1

        for geometry_type, entities_dict in elements_creation.items():
            for element_name, props_id in entities_dict.items():

                # TODO add some info log saying whether using an existing prop or creating a new one
                if model_part_to_add_to.RecursivelyHasProperties(props_id):
                    props = model_part_to_add_to.GetProperties(props_id, 0) # 0 is the mesh_id, required for Kratos
                else:
                    props = model_part_to_add_to.CreateNewProperties(props_id)

                if element_name in all_elements: # elements of this type already exist
                    for geometry_id, connectivities in geometries[geometry_type].items():
                        existing_element = all_elements[element_name].get(geometry_id)
                        if existing_element:
                            # an element was already created from this geometry
                            # therefore NOT creating a new one but adding the existing one
                            # Note: this does not check the Properties (maybe should, but would probably affect performance)
                            model_part_to_add_to.AddElement(existing_element)
                            # TODO maybe save the IDs and use AddElements instead? => might be faster
                        else:
                            # no element has yet been created from this geometry
                            # hence creating a new one
                            element_id_counter = CreateAndSaveNewElement(element_name, geometry_id, connectivities, props, element_id_counter)

                else: # no elements of this type exist yet, new elements can be added without checking
                    all_elements[element_name] = {}
                    for geometry_id, connectivities in geometries[geometry_type].items():
                        element_id_counter = CreateAndSaveNewElement(element_name, geometry_id, connectivities, props, element_id_counter)

    @staticmethod
    def __AddConditions(model_part_to_add_to, geometries, conditions_creation, all_conditions):
        raise NotImplementedError












def __init__(self, model_part):
    self.model_part = model_part
    if self.model_part.GetRootModelPart().NumberOfNodes() != 0:
        # if nodes already exist then the numbering might get screwed up!
        raise RuntimeError("The Root-ModelPart has to be empty!")

def AddMesh(self, mesh_name, mesh_interface, mesh_description):
    """ Example for the format of the "mesh_description":
    {
        "add_sub_model_part" : True

        "elements" : {
            "0D"         : { "PointLoadCondition3D1N"   : 0,
                                "PointMomentCondition3D1N" : 1
                            }
            "Triangle"   : [["SmallDisplacementElement2D3N", 0]]
            "Quadrangle" : [["SmallDisplacementElement2D4N", 0]]

        "conditions" : {
            "Line" : [["LineCondition", 0]]
        }
    }
    """

    default_mesh_description = {
        "add_sub_model_part" : True,
        "elements" : { },
        "conditions" : { }
    }

    for k,v in default_mesh_description.items():
        if k not in mesh_description:
            mesh_description[k] = v


    # TODO how to handle the overwritting?

    if mesh_description["add_sub_model_part"]:
        model_part_to_add_to = self.model_part.CreateSubModelPart(mesh_name) # this enforces the names to be unique
    else:
        model_part_to_add_to = self.model_part

    unique_keys = list(set(list(mesh_description["elements"].keys()) + list(mesh_description["conditions"].keys())))
    nodes, geom_entities = mesh_interface.GetNodesAndGeometricalEntities(unique_keys)

    self.__AddNodes(model_part_to_add_to, nodes)

    if len(mesh_description["elements"]) > 0:
        self.__AddElements(model_part_to_add_to, geom_entities, mesh_description["elements"])
    if len(mesh_description["conditions"]) > 0:
        self.__AddConditions(model_part_to_add_to, geom_entities, mesh_description["conditions"])

def __AddElements(self, model_part_to_add_to, geom_entities, entity_creation):
    counter = 0
    for entity_type, entities_dict in entity_creation.items():
        print(entity_type, entities_dict)
        for entities_name, props_id in entities_dict.items():
            print(entities_name, props_id)
            props = model_part_to_add_to.GetRootModelPart().GetProperties(props_id)
            for geom_entity_id, geom_entity_connectivitiess in geom_entities[entity_type].items():
                print(geom_entity_id, geom_entity_connectivities)
                counter += 1
                model_part_to_add_to.CreateNewElement(entities_name, counter, geom_entity_connectivities, props)

def __AddConditions(self, model_part_to_add_to, geom_entities, entity_creation):
    pass