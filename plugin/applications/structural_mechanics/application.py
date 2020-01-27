#  _  __         _          ___       _               ___ _           _
# | |/ /_ _ __ _| |_ ___ __/ __| __ _| |___ _ __  ___| _ \ |_  _ __ _(_)_ _
# | ' <| '_/ _` |  _/ _ (_-<__ \/ _` | / _ \ '  \/ -_)  _/ | || / _` | | ' \
# |_|\_\_| \__,_|\__\___/__/___/\__,_|_\___/_|_|_\___|_| |_|\_,_\__, |_|_||_|
#                                                               |___/
# License: BSD License ; see LICENSE
#
# Main authors: Philipp Bucher (https://github.com/philbucher)
#

from base_application import Application


class StructuralMechanicsApplication(Application):

    def WriteCalculationFiles(self, path):
        project_parameters, materials, mesh = self.__AssembleBeforeWrite()
        WriteJson(project_parameters, path)
        WriteJson(materials, path)
        WriteModelPart(mesh_definition, full_path)

    def __AssembleBeforeWrite(self):
        project_parameters = {
            "processes"        : [],
            "output_processes" : []
        }

        mesh = []

        project_parameters["problem_data"] = self.GetProblemData().GetJson()
        project_parameters["solver_settings"] = self.GetSolverSettings().GetJson()

        for bc in self.GetBoundaryConditions:
            mesh_def = bc.GetMeshDefinition()
            mesh_group = bc.GetMeshGroup()
            mesh.append((mesh_def, mesh_group))

        for mat in self.GetMaterials():
            pass

        for output in self.GetOutput():
            pass


