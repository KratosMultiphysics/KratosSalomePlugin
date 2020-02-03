### This folder contains files and other things that are helpful for the development.

**Github Actions:**
- Version 8.3 and 8.4 do NOT return failure (i.e. `sys.exit(1)`) even if they fail in TUI-mode! => hence have to be checked manually!

**Github Actions: triggering workflows externally**
http://www.btellez.com/posts/triggering-github-actions-with-webhooks.html
https://stackoverflow.com/questions/57903836/how-to-fail-a-job-in-github-actions

This file contains a collection of links that are useful for the development

**Salome**
- How to detect Salome version? : https://www.salome-platform.org/forum/forum_12/175881302
- How to active geometry module using python?: https://www.salome-platform.org/forum/forum_12/171355949
- https://code-aster.it/2019/01/04/come-fare-un-plugin-in-salome/
- https://docs.salome-platform.org/5/gui/dev/classSVTK__ViewModelBase.html => selectionChanged
- https://docs.salome-platform.org/7/gui/GUI/using_pluginsmanager.html => selectionChanged
- https://docs.salome-platform.org/latest/gui/GUI/using_pluginsmanager.html => maybe there one can see how to connect slots

**Testing**
Mock objects are not used because it is not included in Salome => Mock is only part of unittest since python3.3
"terminate called after throwing an instance of 'CORBA::OBJECT_NOT_EXIST'" called after tests in Version 9, related to study clearing but nothing to worry about

**Resons to drop support for versions > 9**
- Mock unittesting is not available
- return value is not correct in older version, makes use of wrapper necessary
- PointerVectorSet not working with py-2 (infinite recursion)
- filtering on subgeom seems not to work
- well, python2 ...
- some other methods inside of salome are not working (e.g. GetSalomeObject from identifier, or some classes only have type "instance")
- study management much easier, since now there is only one study and I don't have to maintain two different versions