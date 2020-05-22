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

class Mesh(object):
    def __init__(self, mesh_interface, mesh_description, model_part_name=""):
        # name of ModelPart by default empty, which means that entities will be added to the ModelPart that is being passed to the GeometriesIO
        self.mesh_interface = mesh_interface
        self.mesh_description = mesh_description
        self.model_part_name = model_part_name

    def __str__(self):
        string_buf  = "Mesh\n"
        string_buf += "  MeshInterface : {}\n".format(self.mesh_interface.PrintData("  "))
        string_buf += "  Mesh description: {}\n".format(self.mesh_description)
        string_buf += "  ModelPart name: {}\n".format(self.model_part_name)
        return string_buf


class GeometriesIO(object):
    @staticmethod
    def AddMeshes(model_part, meshes):
        if model_part.GetRootModelPart().NumberOfNodes() != 0:
            # this also ensures that no Elements/Conditions exist, since they need Nodes
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
        unique_keys = set(list(mesh_description["elements"].keys()) + list(mesh_description["conditions"].keys()))
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

                if model_part.HasSubModelPart(model_part_name):
                    model_part = model_part.GetSubModelPart(model_part_name)
                    logger.debug('Using existing SubModelPart "{}"'.format(model_part_name))
                else:
                    model_part = model_part.CreateSubModelPart(model_part_name)
                    logger.debug('Creating new SubModelPart "{}"'.format(model_part_name))

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

        def AddExistingElement(model_part, element):
            model_part.AddElement(element, 0) # 0 is the mesh_id, required for Kratos

        GeometriesIO.__AddGeometricalEntities(model_part_to_add_to,
                                              geometries,
                                              elements_creation,
                                              all_elements,
                                              CreateAndSaveNewElement,
                                              AddExistingElement,
                                              element_id_counter)

    @staticmethod
    def __AddConditions(model_part_to_add_to, geometries, conditions_creation, all_conditions):
        condition_id_counter = model_part_to_add_to.GetRootModelPart().NumberOfConditions() + 1

        def CreateAndSaveNewCondition(condition_name, geometry_id, connectivities, properties, condition_id_counter):
            new_condition = model_part_to_add_to.CreateNewCondition(condition_name, condition_id_counter, connectivities, properties)
            all_conditions[condition_name][geometry_id] = new_condition
            return condition_id_counter+1

        def AddExistingCondition(model_part, condition):
            model_part.AddCondition(condition, 0) # 0 is the mesh_id, required for Kratos

        GeometriesIO.__AddGeometricalEntities(model_part_to_add_to,
                                              geometries,
                                              conditions_creation,
                                              all_conditions,
                                              CreateAndSaveNewCondition,
                                              AddExistingCondition,
                                              condition_id_counter)

    @staticmethod
    def __AddGeometricalEntities(model_part_to_add_to, geometries, entities_creation, all_entities, fct_ptr_create_save_new_entity, fct_ptr_add_existing_entity, id_counter):
        for geometry_type, entities_dict in entities_creation.items():
            reorder_conn_fct_ptr = GetReorderFunction(geometry_type)

            for entity_name, props_id in entities_dict.items():

                if model_part_to_add_to.RecursivelyHasProperties(props_id):
                    # note: this also adds the properties to the submodelpart (if previously they were only in the mainmodelpart)
                    props = model_part_to_add_to.GetProperties(props_id, 0) # 0 is the mesh_id, required for Kratos
                    logger.debug('Using existing Properties with Id {} for "{}"'.format(props_id, entity_name))
                else:
                    props = model_part_to_add_to.CreateNewProperties(props_id)
                    logger.debug('Creating new Properties with Id {} for "{}"'.format(props_id, entity_name))

                already_existing_entities = 0
                newly_created_entities = 0

                if entity_name in all_entities: # entities of this type already exist
                    logger.debug('Entities with name "{}" exist already'.format(entity_name))

                    for geometry_id, connectivities in geometries[geometry_type].items():
                        existing_entity = all_entities[entity_name].get(geometry_id)
                        if existing_entity:
                            # an entity was already created from this geometry
                            # therefore NOT creating a new one but adding the existing one
                            if props_id != existing_entity.Properties.Id:
                                err_msg  = 'Mismatch in properties Ids!\n'
                                err_msg += 'Trying to use properties with Id {} '.format(props_id)
                                err_msg += 'with an existing entity that has the properties with Id {}'.format(existing_entity.Properties.Id)
                                raise Exception(err_msg)
                            fct_ptr_add_existing_entity(model_part_to_add_to, existing_entity)
                            already_existing_entities+=1
                        else:
                            # no entity has yet been created from this geometry
                            # hence creating a new one
                            reordered_conn = reorder_conn_fct_ptr(connectivities)
                            id_counter = fct_ptr_create_save_new_entity(entity_name, geometry_id, reordered_conn, props, id_counter)
                            newly_created_entities+=1

                else: # no entities of this type exist yet, new entities can be added without checking
                    logger.debug('No entities with name "{}" exist already'.format(entity_name))
                    all_entities[entity_name] = {}
                    for geometry_id, connectivities in geometries[geometry_type].items():
                        reordered_conn = reorder_conn_fct_ptr(connectivities)
                        id_counter = fct_ptr_create_save_new_entity(entity_name, geometry_id, reordered_conn, props, id_counter)
                        newly_created_entities+=1

                logger.debug('{} new entities were created and {} existed already'.format(newly_created_entities, already_existing_entities))


def GetReorderFunction(salome_entity_type):
    # for some entities the node ordering differs between Salome and Kratos
    # those have to be corrected
    if salome_entity_type == "Tetra":
        return lambda conn: [conn[i] for i in [0, 2, 1, 3]]
    elif salome_entity_type == "Hexa":
        return lambda conn: [conn[i] for i in [0, 3, 2, 1, 4, 7, 6, 5]]
    elif salome_entity_type == "Penta":
        return lambda conn: [conn[i] for i in [0, 2, 1, 3, 5, 4]]
    else:
        return lambda conn: conn
