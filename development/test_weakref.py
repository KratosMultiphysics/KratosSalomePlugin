
import weakref

class A:
    def Hello(self):
        print("A says hello")

a = A()
print(weakref.getweakrefcount(a))

wr = weakref.ref(a)

print(wr)
print(dir(wr))
print(wr())
wr().Hello()
print(weakref.getweakrefcount(a))

del (a)
print(wr)
print(wr())
