from pector import vec3, mat4, tools
from .treenode import TreeNode
from .glsl import to_glsl

INFINITY = 1.0e+20


class GlslBase:

    def get_glsl_function_name(self):
        return "%s_%s" % (self.node_name, str(self.id))

    def get_glsl_function_body(self):
        return None

    def get_glsl_inline(self, pos):
        return None

    def get_glsl(self, pos):
        """Returns either get_glsl_inline() or a call to get_glsl_function_name()"""
        inl = self.get_glsl_inline(pos)
        if inl:
            return inl
        return "%s(%s)" % (self.get_glsl_function_name(), pos)

    def get_glsl_transform(self, pos):
        if self.has_transform:
            if not self.transform.has_translation():
                pos = "(%s * %s)" % (to_glsl(self.itransform.get_3x3()), pos)
            elif not self.transform.has_rotation():
                pos = "(%s + %s)" % (pos, to_glsl(self.itransform.position()))
            else:
                pos = "(%s * vec4(%s,1.)).xyz" % (to_glsl(self.itransform), pos)
        return pos



class CsgBase(TreeNode, GlslBase):
    def __init__(self, name, transform=mat4()):
        super(CsgBase, self).__init__(name)
        self._has_transform = transform != mat4()
        self._transform = mat4(transform)
        self._itransform = self._transform.inversed_simple()
        self._id = abs(self.__hash__())

    def __str__(self):
        p = self.param_string()
        if self.has_transform:
            if p:
                p += ", "
            p += "transform=%s" % self.transform
        return "%s(%s)" % (self.__class__.__name__, p)

    def param_string(self):
        raise NotImplementedError

    #def __repr__(self):
    #    return self.__str__()

    @property
    def id(self):
        return str(self._id)
    @property
    def transform(self):
        return self._transform
    @property
    def itransform(self):
        return self._itransform
    @transform.setter
    def transform(self, mat):
        self.set_transform(mat)
    def set_transform(self, mat):
        self._has_transform = mat != mat4()
        self._transform = mat4(mat)
        self._itransform = self._transform.inversed_simple()
        return self
    @property
    def has_transform(self):
        return self._has_transform

    def pos_to_local(self, pos):
        return self._itransform * pos if self.has_transform else vec3(pos)

    def get_glsl_static_functions(self):
        """Should return a list of helper functions, if needed."""
        return []

    def copy(self):
        raise NotImplementedError

    def get_distance(self, pos):
        raise NotImplementedError

    def get_normal(self, pos, e = 0.001):
        return vec3(
            self.get_distance(pos + (e, 0, 0)) - self.get_distance(pos - (e, 0, 0)),
            self.get_distance(pos + (0, e, 0)) - self.get_distance(pos - (0, e, 0)),
            self.get_distance(pos + (0, 0, e)) - self.get_distance(pos - (0, 0, e))
        ).normalize_safe()

    def sphere_trace(self, ro, rd):
        t = 0.
        for i in range(150):
            p = ro + rd * t
            d = self.get_distance(p)
            if d < 0.001:
                return t
            t += d
        return -1.





