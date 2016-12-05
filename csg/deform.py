from .csg_base import *
from .glsl import to_glsl
from pector.const import DEG_TO_TWO_PI

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
        pos = self.get_glsl_transform("pos")
        if not pos == "pos":
            code += "pos = %s;\n" % pos
        for i in range(3):
            r = self.repeat[i]
            if r > 0.:
                code += "pos.%(x)s = mod(pos.%(x)s + %(h)s, %(m)s) - %(h)s;\n" % {
                    "x": ("xyz")[i],
                    "m": to_glsl(r),
                    "h": to_glsl(r*.5),
                }
        code += "return %s;" % self.contained_object().get_glsl("pos")
        return code


class Fan(DeformBase):
    def __init__(self, object=None, angle = (-15., 15.), axis=0, transform=mat4()):
        super(Fan, self).__init__("fan", object=object, transform=transform)
        self.angle = angle
        if axis < 0 or axis > 2:
            raise ValueError("Illegal axis argument %d" % axis)
        self.axis = axis

    def param_string(self):
        return "angle=%s, axis=%d" % (self.angle, self.axis)

    def copy(self):
        return Fan(object = self.nodes[0].copy(), angle=self.angle, axis=self.axis, transform=self.transform)

    def get_distance(self, pos):
        raise NotImplementedError

    def get_glsl_inline(self, pos):
        return None

    def get_glsl_function_body(self):
        code = ""
        pos = self.get_glsl_transform("pos")
        if not pos == "pos":
            code += "pos = %s;\n" % pos

        swizz = "xy"
        if self.axis == 0:
            swizz = "yz"
        elif self.axis == 1:
            swizz = "xz"

        start = DEG_TO_TWO_PI * self.angle[0]
        end = DEG_TO_TWO_PI * self.angle[1]
        len = end - start

        code += """
float ang = atan(pos.%(swizz0)s, pos.%(swizz1)s),
      len = length(pos.%(swizz)s);
ang = mod(ang - %(start)s, %(len)s) - %(len2)s;
pos.%(swizz)s = len * vec2(sin(ang), cos(ang));
return %(call)s;""" % {
            "call": self.contained_object().get_glsl("pos"),
            "start": to_glsl(start),
            "len": to_glsl(len),
            "len2": to_glsl(len/2.),
            "swizz": swizz,
            "swizz0": swizz[0],
            "swizz1": swizz[1]
        }
        return code
