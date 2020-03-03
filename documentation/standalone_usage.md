# Standalone usage for creating MDPA files

This is a brief guide for using some functionalities **INDEPENDENT** of Salome for creating mdpa files that are used as input for Kratos. This is basically what the [salome-kratos-converter](https://github.com/philbucher/salome-kratos-converter#using-the-converter-directly-directly-from-python) did.

Also take a look at ... for more details.

The interface is kept as close to the interface of Kratos as possible.

The [tests]() can also provide some more insights.

Kratos cannot be imported inside Salome. Ofc in the GUI it is not available, but even in the standalone version it is not possible. Python-only things can be imported, but it seems to no be possible to load C++ modules


https://docs.salome-platform.org/latest/tui/KERNEL/kernel_salome.html