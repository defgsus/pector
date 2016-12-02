from pector import vec3, mat4, tools

INFINITY = 1.0e+20

class CsgBase:
    def __init__(self, name, transform):
        self.name = name
        self._transform = mat4(transform)
        self._itransform = self._transform.inverted_simple()

    def __unicode__(self):
        return "CsgBase(\"%s\")" % self.name
    def __repr__(self):
        return self.__unicode__()

    @property
    def transform(self):
        return self._transform
    @transform.setter
    def transform(self, mat):
        self.set_transform(mat)
    def set_transform(self, mat):
        self._transform = mat4(mat)
        self._itransform = self._transform.inverted_simple()
        return self

    def pos_to_local(self, pos):
        return self._itransform * pos

    def copy(self):
        raise NotImplementedError

    def get_distance(self, pos):
        raise NotImplementedError


class Container(CsgBase):
    def __init__(self, name, objects=[], transform=mat4()):
        super(Container, self).__init__(name=name, transform=transform)
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
    def __init__(self, objects=[], transform=mat4()):
        super(Union, self).__init__(name="union", objects=objects, transform=transform)

    def __unicode__(self):
        return "Union(%s)" % self.objects

    def copy(self):
        return Union([o.copy() for o in self.objects], transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        d = INFINITY
        for i in self.objects:
            d = min(d, i.get_distance(pos))
        return d


class Difference(Container):
    def __init__(self, objects=[], transform=mat4()):
        super(Difference, self).__init__(name="difference", objects=objects, transform=transform)

    def __unicode__(self):
        return "Difference(%s)" % self.objects

    def copy(self):
        return Difference([o.copy() for o in self.objects], transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        if not self.objects:
            return INFINITY
        d = self.objects[0].get_distance(pos)
        for i in range(1, len(self.objects)):
            d = max(d, -self.objects[i].get_distance(pos))
        return d

class Intersection(Container):
    def __init__(self, objects=[], transform=mat4()):
        super(Intersection, self).__init__(name="intersection", objects=objects, transform=transform)

    def __unicode__(self):
        return "Intersection(%s)" % self.objects

    def copy(self):
        return Intersection([o.copy() for o in self.objects], transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        if not self.objects:
            return INFINITY
        d = self.objects[0].get_distance(pos)
        for i in range(1, len(self.objects)):
            d = max(d, self.objects[i].get_distance(pos))
        return d



class DeformBase(CsgBase):
    def __init__(self, name, object, transform=mat4()):
        super(DeformBase, self).__init__(name, transform=transform)
        self.object = object

    def __unicode__(self):
        return "Deform(\"%s\", transform=%s, %s)" % (self.name, self.transform, self.object)


class Repeat(DeformBase):
    def __init__(self, object, repeat = vec3((1,0,0)), transform=mat4()):
        super(Repeat, self).__init__("repeat", object=object, transform=transform)
        self.repeat = vec3(repeat)

    def __unicode__(self):
        return "Repeat(%s, tranform=%s, %s)" % (self.repeat, self.transform, self.object)

    def copy(self):
        return Repeat(object = self.object.copy(), repeat=self.repeat, transform=self.transform)

    def get_distance(self, pos):
        p = self.pos_to_local(pos)
        for i in range(3):
            r = self.repeat[i]
            if r > 0.:
                p[i] = (p[i] + r*.5) % r - r*.5
        return self.object.get_distance(p)



class Primitive(CsgBase):
    def __init__(self, name, transform=mat4()):
        super(Primitive, self).__init__(name, transform=transform)

    def __unicode__(self):
        return "Primitive(\"%s\", transform=%s)" % (self.name, self.transform)


class Sphere(Primitive):
    def __init__(self, radius = 1., transform = mat4()):
        super(Sphere, self).__init__(name="sphere", transform=transform)
        self.radius = tools.check_float_number(radius)

    def __unicode__(self):
        return "Sphere(radius=%g, transform=%s)" % (self.radius, self.transform)

    def copy(self):
        return Sphere(radius=self.radius, transform=self.transform)

    def get_distance(self, pos):
        return self.pos_to_local(pos).length() - self.radius


class Cylinder(Primitive):
    def __init__(self, radius = 1., axis=0, transform = mat4()):
        super(Cylinder, self).__init__(name="sphere", transform=transform)
        self.radius = tools.check_float_number(radius)
        if axis < 0 or axis > 2:
            raise ValueError("Illegal axis argument %d" % axis)
        self.axis = axis

    def __unicode__(self):
        return "Cylinder(radius=%g, axis=%d, transform=%s)" % (self.radius, self.axis, self.transform)

    def copy(self):
        return Cylinder(radius=self.radius, axis=self.axis, transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        pos[self.axis] = 0.
        return pos.length() - self.radius



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


    #c = Difference([s, Sphere(radius=0.5, transform=mat4().translate((1.,0,0)))])

    stripes = Repeat(
            Cylinder(radius=.2, axis=1)#, transform=mat4().rotate_z(22.5).translate((2,0,0)))
            , repeat=vec3((1., 0, 0))
            , transform=mat4().rotate_z(45.)
        )
    c = Union([
        Difference([
            Cylinder(radius=1, axis=2),
            Cylinder(radius=.6, axis=2, transform=mat4().translate((0,0,0)))
        ]),
        Intersection([
            stripes.copy(),
            stripes.copy().set_transform(stripes.transform.rotate_y(180.))
        ])
    ]# , transform=mat4().translate((1,0,0))
    )
    print(c)
    print(c.get_distance((2,0,0)))

    try:
        import sys
        size = (int(sys.argv[1]), int(sys.argv[2]))
    except BaseException:
        size = (80, 10)
    try:
        scale = float(sys.argv[3])
    except BaseException:
        scale = .1
    print_slice(c, size=size, scale=scale)