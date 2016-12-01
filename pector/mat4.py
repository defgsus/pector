import math
from pector import tools, const
from pector.vec3 import vec3


class mat4:
    """
    4x4 anisotropic matrix - column-major order
    """
    def __init__(self, arg=None):
        self.set(1. if arg is None else arg)

    def __unicode__(self):
        r = "mat4("
        for i, x in enumerate(self.v):
            r += "%g" % x
            if i < len(self)-1:
                r += ","
                if i % 4 == 3:
                    r += " "
        return r + ")"

    def __repr__(self):
        return self.__unicode__()

    def __len__(self):
        return 16

    def __iter__(self):
        return self.v.__iter__()

    def __getitem__(self, item):
        return self.v[item]

    def __setitem__(self, key, value):
        self.v[key] = float(value)

    def __eq__(self, other):
        if isinstance(other, mat4):
            return self.v == other.v
        tools.check_float_sequence(other)
        if not len(other) == len(self):
            return False
        for i in range(len(self)):
            if not self.v[i] == other[i]:
                return False
        return True

    def __abs__(self):
        return mat4([abs(x) for x in self.v])

    def __neg__(self):
        return mat4([-x for x in self.v])

    def __contains__(self, item):
        return item in self.v

    # ------- arithmetic ops --------

    def __add__(self, arg):
        return self._binary_operator(arg, lambda l, r: l + r)

    def __radd__(self, arg):
        return self._binary_operator(arg, lambda r, l: l + r)

    def __iadd__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l + r)


    def __sub__(self, arg):
        return self._binary_operator(arg, lambda l, r: l - r)

    def __rsub__(self, arg):
        return self._binary_operator(arg, lambda r, l: l - r)

    def __isub__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l - r)


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


    def __truediv__(self, arg):
        return self._binary_operator(arg, lambda l, r: l / r)

    def __rtruediv__(self, arg):
        return self._binary_operator(arg, lambda r, l: l / r)

    def __itruediv__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l / r)


    def __mod__(self, arg):
        return self._binary_operator(arg, lambda l, r: l % r)

    def __rmod__(self, arg):
        return self._binary_operator(arg, lambda r, l: l % r)

    def __imod__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l % r)


    # --- helper ---

    def _binary_operator(self, arg, op):
        if tools.is_number(arg):
            fother = float(arg)
            return mat4([op(x, fother) for x in self.v])
        tools.check_float_sequence(arg, len(self))
        return mat4([op(x, float(arg[i])) for i, x in enumerate(self.v)])

    def _binary_operator_inplace(self, arg, op):
        if tools.is_number(arg):
            fother = float(arg)
            for i in range(len(self)):
                self.v[i] = op(self.v[i], fother)
            return self
        tools.check_float_sequence(arg, len(self))
        for i in range(len(self)):
            self.v[i] = op(self.v[i], float(arg[i]))
        return self

    @classmethod
    def _multiply(cls, l, r):
        # mat4 * mat4
        if len(l) == 16 and len(r) == 16:
            r = mat4()
            for i in range(4):
                r.v[i +  0] = l[ 0] * r[i + 0] + l[ 1] * r[i + 4] + l[ 2] * r[i + 8] + l[ 3] * r[i + 12]
                r.v[i +  4] = l[ 4] * r[i + 0] + l[ 5] * r[i + 4] + l[ 6] * r[i + 8] + l[ 7] * r[i + 12]
                r.v[i +  8] = l[ 8] * r[i + 0] + l[ 9] * r[i + 4] + l[10] * r[i + 8] + l[11] * r[i + 12]
                r.v[i + 12] = l[12] * r[i + 0] + l[13] * r[i + 4] + l[14] * r[i + 8] + l[15] * r[i + 12]
            return r
        # mat4 * vec3
        elif len(l) == 16 and len(r) == 3:
            return vec3((
                l[0] * r[0] + l[4] * r[1] + l[8 ] * r[2] + l[12],
                l[1] * r[0] + l[5] * r[1] + l[9 ] * r[2] + l[13],
                l[2] * r[0] + l[6] * r[1] + l[10] * r[2] + l[14] ))
        else:
            raise TypeError("Can not matrix-multiply %s (%d) with %s (%d)" % (
                                type(l), len(l), type(r), len(r) ))

    def _multiply_inplace(self, m):
        sv = list(self.v)
        for i in range(4):
            self.v[i +  0] = sv[ 0] * m[i + 0] + sv[ 1] * m[i + 4] + sv[ 2] * m[i + 8] + sv[ 3] * m[i + 12]
            self.v[i +  4] = sv[ 4] * m[i + 0] + sv[ 5] * m[i + 4] + sv[ 6] * m[i + 8] + sv[ 7] * m[i + 12]
            self.v[i +  8] = sv[ 8] * m[i + 0] + sv[ 9] * m[i + 4] + sv[10] * m[i + 8] + sv[11] * m[i + 12]
            self.v[i + 12] = sv[12] * m[i + 0] + sv[13] * m[i + 4] + sv[14] * m[i + 8] + sv[15] * m[i + 12]
        return self

    # ----- public API getter ------

    def copy(self):
        """
        Returns a copy of the matrix
        :return: mat4
        """
        return mat4(self)

    def dot(self, arg):
        """
        Returns the dot product of self and other mat4
        :param arg: float sequence of length 16
        :return: float
        >>> mat4(1).dot(mat4(2))
        8.0
        """
        tools.check_float_sequence(arg, len(self))
        return sum([x * float(arg[i]) for i, x in enumerate(self.v)])

    def position(self):
        """
        Return translational (the last column) part as vec3
        :return: vec3
        >>> mat4().translated((2,3,4)).position()
        vec3(2, 3, 4)
        """
        return vec3(self.v[12:15])

    # ---- public API setter -----

    def set_identity(self, val=1.):
        """
        Sets the identity matrix
        :param val: The identity value, default = 1.
        :return: self
        >>> mat4().set_identity()
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
        >>> mat4().set_identity(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,2)
        """
        arg = tools.check_float_number(val)
        self.v = [arg, 0., 0., 0., 0., arg, 0., 0., 0., 0., arg, 0., 0., 0., 0., arg]
        return self

    def set(self, arg):
        """
        Sets the content of the matrix
        :param arg: either a float, to set the identity or a float sequence of length 16
        :return: self
        >>> mat4().set(1)
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)
        >>> mat4().set((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16))
        mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        """
        if tools.is_number(arg):
            arg = float(arg)
            self.v = [arg,0.,0.,0., 0.,arg,0.,0., 0.,0.,arg,0., 0.,0.,0.,arg]
            return self

        tools.check_float_sequence(arg, len(self))

        self.v = [float(x) for x in arg]
        return self

    def set_position(self, arg3):
        """
        Sets the translation-part of the matrix which is the last column
        :param arg3: a float sequence of length 3
        :return: self
        >>> mat4().set_position((2,3,4))
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 2,3,4,1)
        """
        tools.check_float_sequence(arg3, 3)
        self.v[12] = float(arg3[0])
        self.v[13] = float(arg3[1])
        self.v[14] = float(arg3[2])
        return self

    def floor(self):
        """
        Applies the floor() function to all elements, INPLACE
        :return: self
        >>> mat4((.1,.2,.3,.4, .5,.6,.7,.8, .9,1.,1.1,1.2, 1.3,1.4,1.5,1.6)).floor()
        mat4(0,0,0,0, 0,0,0,0, 0,1,1,1, 1,1,1,1)
        >>> mat4((-.1,-.2,-.3,-.4, -.5,-.6,-.7,-.8, -.9,-1.,-1.1,-1.2, -1.3,-1.4,-1.5,-1.6)).floor()
        mat4(-1,-1,-1,-1, -1,-1,-1,-1, -1,-1,-2,-2, -2,-2,-2,-2)
        """
        self.v = [math.floor(x) for x in self.v]
        return self

    def round(self):
        """
        Applies floor(+.5) to all elements, INPLACE
        :return: self
        >>> mat4((.1,.2,.3,.4, .5,.6,.7,.8, .9,1.,1.1,1.2, 1.3,1.4,1.5,1.6)).round()
        mat4(0,0,0,0, 1,1,1,1, 1,1,1,1, 1,1,2,2)
        >>> mat4((-.1,-.2,-.3,-.4, -.5,-.6,-.7,-.8, -.9,-1.,-1.1,-1.2, -1.3,-1.4,-1.5,-1.6)).round()
        mat4(0,0,0,0, 0,-1,-1,-1, -1,-1,-1,-1, -1,-1,-1,-2)
        """
        self.v = [math.floor(x+.5) for x in self.v]
        return self

    def transpose(self):
        """
        Exchanges the matrix columns and rows, INPLACE
        :return: self
        >>> mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transpose()
        mat4(1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)
        """
        self.v = [
            self.v[0], self.v[4], self.v[8], self.v[12],
            self.v[1], self.v[5], self.v[9], self.v[13],
            self.v[2], self.v[6], self.v[10], self.v[14],
            self.v[3], self.v[7], self.v[11], self.v[15]]
        return self


    def set_translate(self, arg3):
        """
        Initializes the matrix with a translation transform, INPLACE
        :param arg3: a float sequence of lengh 3
        :return: self
        >>> mat4(1).set_translate((2,3,4))
        mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 2,3,4,1)
        """
        tools.check_float_sequence(arg3, 3)
        self.set_identity()
        self.v[12] = float(arg3[0])
        self.v[13] = float(arg3[1])
        self.v[14] = float(arg3[2])
        return self

    def set_scale(self, arg):
        """
        Initializes the matrix with a scale transform, INPLACE
        :param arg: either a float or a float sequence of length 3
        :return: self
        >>> mat4().set_scale(2)
        mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,1)
        >>> mat4().set_scale((2,3,4))
        mat4(2,0,0,0, 0,3,0,0, 0,0,4,0, 0,0,0,1)
        """
        if tools.is_number(arg):
            self.set(arg)
            self.v[15] = 1.
            return self
        tools.check_float_sequence(arg, 3)
        self.set_identity()
        self.v[0] = float(arg[0])
        self.v[5] = float(arg[1])
        self.v[10] = float(arg[2])
        return self

    def set_rotate_x(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_x(90).round()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[5] = ca
        self.v[6] = sa
        self.v[9] = -sa
        self.v[10] = ca
        return self

    def set_rotate_y(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_y(90).round()
        mat4(0,0,-1,0, 0,1,0,0, 1,0,0,0, 0,0,0,1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[0] = ca
        self.v[2] = -sa
        self.v[8] = sa
        self.v[10] = ca
        return self

    def set_rotate_z(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_z(90).round()
        mat4(0,1,0,0, -1,0,0,0, 0,0,1,0, 0,0,0,1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[0] = ca
        self.v[1] = sa
        self.v[4] = -sa
        self.v[5] = ca
        return self

    def set_rotate_axis(self, axis, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param axis: float sequence of length 3, must be normalized!
        :param degree: degrees of rotation
        :return: self
        >>> mat4().set_rotate_axis((1,0,0), 90).round()
        mat4(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1)
        """
        tools.check_float_sequence(axis, 3)
        degree *= const.DEG_TO_TWO_PI
        si = math.sin(degree)
        co = math.cos(degree)
        m = 1. - co

        self.set_identity()
        self.v[0] =  co + axis[0] * axis[0] * m
        self.v[5] =  co + axis[1] * axis[1] * m
        self.v[10] = co + axis[2] * axis[2] * m

        t1 = axis[0] * axis[1] * m
        t2 = axis[2] * si
        self.v[1] = t1 + t2
        self.v[4] = t1 - t2

        t1 = axis[0] * axis[2] * m
        t2 = axis[1] * si
        self.v[2] = t1 - t2
        self.v[8] = t1 + t2

        t1 = axis[1] * axis[2] * m
        t2 = axis[0] * si
        self.v[6] = t1 + t2
        self.v[9] = t1 - t2
        return self


    def translate(self, arg3):
        m = mat4().set_translate(arg3)
        self._multiply_inplace(m)
        return self

    def scale(self, arg):
        m = mat4().set_scale(arg)
        self._multiply_inplace(m)
        return self

    def rotate_x(self, degree):
        m = mat4().set_rotate_x(degree)
        self._multiply_inplace(m)
        return self

    def rotate_y(self, degree):
        m = mat4().set_rotate_y(degree)
        self._multiply_inplace(m)
        return self

    def rotate_z(self, degree):
        m = mat4().set_rotate_z(degree)
        self._multiply_inplace(m)
        return self

    def rotate_axis(self, axis, degree):
        m = mat4().set_rotate_axis(axis, degree)
        self._multiply_inplace(m)
        return self

    # ------ value-copying methods -------

    def transposed(self):
        """
        Returns a mat4 with columns and rows interchanged
        :return: self
        >>> mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transposed()
        mat4(1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)
        """
        return self.copy().transpose()

    def translated(self, arg3):
        return self.copy().translate(arg3)

    def scaled(self, arg):
        return self.copy().scale(arg)

    def rotated_x(self, degree):
        return self.copy().rotate_x(degree)

    def rotated_y(self, degree):
        return self.copy().rotate_y(degree)

    def rotated_z(self, degree):
        return self.copy().rotate_z(degree)

    def rotated_axis(self, axis, degree):
        return self.copy().rotate_axis(axis, degree)

if __name__ == "__main__":
    import doctest
    doctest.testmod()