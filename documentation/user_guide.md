# User Guide
This guide explains how the plugin works in the background and how it can be used.

The workflow for creating Kratos input files (currently supported format: `mdpa`) follows the workflow of Kratos itself. The implementation is very modular, such that it can easily be extended (or even adapted to other preprocessors) in the future.

The main components are:
- [`ModelPart`](../kratos_salome_plugin/model_part.py): Kratos cannot be imported inside of Salome. Hence a python version of the [Kratos-ModelPart](https://github.com/KratosMultiphysics/Kratos/blob/master/kratos/includes/model_part.h) was developed, which has a matching interface for the most part. I.e. it is possible to add Nodes, Elements, Properties etc, just like with the Kratos-ModelPart. Form users familiar with Kratos using it is straight forward.
- [`write_mdpa`](../kratos_salome_plugin/write_mdpa.py): This function takes a `ModelPart` as input and writes an `mdpa` file from it. This is basically what the [ModelPartIO](https://github.com/KratosMultiphysics/Kratos/blob/master/kratos/includes/model_part_io.h) does. It was kept a bit more modular to be easier to extend in the future.
- [`GeometriesIO`](../kratos_salome_plugin/geometries_io.py): This class takes (Salome) meshes as input and creates `Nodes`, `Elements` and `Conditions` from it. It works purely based on connectivities and could therefore serve as a prototype for creating `ModelPart`s from `Geometries` inside of the solvers in Kratos
- [`MeshInterface`](../kratos_salome_plugin/mesh_interface.py): The interface for getting accessing the Salome Mesh. It directly accesses the database of Salome and extracts the information the user requested.

Those components are combined in the following way:
1. An empty `ModelPart` is created
2. `MeshInterface`s are created for the Salome meshes that are to be used
3. The created `ModelPart` and the `MeshInterface`s are given to the `GeometriesIO` in order to create `Nodes`, `Elements` and `Conditions`. A separate dictionary is used to specify which entities to create.
4. After the `ModelPart` is filled with entities, it is being passed to `write_mdpa` for creating the `mdpa` file.


## GUI mode
The GUI is currently under development. This section will be added once the GUI of the plugin fully developed.


## TUI mode
The plugin offers a wide range of usecases:
- The most basic and straight forward way of creating `mdpa` files from salome meshes is to use `CreateMdpaFile` of [create_kratos_input_tui.py](../create_kratos_input_tui.py). Several [examples](../tui_examples) demonstrate this.
- In case the user wants to modify the `ModelPart` before creating an `mdpa` file, then the function `CreateModelPart` is suitable. After modifying the `ModelPart` the function `write_mdpa` can be called separately.
- For a more customized usage the main components introduced above can of course also be used individually. It is recommended to take a look at the workflow inside of `create_kratos_input_tui.py` as a starting point.