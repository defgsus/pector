from .csg_base import *
from .glsl import to_glsl

class Primitive(CsgBase):
    def __init__(self, name, transform=mat4()):
        super(Primitive, self).__init__(name, transform=transform)
        self._can_have_nodes = False

    def __str__(self):
        return "Primitive(\"%s\", transform=%s)" % (self.name, self.transform)



class Sphere(Primitive):
    def __init__(self, radius = 1., transform = mat4()):
        super(Sphere, self).__init__(name="sphere", transform=transform)
        self.radius = tools.check_float_number(radius)

    def __str__(self):
        return "Sphere(radius=%g, transform=%s)" % (self.radius, self.transform)

    def copy(self):
        return Sphere(radius=self.radius, transform=self.transform)

    def get_distance(self, pos):
        return self.pos_to_local(pos).length() - self.radius

    def get_glsl_inline(self, pos):
        pos = self.get_glsl_transform(pos)
        return "length(%s) - %s" % (pos, to_glsl(self.radius))


class Tube(Primitive):
    def __init__(self, radius = 1., axis=0, transform = mat4()):
        super(Tube, self).__init__(name="sphere", transform=transform)
        self.radius = tools.check_float_number(radius)
        if axis < 0 or axis > 2:
            raise ValueError("Illegal axis argument %d" % axis)
        self.axis = axis

    def __str__(self):
        return "Tube(radius=%g, axis=%d, transform=%s)" % (self.radius, self.axis, self.transform)

    def copy(self):
        return Tube(radius=self.radius, axis=self.axis, transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        pos[self.axis] = 0.
        return pos.length() - self.radius

    def get_glsl_inline(self, pos):
        pos = self.get_glsl_transform(pos)
        swizz = "yz"
        if self.axis == 1:
            swizz = "xz"
        elif self.axis == 2:
            swizz = "xy"
        return "length(%s.%s) - %s" % (pos, swizz, to_glsl(self.radius))

