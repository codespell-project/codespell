
class Person:
   def __init__(self,name,age):
        self.name = name
        self.age = age
   def display(self):
        print(self.name,self.age)
p = Person("joe",30)
p.display()


class Person:
   def __init__(self,name,age):
        self.name = name
        self.age = age
 
p = Person("joe",30)
print(p.name,p.age)
