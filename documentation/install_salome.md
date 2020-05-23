# Installing Salome

Usually it is enough to [download](https://www.salome-platform.org/downloads/current-version) and unpack Salome.

In some cases it can be necessary to do additional things like installing some missing libraries. For required libraries and how to install them it is recommended to check the [DockerFiles](../.github).

#

Here is a list of know issues:

- Cannot save files on Windows:
add `@SET SALOME_TMP_DIR=%TEMP%` at the end of `SALOME-8.2.0-WIN64\WORK\set_env.bat`. More information can be found [here](https://www.salome-platform.org/forum/forum_10/541818275).

- Installation on Ubuntu 18.04:
    - Problem:
        `SALOME_Session_Server: error while loading shared libraries: libicui18n.so.55: cannot open shared object file: No such file or directory`

        Download and install missing package: <https://www.ubuntuupdates.org/package/core/xenial/main/security/libicu55>

    - Problem:
        `SALOME_Session_Server: error while loading shared libraries: libpcre16.so.3: cannot open shared object file: No such file or directory`

        Install missing package:
        `sudo apt-get install libpcre16-3`

    - Problem:
        `SALOME_Session_Server: error while loading shared libraries: libpng12.so.0: cannot open shared object file: No such file or directory`

        Download and install missing package:
        1. `wget http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb`
        2. `sudo dpkg -i libpng12-0_1.2.54-1ubuntu1_amd64.deb`

    - Problem: Meshing requires `libgfortran.so.3` but, gcc7 only has *.4

        `sudo apt-get install libgfortran3`