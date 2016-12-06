import math
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

    def get_glsl_static_functions(self):
        return ["""
vec3 repeat_transform(in vec3 pos, in vec3 repeat) {
    if (repeat.x > 0.) pos.x = mod(pos.x + repeat.x/2., repeat.x) - repeat.x/2.;
    if (repeat.y > 0.) pos.y = mod(pos.y + repeat.y/2., repeat.y) - repeat.y/2.;
    if (repeat.z > 0.) pos.z = mod(pos.z + repeat.z/2., repeat.z) - repeat.z/2.;
    return pos;
}
"""]

    def get_glsl_inline(self, pos):
        return self.contained_object().get_glsl(
            "repeat_transform(%s, %s)" % (self.get_glsl_transform(pos), to_glsl(self.repeat))
        )

    def get_glsl_function_body(self):
        return None

class Fan(DeformBase):
    def __init__(self, object=None, angle = (0., 30.), axis=0, transform=mat4()):
        """
        :param object:
        :param angle: tuple with (center, range) in degrees
        :param axis: 0, 1 or 2
        :param transform:
        """
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
        pos = self.pos_to_local(pos)

        start = DEG_TO_TWO_PI * (self.angle[0] - self.angle[1]/2.)
        end = DEG_TO_TWO_PI * (self.angle[0] + self.angle[1]/2.)
        len = end - start

        swizz0, swizz1 = (0, 1)
        if self.axis == 0:
            swizz0, swizz1 = (1,2)
        elif self.axis == 1:
            swizz0, swizz1 = (0,2)

        ang = math.atan2(pos[swizz0], pos[swizz1])
        leng = math.sqrt(pos[swizz0]*pos[swizz0] + pos[swizz1]*pos[swizz1])
        ang = (ang - start) % len - len/2
        pos[swizz0] = leng * math.sin(ang)
        pos[swizz1] = leng * math.cos(ang)
        return self.contained_object().get_distance(pos)

    def get_swizzle(self):
        swizz = "xy"
        if self.axis == 0:
            swizz = "yz"
        elif self.axis == 1:
            swizz = "xz"
        return swizz

    def get_glsl_static_functions(self):
        swizz = self.get_swizzle()
        code = """
vec3 fan_transform_%(swizz)s(in vec3 pos, in float center, in float range) {
    float start = (center - range/2.) * %(D2P)s,
          m = (range) * %(D2P)s,
          ang = atan(pos.%(swizz0)s, pos.%(swizz1)s),
          len = length(pos.%(swizz)s);
    ang = mod(ang - start, m) - m/2.;
    pos.%(swizz)s = len * vec2(sin(ang), cos(ang));
    return pos;
}""" % {    "D2P": to_glsl(DEG_TO_TWO_PI),
            "swizz": swizz,
            "swizz0": swizz[0],
            "swizz1": swizz[1],
            }
        return [code]

    def get_glsl_inline(self, pos):
        return self.contained_object().get_glsl(
            "fan_transform_%s(%s, %s, %s)" % (self.get_swizzle(), self.get_glsl_transform(pos),
                                              to_glsl(float(self.angle[0])),
                                              to_glsl(float(self.angle[1])))
        )

    def get_glsl_function_body(self):
        return None




class DeformFunction(DeformBase):
    def __init__(self, object=None, py_func=lambda pos: pos, glsl_func="pos = pos;", transform=mat4()):
        super(DeformFunction, self).__init__("fan", object=object, transform=transform)
        self.py_func = py_func
        self.glsl_func = glsl_func

    def param_string(self):
        return "glsl_func=%s, py_func=%s" % (self.glsl_func, self.py_func)

    def copy(self):
        return DeformFunction(object = self.nodes[0].copy(), py_func=self.py_func,
                              glsl_func=self.glsl_func, transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        pos = self.py_func(pos)
        return self.contained_object().get_distance(pos)

    def get_glsl_inline(self, pos):
        return None

    def get_glsl_function_body(self):
        code = self.glsl_func
        if not code.endswith("\n"):
            code += "\n"
        code += "return %s;\n" % self.contained_object().get_glsl("pos")
        return code




"""
hexa-repeat
vec3 img(in vec2 uv)
{
    vec3 col = vec3(0.);
    col.xz = sin(uv.xy*10.);

    col.y = smoothstep(0.01,0., length(uv.xy)-0.1);

    return col;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 uv = fragCoord.xy / iResolution.xy * 2. - 1.;
    uv.x *= iResolution.x/iResolution.y;

    vec2 q = vec2(.5, .46);
    float a = 3.1416/4.;
    mat2 r = mat2(cos(a),-sin(a),sin(a),cos(a));

    uv.x += mod(uv.y+q.y/2., q.y*2.) < q.y ? 0. : q.x/2.;
    uv = (mod(uv+q/2.,q)-q/2.);

	fragColor = vec4(img(uv),1.0);
}"""