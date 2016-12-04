from .csg_base import *
from .glsl import to_glsl

class CombineBase(CsgBase):
    def __init__(self, name, objects=[], transform=mat4()):
        super(CombineBase, self).__init__(name=name, transform=transform)
        for i in objects:
            self.add_node(i)

    def __str__(self):
        return "CombineBase(\"%s\", %s)" % (self.node_name, self.nodes)

    def get_glsl_inline(self, pos):
        pos = self.get_glsl_transform(pos)
        if len(self.nodes) == 0:
            return "%s" % to_glsl(INFINITY)
        if len(self.nodes) == 1:
            return self.nodes[0].get_glsl(pos)
        if len(self.nodes) == 2:
            return self.get_glsl_operation() % (self.nodes[0].get_glsl(pos), self.nodes[1].get_glsl(pos))
        return None

    def get_glsl_function_body(self):
        if len(self.nodes) <= 2:
            return None
        pos = self.get_glsl_transform("pos")
        code = "float d = %s;\n" % self.nodes[0].get_glsl(pos)
        for i in range(1, len(self.nodes)):
            code += ("d = %s;\n" % self.get_glsl_operation()) % ("d", self.nodes[i].get_glsl(pos))
        return code

    def get_glsl_operation(self):
        return None


class Union(CombineBase):
    def __init__(self, objects=[], transform=mat4()):
        super(Union, self).__init__(name="union", objects=objects, transform=transform)

    def __str__(self):
        return "Union(%s)" % self.nodes

    def copy(self):
        return Union([o.copy() for o in self.nodes], transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        d = INFINITY
        for i in self.nodes:
            d = min(d, i.get_distance(pos))
        return d

    def get_glsl_operation(self):
        return "min(%s, %s)"


class Difference(CombineBase):
    def __init__(self, objects=[], transform=mat4()):
        super(Difference, self).__init__(name="difference", objects=objects, transform=transform)

    def __str__(self):
        return "Difference(%s)" % self.nodes

    def copy(self):
        return Difference([o.copy() for o in self.nodes], transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        if not self.nodes:
            return INFINITY
        d = self.nodes[0].get_distance(pos)
        for i in range(1, len(self.nodes)):
            d = max(d, -self.nodes[i].get_distance(pos))
        return d

    def get_glsl_operation(self):
        return "max(%s, -(%s))"


class Intersection(CombineBase):
    def __init__(self, objects=[], transform=mat4()):
        super(Intersection, self).__init__(name="intersection", objects=objects, transform=transform)

    def __str__(self):
        return "Intersection(%s)" % self.nodes

    def copy(self):
        return Intersection([o.copy() for o in self.nodes], transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        if not self.nodes:
            return INFINITY
        d = self.nodes[0].get_distance(pos)
        for i in range(1, len(self.nodes)):
            d = max(d, self.nodes[i].get_distance(pos))
        return d

    def get_glsl_operation(self):
        return "max(%s, %s)"


