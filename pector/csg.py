from pector.vec3 import vec3
from pector.mat4 import mat4
from pector import tools

INFINITY = 1.0e+20

class CsgBase:
    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return "CsgBase(\"%s\")" % self.name
    def __repr__(self):
        return self.__unicode__()

    def get_distance(self, pos):
        raise NotImplementedError


class Primitive(CsgBase):
    def __init__(self, name, transform=mat4()):
        super(Primitive, self).__init__(name)
        self.transform = mat4(transform)
        self.itransform = self.transform.inverted_simple()

    def __unicode__(self):
        return "Primitive(\"%s\", tranform=%s)" % (self.name, self.transform)



class Container(CsgBase):
    def __init__(self, name, objects=[]):
        super(Container, self).__init__(name=name)
        self.objects = objects

    def add(self, object):
        if not isinstance(object, CsgBase):
            raise TypeError("Adding non-CsgBase objects to Container is not supported")
        if object in self.objects:
            raise ValueError("Can not add the same instance twice: %s" % object)
        self.objects.append(object)

    def __unicode__(self):
        return "Container(\"%s\", %s)" % (self.name, self.objects)


class Union(Container):
    def __init__(self, objects=[]):
        super(Union, self).__init__(name="union", objects=objects)

    def __unicode__(self):
        return "Union(%s)" % self.objects

    def get_distance(self, pos):
        d = INFINITY
        for i in self.objects:
            d = min(d, i.get_distance(pos))
        return d


class Difference(Container):
    def __init__(self, objects=[]):
        super(Difference, self).__init__(name="difference", objects=objects)

    def __unicode__(self):
        return "Difference(%s)" % self.objects

    def get_distance(self, pos):
        if not self.objects:
            return INFINITY
        d = self.objects[0].get_distance(pos)
        for i in range(1, len(self.objects)):
            d = max(d, -self.objects[i].get_distance(pos))
        return d


class Sphere(Primitive):
    def __init__(self, radius = 1., transform = mat4()):
        super(Sphere, self).__init__(name="sphere", transform=transform)
        self.radius = tools.check_float_number(radius)

    def __unicode__(self):
        return "Sphere(radius=%g, transform=%s)" % (self.radius, self.transform)

    def get_distance(self, pos):
        return (self.itransform * pos).length() - self.radius



if __name__ == "__main__":

    def print_slice(csg, center=(0., 0.), size=(20,20), scale=.1):
        scaley = scale * size[1] * 2.
        scalex = scale * size[0]
        scale = scale * max(size[0], size[1])
        for j in range(size[1]):
            y = (.5 - j / size[1]) * scaley + center[1]
            for i in range(size[0]):
                x = (i / size[0] - .5) * scalex + center[0]
                d = csg.get_distance((x,y,0.))
                c = "."
                if d <= 0.:
                    c = "#"
                print(c, end="")
            print("")

    s = Sphere()
    print(s)

    c = Difference([s, Sphere(radius=0.5, transform=mat4().translate((1.,0,0)))])

    print(c)
    print(c.get_distance((2,0,0)))
    print_slice(c, size=(80, 10))