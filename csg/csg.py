from pector import vec3, mat4, tools

INFINITY = 1.0e+20


def to_glsl(arg):
    if tools.is_number(arg):
        s = str(arg)
        if not '.' in s:
            s += '.'
        return s
    if isinstance(arg, vec3):
        return "vec3(%s, %s, %s)" % (to_glsl(arg[0]), to_glsl(arg[1]), to_glsl(arg[2]))
    return str(arg)



class TreeNode:
    def __init__(self, name):
        self._node_name = name
        self._nodes = []
        self._node_parent = None
        self._can_have_nodes = True

    def __repr__(self):
        return 'TreeNode("%s")' % self._node_name

    @property
    def node_name(self):
        return self._node_name
    @property
    def nodes(self):
        return self._nodes
    @property
    def node_parent(self):
        return self._node_parent
    @property
    def node_root(self):
        return self if not self._node_parent else self._node_parent.node_root

    def add_node(self, node):
        if not self._can_have_nodes:
            raise ValueError("Can not add nodes to %s" % repr(self))
        if not isinstance(node, TreeNode):
            raise TypeError("Can not add non-TreeNode object %s" % type(node))
        this_nodes = self.node_root.nodes_to_set()
        if node in this_nodes:
            raise ValueError("Can not add the same node twice: %s" % repr(node))
        if this_nodes & node.node_root.nodes_to_set():
            raise ValueError("Can not add the node because it contains a mutual node")
        self._nodes.append(node)
        node._node_parent = self

    def contains_node(self, node):
        if node in self._nodes:
            return True
        for o in self._nodes:
            if o.contains_node(node):
                return True
        return False

    def nodes_to_set(self):
        s = set((self,))
        for o in self._nodes:
            s |= o.nodes_to_set()
        return s


class CsgBase(TreeNode):
    def __init__(self, name, transform=mat4()):
        super(CsgBase, self).__init__(name)
        self._has_transform = transform != mat4()
        self._transform = mat4(transform)
        self._itransform = self._transform.inverted_simple()
        self._id = None

    def __unicode__(self):
        return "CsgBase(\"%s\")" % self.node_name

    #def __repr__(self):
    #    return self.__unicode__()

    @property
    def id(self):
        return str(abs(self.__hash__()))
    @property
    def transform(self):
        return self._transform
    @transform.setter
    def transform(self, mat):
        self.set_transform(mat)
    def set_transform(self, mat):
        self._has_transform = mat != mat4()
        self._transform = mat4(mat)
        self._itransform = self._transform.inverted_simple()
        return self
    @property
    def has_transform(self):
        return self._has_transform

    def pos_to_local(self, pos):
        return self._itransform * pos if self.has_transform else vec3(pos)

    def copy(self):
        raise NotImplementedError

    def get_distance(self, pos):
        raise NotImplementedError

    def get_glsl_function_name(self):
        return "%s_%s" % (self.node_name, str(self.id))

    def get_glsl_function(self):
        return None

    def get_glsl_inline(self):
        return None

    def get_glsl(self):
        """Returns either get_glsl_inline() or a call to get_glsl_function_name()"""
        inl = self.get_glsl_inline()
        if inl:
            return inl
        return "%s(pos)" % self.get_glsl_function_name()


class Combiner(CsgBase):
    def __init__(self, name, objects=[], transform=mat4()):
        super(Combiner, self).__init__(name=name, transform=transform)
        for i in objects:
            self.add_node(i)

    def __unicode__(self):
        return "Combiner(\"%s\", %s)" % (self.node_name, self.nodes)



class Union(Combiner):
    def __init__(self, objects=[], transform=mat4()):
        super(Union, self).__init__(name="union", objects=objects, transform=transform)

    def __unicode__(self):
        return "Union(%s)" % self.nodes

    def copy(self):
        return Union([o.copy() for o in self.nodes], transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        d = INFINITY
        for i in self.nodes:
            d = min(d, i.get_distance(pos))
        return d

    def get_glsl_inline(self):
        if len(self.nodes) == 1:
            return self.nodes[0].get_glsl()
        if len(self.nodes) == 2:
            return "min(%s, %s)" % (self.nodes[0].get_glsl(), self.nodes[1].get_glsl())
        return None

    def get_glsl_function(self):
        if len(self.nodes) <= 2:
            return None
        code = "float d = %s;\n" % self.nodes[0].get_glsl()
        for i in range(1, len(self.nodes)):
            code += "d = min(d, %s);\n" % self.nodes[i].get_glsl()
        return code


class Difference(Combiner):
    def __init__(self, objects=[], transform=mat4()):
        super(Difference, self).__init__(name="difference", objects=objects, transform=transform)

    def __unicode__(self):
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


class Intersection(Combiner):
    def __init__(self, objects=[], transform=mat4()):
        super(Intersection, self).__init__(name="intersection", objects=objects, transform=transform)

    def __unicode__(self):
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



class DeformBase(CsgBase):
    def __init__(self, name, object, transform=mat4()):
        super(DeformBase, self).__init__(name, transform=transform)
        self.object = None
        self.set_object(object)

    def set_object(self, object):
        if self.node_root.contains_sub(object):
            raise ValueError("Can not add the same instance twice: %s" % object)
        object._parent = self
        self.object = object

    def __unicode__(self):
        return "Deform(\"%s\", transform=%s, %s)" % (self.name, self.transform, self.object)

    def contains_sub(self, obj):
        return obj is self.object or (self.object and self.object.contains_sub(obj))


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
        self._can_have_nodes = False

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

    def get_glsl_inline(self):
        return "length(pos) - %s" % (to_glsl(self.radius))


class Tube(Primitive):
    def __init__(self, radius = 1., axis=0, transform = mat4()):
        super(Tube, self).__init__(name="sphere", transform=transform)
        self.radius = tools.check_float_number(radius)
        if axis < 0 or axis > 2:
            raise ValueError("Illegal axis argument %d" % axis)
        self.axis = axis

    def __unicode__(self):
        return "Tube(radius=%g, axis=%d, transform=%s)" % (self.radius, self.axis, self.transform)

    def copy(self):
        return Tube(radius=self.radius, axis=self.axis, transform=self.transform)

    def get_distance(self, pos):
        pos = self.pos_to_local(pos)
        pos[self.axis] = 0.
        return pos.length() - self.radius

    def get_glsl_inline(self):
        swizz = "yz"
        if self.axis == 1:
            swizz = "xz"
        elif self.axis == 2:
            swizz = "xy"
        return "length(pos.%s) - %s" % (swizz, to_glsl(self.radius))



if __name__ == "__main__":

    def print_slice(csg, center=(0., 0.), size=(20,20), scale=.1):
        chars = [' ', '.', ':', '+', '*', '#']
        crange = 0.07
        scaley = scale * size[1] * 2.
        scalex = scale * size[0]
        scale = scale * max(size[0], size[1])
        for j in range(size[1]):
            y = (.5 - j / size[1]) * scaley + center[1]
            for i in range(size[0]):
                x = (i / size[0] - .5) * scalex + center[0]
                d = csg.get_distance((x,y,0.)) - crange*.5
                idx = max(0,min(len(chars)-1, int(len(chars)*(1. - d / crange))))
                print(chars[idx], end="")
            print("")


    #c = Difference([s, Sphere(radius=0.5, transform=mat4().translate((1.,0,0)))])

    stripes = Repeat(
            Tube(radius=.1, axis=1)#, transform=mat4().rotate_z(22.5).translate((2,0,0)))
            , repeat=vec3((1., 0, 0))
            , transform=mat4().rotate_z(45.)
        )
    c = Union([
        Difference([
            Tube(radius=1, axis=2),
            Tube(radius=.6, axis=2, transform=mat4().translate((0, 0, 0)))
        ]),
        Intersection([
            stripes.copy(),
            stripes.copy().set_transform(stripes.transform.rotate_y(180.))
        ]),
        Difference([
            stripes.copy().set_transform(mat4().scale(1.)),
            Tube(radius=2.8, axis=2)
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
    #print(stripes is stripes.set_transform(mat4(2)))

    print(c.get_glsl())
