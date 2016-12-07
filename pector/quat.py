import math
from pector import vec_base, tools, const, mat3

# some refs:
# http://www.cprogramming.com/tutorial/3d/quaternions.html


class quat(vec_base):
    """
    A 3D rotation/orientation quaternion
    It behaves like a list of floats of length 4
    Arguments to member functions can be any list-like objects,
    containing float-convertible elements,
    typically of length 4 as well.
    """
    def __init__(self, *arg):
        self.v = [1., 0., 0., 0.]
        if arg:
            self.set(*arg)

    def __unicode__(self):
        return "quat(%g, %g, %g, %g)" % (self.v[0], self.v[1], self.v[2], self.v[3])

    def __len__(self):
        return 4

    # ---- x,y,z properties ----

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

    @property
    def w(self):
        return self.v[3]
    @w.setter
    def w(self, arg):
        self.v[3] = float(arg)

    # ---- public API -----

    def set(self, *arg):
        if arg is None:
            self.v = [1.,0.,0., 0.]
            return self
        if len(arg) == 1:
            if tools.is_number(arg[0]):
                self.init_rotate_axis((1,0,0), float(arg[0]))
                return self
            if tools.is_float_sequence(arg[0]):
                tools.check_float_sequence(arg[0], 4)
                self.v = [float(x) for x in arg[0]]
                return self
        if len(arg) == 2:
            if tools.is_float_sequence(arg[0]) and len(arg[0]) == 3 and tools.is_number(arg[1]):
                self.init_rotate_axis(arg[0], float(arg[1]))
                return self
            if tools.is_float_sequence(arg[1]) and len(arg[1]) == 3 and tools.is_number(arg[0]):
                self.init_rotate_axis(arg[1], float(arg[0]))
                return self
        if len(arg) == 4:
            tools.check_float_sequence(arg, 4)
            self.v = [float(x) for x in arg]
            return self
        raise TypeError("Invalid arguments to quaternion, expected seq-4 or seq-3 + float, got %s" % type(arg))

    # ------- getter --------

    def as_mat3(self):
        x2 = self.x ** 2
        y2 = self.y ** 2
        z2 = self.z ** 2
        w2 = self.w ** 2
        return mat3( w2 + x2 - y2 - z2,  2.*self.x*self.y + 2.*self.w*self.z,  2.*self.x*self.z - 2.*self.w*self.y,
                     2.*self.x*self.y - 2.*self.w*self.z, w2-x2+y2-z2, 2.*self.y*self.z - 2.*self.w*self.x,
                     2.*self.x*self.z + 2.*self.w*self.y, 2.*self.y*self.z + 2.*self.w*self.x, w2-y2-y2+z2
        )

    # ------- arithmetic ops --------

    def __mul__(self, other):
        if tools.is_number(other):
            return self._binary_operator(float(other), lambda l, r: l * r)
        tools.check_float_sequence(other)
        q = quat()
        q.x = self.w * other[0] - self.x * other[3] - self.y * other[2] - self.z * other[1]
        q.y = self.w * other[1] + self.x * other[2] + self.y * other[3] - self.z * other[0]
        q.z = self.w * other[2] - self.x * other[1] + self.y * other[0] + self.z * other[3]
        q.w = self.w * other[3] + self.x * other[0] - self.y * other[1] + self.z * other[2]
        return q

    def __rmul__(self, other):
        if tools.is_number(other):
            return self._binary_operator(float(other), lambda r, l: l * r)
        tools.check_float_sequence(other)
        q = quat(other)
        return q.__mul__(self)

    def __imul__(self, other):
        q = self.__mul__(other)
        self.v = q.v
        return self

    # ------ inplace methods -------

    def init_rotate_axis(self, axis, degree):
        """
        Initialize the quaternion with a rotation around a 3d axis, INPLACE
        :param axis: The axis of rotation, must be normalized
        :param degree: The degrees of rotation [0.,360.]
        :return: self
        """
        tools.check_float_sequence(axis, 3)
        degree = float(degree) * const.DEG_TO_TWO_PI
        s = math.sin(degree)
        self.x = float(axis[0]) * s
        self.y = float(axis[1]) * s
        self.z = float(axis[2]) * s
        self.w = math.cos(degree)
        return self

    def rotate_axis(self, axis, degree):
        self.v = (quat().init_rotate_axis(axis, degree) * self.v).v
        return self

    # --- value-copying methods ---

    def rotated_axis(self, axis, degree):
        return quat().init_rotate_axis(axis, degree) * self.v



if __name__ == "__main__":
    import doctest
    doctest.testmod()
