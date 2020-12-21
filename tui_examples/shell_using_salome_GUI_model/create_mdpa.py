"""
This script is designed to be loaded in the Salome GUI after the Salome project
file plate_with_hole.hdf has been opened.
It exports the Salome mesh in Kratos syntax as .mdpa file.

NOTE: Before loading this script, lines 16&20 have to be updated with
the absolute paths to:
- the KratosSalomePlugin (line 16)
- the desired output of the .mdpa file (line 20)
"""

import sys
import os


sys.path.append("/absolute/path/to/KratosSalomePlugin")
import create_kratos_input_tui

# define the target path and file name for the mdpa file
mdpa_path = "/absolute/path/to/output/of/mdpa_file/"
mdpa_file_name = "plate_with_hole"

# define the modelparts for Kratos (elements, conditions)
shell = { "elements"   : {"Triangle" : {"ShellThinElement3D3N" : 1} } }
loads = { "conditions" : {"Node" : {"PointLoadCondition3D1N" : 0} } }

meshes = [
    create_kratos_input_tui.SalomeMesh("0:1:2:3", shell, "shell"),
    create_kratos_input_tui.SalomeMesh("0:1:2:3:5:1", {}, "support"),
    create_kratos_input_tui.SalomeMesh("0:1:2:3:4:1", loads, "load1"),
    create_kratos_input_tui.SalomeMesh("0:1:2:3:4:2", loads, "load2")
]

create_kratos_input_tui.CreateMdpaFile(meshes, os.path.join(mdpa_path, mdpa_file_name))

print(f"Kratos mdpa file written to:\n{os.path.join(mdpa_path, mdpa_file_name)}.mdpa")
