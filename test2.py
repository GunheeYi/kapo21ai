class A:
    def __init__(self):
        self.a = [ 1, 2, 3 ]
    def get(self, index):
        return self.a[index]

a = A()
b = a.get(0)
b = 24

print(a.a)