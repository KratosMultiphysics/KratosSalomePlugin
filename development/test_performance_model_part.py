"""
Testing the performance (speed and memor usage) of the py-ModelPart and the WriteMdpa
"""


from ks_plugin import model_part
from ks_plugin.write_mdpa import WriteMdpa

from memory_profiler import profile

from time import time

@profile
def CreateDataValueContainers(num_objects):
    u = [model_part.DataValueContainer()] * num_objects

@profile
def CreateNodes(num_objects):
    u = [model_part.Node(0,0,0,0)] * num_objects

@profile
def CreateModelPart():
    mp = model_part.ModelPart("for_Test_profiling")

    start_time = time()
    for i in range(int(3E5)+1):
        mp.CreateNewNode(i+1,0,0,0)

    print('Creating {0} Nodes took {1:.{2}f} [s]'.format(mp.NumberOfNodes(), time()-start_time,2))

    props = mp.CreateNewProperties(0)
    start_time = time()
    for i in range(mp.NumberOfNodes()-1):
        mp.CreateNewElement("BarElement", i+1, [i+1,i+2],props)

    print('Creating {0} Elements took {1:.{2}f} [s]'.format(mp.NumberOfElements(), time()-start_time,2))

# CreateDataValueContainers(100000000)
# CreateNodes(100000000)

def CreateFullModelPart():
    # just creating a full ModelPart for testing
    mp = model_part.ModelPart()
    mp.SetValue("Card", 15.336)
    mp.SetValue("kMui", [2, 3.3, 15.78, -33.74, 36.01, 72.1])
    mp.SetValue("SomeMatrix", [[2, 3.3, 10.4, 11.2, 0.33], [5.3, 456, 88.123, 101.3, 7.456], [1.129,2.129,3.129,4.129,5.129]])
    mp.SetValue("TheString", "SmallDisp")
    mp.SetValue("Mulz", 1)
    mp.SetValue("AAbbCC", 1.336E6)
    mp.SetValue("YOUNG", 2397)

    smp_1 = mp.CreateSubModelPart("smp_one") # sub
    smp_2 = smp_1.CreateSubModelPart("smp_two") # subsub
    smp_22 = smp_1.CreateSubModelPart("smp_two_two") # subsub
    smp_3 = smp_2.CreateSubModelPart("smp_two_three") # subsubsub

    smp_1.SetValue("wweerrtt", 12345)
    smp_1.SetValue("LITF", 852.74)

    smp_22.SetValue("My_Val", -92.74)
    smp_22.SetValue("TAB", 13)

    for i in range(400000):
        node = smp_1.CreateNewNode(i+1, i*2.2, 0.0, 0.0)
        node.SetValue("kMui", [2, 3.3, -78.1, i+2]) # vector
        if i%2==0:
            node.SetValue("Hjkwq", 15-i)
    for i in range(400000, 1100000):
        smp_2.CreateNewNode(i+1, 0.0, 0.0, -i*8.3)
    for i in range(1100000, 1400000):
        smp_22.CreateNewNode(i+1, 0.0, i*i+2.3, 0.0)
    for i in range(1400000, 2000000):
        smp_3.CreateNewNode(i+1, 1.897+i, -i*i+2.3, 0.0)

    for i in range(2500000, 3500000):
        node = mp.CreateNewNode(i+1, 1.897+i, i*i+2.3, 18+i*1.33)
        node.SetValue("Hjkwq", 1+5*i)

    props_1 = smp_1.CreateNewProperties(1)
    props_1.SetValue("Card", 15.336)
    props_1.SetValue("kMui", [2, 3.3])
    props_1.SetValue("SomeMatrix", [[2, 3.3], [5.3, 7.456]])
    props_1.SetValue("TheString", "SmallDisp")

    props_2 = mp.CreateNewProperties(2)
    props_2.SetValue("sdlwzy", [2, 3.3, 15.78, -33.74, 36.01, 72.1])

    props = mp.CreateNewProperties(15)
    props.SetValue("Mulz", 1)
    props.SetValue("AAbbCC", 1.336E6)
    props.SetValue("YOUNG", 2397)

    for i in range(6):
        elem = smp_1.CreateNewElement("CustomElement", i+1, [1], props_1)
        elem.SetValue("AUX_INDEX", 1.45*i)
    for i in range(3):
        cond = smp_1.CreateNewCondition("TheMainCondition", i+1, [1], props)
        cond.SetValue("main", [1-i, i*9, 3.7093-10*i, 3.45, 5.1])
    for i in range(6):
        elem = smp_2.CreateNewElement("FluidElement", i+7, [1], props_2)
        if i%2==0:
            elem.SetValue("AUX_INDEX", 1.45*i)
        else:
            elem.SetValue("MIN", -13.9*i)

    for i in range(3):
        cond = smp_22.CreateNewCondition("WallCondition", i+4, [1], props)
        cond.SetValue("DIST", i+1)
    for i in range(6): # again adding the same type to make sure this also works
        smp_1.CreateNewElement("CustomElement", i+18, [1], props_1)

    return mp

# CreateModelPart()

start_time = time()
my_mp = CreateFullModelPart()
print('Creating ModelPart took {0:.{1}f} [s]'.format(time()-start_time,2))

start_time = time()
WriteMdpa(my_mp, "asdf")
print('Creating MDPA took {0:.{1}f} [s]'.format(time()-start_time,2))
import os
os.remove("asdf.mdpa")

