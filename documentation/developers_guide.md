# Development Guide
This is a guide for developing in the plugin. It explains the most important concepts and ideas that are used.

## Interaction with Salome Meshes
Mesh idetifier of Salome is used. This is supposed to be unique. Note that the mesh names can be duplicated!

## Creating the MDPA file
An instance of `ModelPart` is created, to which entities (Nodes, Elements etc) are added, e.g. using the `ConnectivitiesIO`. Then `write_mdpa` is used to write the mdpa file.
This workflow is very native for people familiar with Kratos.

## Debugging
- Increase the logger level
- Check the logs

## Testing
The plugin is heavily tested to ensure not only the functionalities but also to check if the things are still working with newer versions of Salome.

### Testing without Salome

### Testign with Salome
