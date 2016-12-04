from .csg_base import *
from .glsl import to_glsl

class DeformBase(CsgBase):
    def __init__(self, name, object=None, transform=mat4()):
        super(DeformBase, self).__init__(name, transform=transform)
        if object:
            self.add_node(object)

    def contained_object(self):
        return self.nodes[0] if len(self.nodes) else None


class Repeat(DeformBase):
    def __init__(self, object=None, repeat = vec3((1,0,0)), transform=mat4()):
        super(Repeat, self).__init__("repeat", object=object, transform=transform)
        self.repeat = vec3(repeat)

    def param_string(self):
        return "repeat=%s" % self.repeat

    def copy(self):
        return Repeat(object = self.nodes[0].copy(), repeat=self.repeat, transform=self.transform)

    def get_distance(self, pos):
        p = self.pos_to_local(pos)
        for i in range(3):
            r = self.repeat[i]
            if r > 0.:
                p[i] = (p[i] + r*.5) % r - r*.5
        return self.contained_object().get_distance(p)

    def get_glsl_inline(self, pos):
        return None

    def get_glsl_function_body(self):
        code = ""
        for i in range(3):
            r = self.repeat[i]
            if r > 0.:
                code += "pos.%(x)s = mod(pos.%(x)s + %(h)s, %(m)s) - %(h)s;\n" % {
                    "x": ("xyz")[i],
                    "m": to_glsl(r),
                    "h": to_glsl(r*.5),
                }
        pos = self.get_glsl_transform("pos")
        if not pos == "pos":
            code += "pos = %s;\n" % pos
        code += "return %s;" % self.contained_object().get_glsl("pos")
        return code
