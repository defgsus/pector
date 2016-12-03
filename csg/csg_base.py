from pector import vec3, mat4, tools
from .treenode import TreeNode


INFINITY = 1.0e+20


class GlslBase:

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



class CsgBase(TreeNode, GlslBase):
    def __init__(self, name, transform=mat4()):
        super(CsgBase, self).__init__(name)
        self._has_transform = transform != mat4()
        self._transform = mat4(transform)
        self._itransform = self._transform.inverted_simple()
        self._id = abs(self.__hash__())

    def __str__(self):
        return "CsgBase(\"%s\")" % self.node_name

    #def __repr__(self):
    #    return self.__str__()

    @property
    def id(self):
        return str(self._id)
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







