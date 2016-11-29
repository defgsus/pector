import math, tools, const

class vec3:

    def __init__(self, arg=None):
        if arg is None:
            self.v = [0., 0., 0.]
            return
        self.set(arg)

    def __unicode__(self):
        return "vec3(%g, %g, %g)" % (self.v[0], self.v[1], self.v[2])

    def __repr__(self):
        return self.__unicode__()

    @property
    def x(self):
        return self.v[0]
    @x.setter
    def x(self, arg):
        self.v[0] = float(arg)

    @property
    def y(self):
        return self.v[1]
    @y.setter
    def y(self, arg):
        self.v[1] = float(arg)

    @property
    def z(self):
        return self.v[2]
    @z.setter
    def z(self, arg):
        self.v[2] = float(arg)

    def __len__(self):
        return 3

    def __iter__(self):
        return self.v.__iter__()

    def __getitem__(self, item):
        return self.v[item]

    def __setitem__(self, key, value):
        self.v[key] = float(value)

    def __eq__(self, other):
        if isinstance(other, vec3):
            return self.v == other.v
        tools.check_float_sequence(other)
        if not len(other) == len(self):
            return False
        for i in range(len(self)):
            if not self.v[i] == other[i]:
                return False
        return True

    def __abs__(self):
        return vec3([abs(x) for x in self.v])

    def __neg__(self):
        return vec3([-x for x in self.v])

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
        return self._binary_operator(arg, lambda l, r: l * r)

    def __rmul__(self, arg):
        return self._binary_operator(arg, lambda r, l: l * r)

    def __imul__(self, arg):
        return self._binary_operator_inplace(arg, lambda l, r: l * r)


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


    def _binary_operator(self, arg, op):
        if tools.is_number(arg):
            fother = float(arg)
            return vec3([op(x, fother) for x in self.v])
        tools.check_float_sequence(arg, len(self))
        return vec3([op(x, float(arg[i])) for i, x in enumerate(self.v)])

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


    def set(self, arg):
        """
        Set the values of this vector
        :param arg: number or sequence
        :return: self

        >>> vec3(1)
        vec3(1, 1, 1)
        >>> vec3((1,2))
        vec3(1, 2, 0)
        >>> vec3((1,2,3))
        vec3(1, 2, 3)
        """
        if tools.is_number(arg):
            arg = float(arg)
            self.v = [arg, arg, arg]
            return self

        tools.check_float_sequence(arg)

        if len(arg) > len(self):
            raise TypeError("Sequence %s with length %d is too long for %s" % (type(arg), len(arg), type(self)))

        if len(arg) == len(self):
            self.v = [float(x) for x in arg]
            return self

        self.v = [x for x in arg]
        for i in range(len(self) - len(arg)):
            self.v.append(0.)

    def floor(self):
        self.v = [math.floor(x) for x in self.v]
        return self

    def dot(self, arg3):
        """
        Dot product of self and other vec3
        :param arg3: float sequence of length 3
        :return: float
        >>> vec3((1,2,3)).dot((4,5,6)) # (1*4)+(2*5)+(3*6)
        32.0
        """
        tools.check_float_sequence(arg3, len(self))
        return sum([x * float(arg3[i]) for i, x in enumerate(self.v)])

    def cross(self, arg3):
        tools.check_float_sequence(arg3)
        x = self.y * arg3[2] - self.z * arg3[1]
        y = self.z * arg3[0] - self.x * arg3[2]
        self.z = self.x * arg3[1] - self.y * arg3[0]
        self.x = x
        self.y = y
        return self

    def rotate_x(self, degree):
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        y = self.y * ca - self.z * sa
        self.z = self.y * sa + self.z * ca
        self.y = y
        return self

    def rotate_y(self, degree):
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        x = self.x * ca + self.z * sa
        self.z = -self.x * sa + self.z * ca
        self.x = x
        return self

    def rotate_z(self, degree):
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        x = self.x * ca - self.y * sa
        self.y = self.x * sa + self.y * ca
        self.x = x
        return self

    def rotate_axis(self, axis, degree):
        tools.check_float_sequence(axis, 3)
        degree *= const.DEG_TO_TWO_PI
        si = math.sin(degree)
        co = math.cos(degree)

        m = axis[0] * axis[0]+ axis[1] * axis[1] + axis[2] * axis[2]
        ms = math.sqrt(m)

        x = (axis[0] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.x * (axis[1] * axis[1] + axis[2] * axis[2]) + axis[0] * (-axis[1] * self.y - axis[2] * self.z))
            + si * ms * (-axis[2] * self.y + axis[1] * self.z)) / m
        y = (axis[1] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.y * (axis[0] * axis[0] + axis[2] * axis[2]) + axis[1] * (-axis[0] * self.x - axis[2] * self.z))
            + si * ms * (axis[2] * self.x - axis[0] * self.z)) / m
        self.z = (axis[2] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.z * (axis[0] * axis[0] + axis[1] * axis[1]) + axis[2] * (-axis[0] * self.x - axis[1] * self.y))
            + si * ms * (-axis[1] * self.x + axis[0] * self.y)) / m
        self.x = x
        self.y = y
        return self


if __name__ == "__main__":
    import doctest
    doctest.testmod()