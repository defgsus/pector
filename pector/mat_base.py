# import math
from pector import tools, vec_base, vec3

class mat_base(vec_base):
    """
    Base class for common matrix operations
    """
    def __init__(self, *arg):
        self.set(*arg)

    def __unicode__(self):
        r = "%s(" % self.__class__.__name__
        for i, x in enumerate(self.v):
            r += "%g" % x
            if i < len(self)-1:
                r += ","
                if i % self.num_rows() == 3:
                    r += " "
        return r + ")"

    def num_rows(self):
        raise NotImplementedError

    # ------- arithmetic ops --------

    def __mul__(self, arg):
        if tools.is_number(arg):
            return self._binary_operator(arg, lambda l, r: l * r)
        tools.check_float_sequence(arg)
        return self._multiply(self, arg)

    def __rmul__(self, arg):
        if tools.is_number(arg):
            return self._binary_operator(arg, lambda r, l: l * r)
        tools.check_float_sequence(arg)
        return self._multiply(arg, self)

    def __imul__(self, arg):
        if tools.is_number(arg):
            return self._binary_operator_inplace(arg, lambda l, r: l * r)
        tools.check_float_sequence(arg, len(self))
        return self._multiply_inplace(self, arg)

    # --- helper ---

    def _multiply(self, l, r):
        # mat * mat
        if len(l) == len(self) == len(r):
            m = self.__class__(l)
            m._multiply_inplace(r)
            return m
        # mat4 * vec3
        elif len(l) == 16 and len(r) == 3:
            return vec3.vec3(
                l[0] * r[0] + l[4] * r[1] + l[8 ] * r[2] + l[12],
                l[1] * r[0] + l[5] * r[1] + l[9 ] * r[2] + l[13],
                l[2] * r[0] + l[6] * r[1] + l[10] * r[2] + l[14] )
        else:
            raise TypeError("Can not matrix-multiply %s (%d) with %s (%d)" % (
                                type(l), len(l), type(r), len(r) ))

    def _multiply_inplace(self, m):
        sv = list(self.v)
        for row in range(self.num_rows()):
            for col in range(self.num_rows()):
                s = 0.
                for i in range(self.num_rows()):
                    s += sv[row + i * self.num_rows()] * m.v[i + col * self.num_rows()]
                self.v[row + col * self.num_rows()] = s
        return self

    # ----- public API getter ------

    def has_translation(self):
        """
        Returns True if the matrix contains a translation, False otherwise
        :return: bool
        """
        return len(self) == 16 and not (self.v[12] == 0. and self.v[13] == 0. and self.v[14] == 0.)

    def has_rotation(self):
        """
        Returns True if the matrix contains a rotation or skew transform, False otherwise
        :return: bool
        """
        num = min(3, self.num_rows())
        for r in range(num):
            for c in range(num):
                if not r == c and not self.v[c*self.num_rows()+r] == 0:
                    return True
        return False

    # ---- public API setter -----

    def set_identity(self, value=1.):
        """
        Sets the identity matrix
        :param value: The identity value, default = 1.
        :return: self
        >>> mat4().set_identity()
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
        >>> mat4().set_identity(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,2)
        """
        arg = tools.check_float_number(value)
        self.v = [arg if i % (self.num_rows()+1) == 0 else 0. for i in range(len(self))]
        return self

    def set(self, *arg):
        """
        Sets the content of the matrix
        :param arg: either a float, to set the identity or a float sequence of length 16
        :return: self
        >>> mat4().set(1)
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
        >>> mat4().set(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        >>> mat4().set((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16))
        mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        """
        if arg and len(arg) == 1 and tools.is_number(arg[0]):
            self.set_identity(float(arg[0]))
            return self
        if not arg:
            self.set_identity(1.)
            return self
        return super(mat_base, self).set(*arg)

    def transpose(self):
        """
        Exchanges the matrix columns and rows, INPLACE
        :return: self
        >>> mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transpose()
        mat4(1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)
        """
        self.v = [self.v[row + i*self.num_rows()] for row in range(self.num_rows()) for i in range(self.num_rows())]
        return self

    def init_scale(self, arg):
        """
        Initializes the matrix with a scale transform, INPLACE
        :param arg: either a float or a float sequence of length 3
        :return: self
        >>> mat4().init_scale(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,1)
        >>> mat4().init_scale((2,3,4))
        mat4(2,0,0,0, 0,3,0,0, 0,0,4,0, 0,0,0,1)
        """
        if tools.is_number(arg):
            self.set(arg)
            if self.num_rows() > 3:
                self.v[-1] = 1.
            return self
        tools.check_float_sequence(arg, self.num_rows()-1)
        self.set_identity()
        num = self.num_rows()-1 if self.num_rows() > 3 else self.num_rows()
        for i in range(num):
            self.v[i * (self.num_rows()+1)] = float(arg[i])
        return self


    def scale(self, arg):
        """
        Scales the current matrix, INPLACE
        :param arg3: single float or float sequence of length 3
        :return: self
        >>> mat4().scale(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,1)
        >>> mat4().scale((2,3,4))
        mat4(2,0,0,0, 0,3,0,0, 0,0,4,0, 0,0,0,1)
        """
        m = self.__class__().init_scale(arg)
        self._multiply_inplace(m)
        return self


    # ------ value-copying methods -------

    def transposed(self):
        """
        Returns a mat4 with columns and rows interchanged
        :return: new matrix
        >>> mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transposed()
        mat4(1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)
        """
        return self.copy().transpose()

    def scaled(self, arg):
        """
        Returns a scaled matrix
        :param arg3: single float or float sequence of length 3
        :return: new matrix
        >>> mat4().scaled(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,1)
        >>> mat4().scaled((2,3,4))
        mat4(2,0,0,0, 0,3,0,0, 0,0,4,0, 0,0,0,1)
        """
        return self.copy().scale(arg)
