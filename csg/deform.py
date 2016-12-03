from .csg_base import *
from .glsl import to_glsl

class DeformBase(CsgBase):
    def __init__(self, name, object, transform=mat4()):
        super(DeformBase, self).__init__(name, transform=transform)
        self.add_node(object)

    def __str__(self):
        return "Deform(\"%s\", transform=%s, %s)" % (self.name, self.transform, self.object)

    def contained_object(self):
        return self.nodes[0] if len(self.nodes) else None


class Repeat(DeformBase):
    def __init__(self, object, repeat = vec3((1,0,0)), transform=mat4()):
        super(Repeat, self).__init__("repeat", object=object, transform=transform)
        self.repeat = vec3(repeat)

    def __str__(self):
        return "Repeat(%s, tranform=%s, %s)" % (self.repeat, self.transform, self.contained_object())

    def copy(self):
        return Repeat(object = self.nodes[0].copy(), repeat=self.repeat, transform=self.transform)

    def get_distance(self, pos):
        p = self.pos_to_local(pos)
        for i in range(3):
            r = self.repeat[i]
            if r > 0.:
                p[i] = (p[i] + r*.5) % r - r*.5
        return self.contained_object().get_distance(p)


    def get_glsl_inline(self):
        return None

    def get_glsl_function(self):
        code = ""
        for i in range(3):
            r = self.repeat[i]
            if r > 0.:
                code += "pos.%(x)s = mod(pos.%(x)s + %(h)s, %(m)s) - %(h)s;\n" % {
                    "x": ("xyz")[i],
                    "m": to_glsl(r),
                    "h": to_glsl(r*.5),
                }
        code += "return %s;" % self.contained_object().get_glsl()
        return code
