import math
from pector import tools, const, mat_base


class mat3(mat_base):
    """
    3x3 transformation matrix - column-major order
    """

    def __len__(self):
        return 9

    def num_rows(self):
        return 3

    # ----- public API getter ------


    # ---- public API setter -----

    def inverse_simple(self):
        """
        Inverts a uniformly-scaled, non-skewed matrix, INPLACE
        :return: self
        """
        self.v = self.inversed_simple().v
        return self

    def init_rotate_x(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat3().init_rotate_x(90).round()
        mat3(1,0,0, 0,0,1, 0,-1,0)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[4] = ca
        self.v[5] = sa
        self.v[7] = -sa
        self.v[8] = ca
        return self

    def init_rotate_y(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat3().init_rotate_y(90).round()
        mat3(0,0,-1, 0,1,0, 1,0,0)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[0] = ca
        self.v[2] = -sa
        self.v[6] = sa
        self.v[8] = ca
        return self

    def init_rotate_z(self, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param degree: degrees of rotation
        :return: self
        >>> mat3().init_rotate_z(90).round()
        mat3(0,1,0, -1,0,0, 0,0,1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        self.set_identity()
        self.v[0] = ca
        self.v[1] = sa
        self.v[3] = -sa
        self.v[4] = ca
        return self

    def init_rotate_axis(self, axis, degree):
        """
        Initializes the matrix with a rotation transform, INPLACE
        :param axis: float sequence of length 3, must be normalized!
        :param degree: degrees of rotation
        :return: self
        >>> mat3().init_rotate_axis((1,0,0), 90).round()
        mat3(1,0,0, 0,0,1, 0,-1,0)
        """
        tools.check_float_sequence(axis, 3)
        degree *= const.DEG_TO_TWO_PI
        si = math.sin(degree)
        co = math.cos(degree)
        m = 1. - co

        self.set_identity()
        self.v[0] =  co + axis[0] * axis[0] * m
        self.v[4] =  co + axis[1] * axis[1] * m
        self.v[8] = co + axis[2] * axis[2] * m

        t1 = axis[0] * axis[1] * m
        t2 = axis[2] * si
        self.v[1] = t1 + t2
        self.v[3] = t1 - t2

        t1 = axis[0] * axis[2] * m
        t2 = axis[1] * si
        self.v[2] = t1 - t2
        self.v[6] = t1 + t2

        t1 = axis[1] * axis[2] * m
        t2 = axis[0] * si
        self.v[5] = t1 + t2
        self.v[7] = t1 - t2
        return self


    def rotate_x(self, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param degree: angle of rotation in degree
        :return: self
        >>> mat3().rotate_x(90).round()
        mat3(1,0,0, 0,0,1, 0,-1,0)
        """
        m = mat3().init_rotate_x(degree)
        self._multiply_inplace(m)
        return self

    def rotate_y(self, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param degree: angle of rotation in degree
        :return: self
        >>> mat3().rotate_y(90).round()
        mat3(0,0,-1, 0,1,0, 1,0,0)
        """
        m = mat3().init_rotate_y(degree)
        self._multiply_inplace(m)
        return self

    def rotate_z(self, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param degree: angle of rotation in degree
        :return: self
        >>> mat3().rotate_z(90).round()
        mat3(0,1,0, -1,0,0, 0,0,1)
        """
        m = mat3().init_rotate_z(degree)
        self._multiply_inplace(m)
        return self

    def rotate_axis(self, axis, degree):
        """
        Adds a rotation to the current matrix, INPLACE
        :param axis: axis of rotation, must be normalized
        :param degree: angle of rotation in degree
        :return: self
        >>> mat3().rotate_axis((1,0,0), 90).round()
        mat3(1,0,0, 0,0,1, 0,-1,0)
        """
        m = mat3().init_rotate_axis(axis, degree)
        self._multiply_inplace(m)
        return self

    # ------ value-copying methods -------

    def transposed(self):
        """
        Returns a mat3 with columns and rows interchanged
        :return: mat3
        >>> mat3((1,2,3, 4,5,6, 7,8,9)).transposed()
        mat3(1,4,7, 2,5,8, 3,6,9)
        """
        return self.copy().transpose()

    def inversed_simple(self):
        """
        Returns inverse of a uniformly-scaled, non-skewed matrix.
        :return: mat3
        """
        raise NotImplementedError
        # TODO:
        m = mat3()
        m.v[0] = self.v[0]
        m.v[1] = self.v[4]
        m.v[2] = self.v[8]
        m.v[3] = self.v[3]

        m.v[4] = self.v[1]
        m.v[5] = self.v[5]
        m.v[6] = self.v[9]
        m.v[7] = self.v[7]

        m.v[8] = self.v[2]
        m.v[9] = self.v[6]
        m.v[10] = self.v[10]
        m.v[11] = self.v[11]

        m.v[12] = -(self.v[12] * self.v[0]) - (self.v[13] * self.v[1]) - (self.v[14] * self.v[2])
        m.v[13] = -(self.v[12] * self.v[4]) - (self.v[13] * self.v[5]) - (self.v[14] * self.v[6])
        m.v[14] = -(self.v[12] * self.v[8]) - (self.v[13] * self.v[9]) - (self.v[14] * self.v[10])
        m.v[15] = self.v[15]
        return m

    def rotated_x(self, degree):
        """
        Returns a rotated matrix
        :param degree: angle of rotation in degree
        :return: mat3
        >>> mat3().rotated_x(90).rounded()
        mat3(1,0,0, 0,0,1, 0,-1,0)
        """
        return self.copy().rotate_x(degree)

    def rotated_y(self, degree):
        """
        Returns a rotated matrix
        :param degree: angle of rotation in degree
        :return: mat3
        >>> mat3().rotated_y(90).rounded()
        mat3(0,0,-1, 0,1,0, 1,0,0)
        """
        return self.copy().rotate_y(degree)

    def rotated_z(self, degree):
        """
        Returns a rotated matrix
        :param degree: angle of rotation in degree
        :return: mat3
        >>> mat3().rotated_z(90).rounded()
        mat3(0,1,0, -1,0,0, 0,0,1)
        """
        return self.copy().rotate_z(degree)

    def rotated_axis(self, axis, degree):
        """
        Returns a rotated matrix
        :param axis: axis of rotation, must be normalized
        :param degree: angle of rotation in degree
        :return: mat3
        >>> mat3().rotated_axis((1,0,0), 90).rounded()
        mat3(1,0,0, 0,0,1, 0,-1,0)
        """
        return self.copy().rotate_axis(axis, degree)


if __name__ == "__main__":
    import doctest
    doctest.testmod()