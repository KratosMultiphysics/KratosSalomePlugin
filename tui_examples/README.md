## TUI Examples

This folder contains scripts and examples for using the functionalities of the plugin in **TUI** mode.

### List of examples:
- [Cantilever beam](cantilever): modeled with solid elements. This is a simple example demonstrating the basic TUI usage for creating a structural model.
- **WIP** [Wind turbine blade](wind_turbine_blade): Advanced structural model of a wind turbine blade discretized with shell elements. Shows how to work with multiple meshes and submeshes.
- **WIP** [Tower](tower): Structural Model of a tower, taken from the [salome website](https://www.salome-platform.org/user-section/tui-examples). More complex structural model.
- [Flow around cylinder](flow_cylinder): Flow around a cylinder in 2D. Shows how to do mesh refinements and write multiple mdpa files.
- **WIP** [Flow over cross with chimera](flow_cross_chimera): Flow over a cross, modelled with overlappig domains using chimera. One domain is the background, the other is the patch containing the cross. The domains are overlapping.
- [Mok FSI](mok_fsi): The Mok FSI benachmark as defined in the dissertation of [Daniel Mok, chapter 7.3](http://dx.doi.org/10.18419/opus-147). This includes two domains, fluid and structure.
- **WIP** [Balls against barrier](balls_barrier): Balls modeled with discrete elements interact with a rigid wall
- **WIP** [Rock falling into cablenet](rock_cablenet): Demonstrating the usage of using discrete elements together with finite elements

### Executing the examples
As [described in the README](../../README.md#how-does-it-work) this example can be executed in two ways:
- Loading the file with `File/Load Script ...` inside of Salome
- Using [execute_in_salome](../execute_in_salome.py). E.g. `python3 ../../execute_in_salome.py ~/software/SALOME/SALOME-9.3.0-UB16.04-SRC/salome salome_cantilever_tetra.py`
