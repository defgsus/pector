from unittest import TestCase
from vec3 import vec3
from mat4 import mat4


class TestVec3(TestCase):
    def setUp(self):
        pass

    def test_assignment(self):
        self.assertEqual(str(vec3()), "vec3(0, 0, 0)")
        self.assertEqual(str(vec3(1)), "vec3(1, 1, 1)")
        self.assertEqual(str(vec3("5")), "vec3(5, 5, 5)")
        self.assertEqual(str(vec3(1,2)), "vec3(1, 2, 0)")
        self.assertEqual(str(vec3(1,2,3)), "vec3(1, 2, 3)")
        self.assertEqual(str(vec3("1","2","3")), "vec3(1, 2, 3)")
        self.assertEqual(str(vec3((1,))), "vec3(1, 0, 0)")
        self.assertEqual(str(vec3((1,2))), "vec3(1, 2, 0)")
        self.assertEqual(str(vec3((1,2,3))), "vec3(1, 2, 3)")
        self.assertEqual(str(vec3(("1","2","3"))), "vec3(1, 2, 3)")
        with self.assertRaises(TypeError):
            vec3(1, 2, 3, 4)
        with self.assertRaises(TypeError):
            vec3((1, 2, 3, 4))
        with self.assertRaises(TypeError):
            vec3("bla")
        with self.assertRaises(TypeError):
            vec3({"x":23})

        self.assertEqual(str(vec3([1])), "vec3(1, 0, 0)")
        self.assertEqual(str(vec3([1,2])), "vec3(1, 2, 0)")

    def test_equal(self):
        self.assertTrue(  vec3(1) == vec3(1) )
        self.assertFalse( vec3(1) == vec3(2) )
        self.assertTrue(  vec3(1) == (1,1,1) )
        self.assertFalse( vec3(1) == (1, 1) )

    def test_properties(self):
        self.assertEqual(vec3(1,2,3).x, 1)
        self.assertEqual(vec3(1,2,3).y, 2)
        self.assertEqual(vec3(1,2,3).z, 3)
        a = vec3()
        a.x = 5
        self.assertEqual(a, (5,0,0))
        a.y = 6
        self.assertEqual(a, (5, 6, 0))
        a.z = 7
        self.assertEqual(a, (5, 6, 7))

    def test_getitem(self):
        a = vec3((1,2,3))
        self.assertEqual(a[0], 1)
        self.assertEqual(a[1], 2)
        self.assertEqual(a[2], 3)
        with self.assertRaises(IndexError):
            a[3]

    def test_setitem(self):
        a = vec3(0)
        a[0] = 1
        self.assertEqual(a, vec3(1,0,0))
        a[1] = 2
        self.assertEqual(a, vec3(1,2,0))
        a[2] = 3
        self.assertEqual(a, vec3(1,2,3))
        with self.assertRaises(IndexError):
            a[3] = 1

    def test_iter(self):
        self.assertEqual([x for x in vec3(1,2,3)], [1,2,3])

    def test_abs(self):
        self.assertEqual(abs(vec3(-1,-2,-3)), vec3(1,2,3))

    def test_floor(self):
        self.assertEqual(vec3(1.4,2.5,3.6).floor(), vec3(1,2,3))
        self.assertEqual(vec3(-1.4,-2.5,-3.6).floor(), vec3(-2,-3,-4))

    def test_round(self):
        self.assertEqual((0, 0, 1), vec3(0.49, 0.5, 0.51).round())
        self.assertEqual((0, 0, -1), vec3(-0.49, -0.5, -0.51).round())
        self.assertEqual((0.5, 0.5, 0.5), vec3(0.49, 0.5, 0.51).round(1))
        self.assertEqual((-0.5, -0.5, -0.5), vec3(-0.49, -0.5, -0.51).round(1))

    def test_add(self):
        self.assertEqual(vec3(1) + 2, vec3(3))
        self.assertEqual(vec3(1) + vec3(2), vec3(3))
        self.assertEqual(vec3(1,2,3) + vec3(2,3,4), vec3(3,5,7))
        self.assertEqual(vec3(1) + vec3(2), vec3(3))
        self.assertEqual(vec3(1) + [1,2,3], vec3(2,3,4))
        self.assertEqual(vec3(1) + ["1","2","3"], vec3(2,3,4))

        self.assertEqual(2 + vec3(1), vec3(3))
        self.assertEqual("2" + vec3(1), vec3(3))
        self.assertEqual([1,2,3] + vec3(1), vec3(2,3,4))
        self.assertEqual(["1","2","3"] + vec3(1), vec3(2,3,4))

        with self.assertRaises(TypeError):
            vec3() + [1,2]

        a = vec3(1)
        a += 1
        self.assertEqual(a, vec3(2))
        a += [1,2,3]
        self.assertEqual(a, vec3((3,4,5)))

    def test_sub(self):
        self.assertEqual(vec3(3) - vec3(2), vec3(1))
        self.assertEqual(vec3(3) - 2, vec3(1))
        self.assertEqual(vec3(3) - (1,2,3), vec3((2,1,0)))
        self.assertEqual(3 - vec3(2), vec3(1))
        self.assertEqual((1,2,3) - vec3(2), vec3((-1,0,1)))

        a = vec3(1)
        a -= 2
        self.assertEqual(a, vec3(-1))
        a -= [1,2,3]
        self.assertEqual(a, vec3((-2,-3,-4)))

    def test_mul(self):
        self.assertEqual(vec3(2) * vec3(3), vec3(6))
        self.assertEqual(vec3(2) * 3, vec3(6))
        self.assertEqual(vec3(2) * (1,2,3), vec3((2,4,6)))
        self.assertEqual(vec3(2) * vec3((1,2,3)), vec3((2,4,6)))
        self.assertEqual(2 * vec3(3), vec3(6))
        self.assertEqual((1,2,3) * vec3(3), vec3((3,6,9)))

        a = vec3(1)
        a *= 2
        self.assertEqual(a, vec3(2))
        a *= [1,2,3]
        self.assertEqual(a, vec3((2,4,6)))

    def test_div(self):
        self.assertEqual(vec3(3) / vec3(2), vec3(1.5))
        self.assertEqual(vec3(3) / 2, vec3(1.5))
        self.assertEqual(vec3(2) / (1,2,4), vec3((2,1,.5)))
        self.assertEqual(vec3(2) / vec3((1,2,4)), vec3((2,1,.5)))
        self.assertEqual(3 / vec3(2), vec3(1.5))
        self.assertEqual((1,2,3) / vec3(2), vec3((.5,1,1.5)))

        a = vec3(8)
        a /= 2
        self.assertEqual(a, vec3(4))
        a /= [1,2,4]
        self.assertEqual(a, vec3((4,2,1)))

    def test_mod(self):
        self.assertEqual(vec3((1,2,3)) % 2, vec3((1,0,1)))
        self.assertEqual(vec3((1,2,3)) % 2.5, vec3((1,2,.5)))

    def test_dot(self):
        self.assertEqual(vec3((1,2,3)).dot((4,5,6)), 32)

    def test_cross(self):
        self.assertEqual(vec3((1,0,0)).cross((0,1,0)), (0,0,1))
        self.assertEqual(vec3((1,0,0)).cross((0,0,1)), (0,-1,0))
        self.assertEqual(vec3((0,1,0)).cross((0,0,1)), (1,0,0))

    def test_rotate(self):
        self.assertEqual(vec3((1,2,3)).rotate_x(90).round(), vec3((1,-3,2)))
        self.assertEqual(vec3((1,2,3)).rotate_y(90).round(), vec3((3,2,-1)))
        self.assertEqual(vec3((1,2,3)).rotate_z(90).round(), vec3((-2,1,3)))

        self.assertEqual(vec3((1,2,3)).rotate_axis((1,0,0), 90).round(), vec3((1,-3,2)))
        self.assertEqual(vec3((1,2,3)).rotate_axis((0,1,0), 90).round(), vec3((3,2,-1)))
        self.assertEqual(vec3((1,2,3)).rotate_axis((0,0,1), 90).round(), vec3((-2,1,3)))

    def test_rotated(self):
        self.assertEqual(vec3((1,2,3)).rotated_x(90).round(), vec3((1,-3,2)))
        self.assertEqual(vec3((1,2,3)).rotated_y(90).round(), vec3((3,2,-1)))
        self.assertEqual(vec3((1,2,3)).rotated_z(90).round(), vec3((-2,1,3)))
        self.assertEqual(vec3((2,-3,-1)).rotated_z(90).round(), vec3((3,2,-1)))

        self.assertEqual(vec3((1,2,3)).rotated_axis((1,0,0), 90).round(), vec3((1,-3,2)))
        self.assertEqual(vec3((1,2,3)).rotated_axis((0,1,0), 90).round(), vec3((3,2,-1)))
        self.assertEqual(vec3((1,2,3)).rotated_axis((0,0,1), 90).round(), vec3((-2,1,3)))

        self.assertEqual(vec3((1,2,3)).rotated_x(90).rotated_y(90).round(), vec3((2,-3,-1)))
        self.assertEqual(vec3((1,2,3)).rotated_x(90).rotated_y(90).rotated_z(90).round(), vec3((3,2,-1)))

        self.assertEqual(vec3((1,2,3)).rotated_axis((1,0,0), 90).rotated_axis((0,1,0), 90).rotated_axis((0,0,1), 90).round(),
                         vec3((3,2,-1)))

    """
    def test_op_speed(self):
        for i in range(100000):
            vec3(1) + vec3(2)
    """

class TestMat4(TestCase):
    def setUp(self):
        pass

    def test_assignment(self):
        self.assertEqual(str(mat4()), "mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)")
        self.assertEqual(str(mat4(2)), "mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,2)")
        self.assertEqual(str(mat4(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)),
                         "mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)")
        self.assertEqual(str(mat4((1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16))),
                         "mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)")

    def test_equal(self):
        self.assertEqual(mat4(1), (1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1))

    def test_floor(self):
        self.assertEqual(mat4(1), mat4(1.4).floor())
        self.assertEqual(mat4(1), mat4(1.5).floor())
        self.assertEqual(mat4(1), mat4(1.6).floor())
        self.assertEqual(mat4(-2), mat4(-1.4).floor())
        self.assertEqual(mat4(-2), mat4(-1.5).floor())
        self.assertEqual(mat4(-2), mat4(-1.6).floor())

    def test_round(self):
        self.assertEqual(mat4(0), mat4(0.49).round())
        self.assertEqual(mat4(0), mat4(0.5).round())
        self.assertEqual(mat4(1), mat4(0.51).round())
        self.assertEqual(mat4(0), mat4(-0.49).round())
        self.assertEqual(mat4(0), mat4(-0.5).round())
        self.assertEqual(mat4(-1), mat4(-0.51).round())
        self.assertEqual(mat4(0.5), mat4(0.49).round(1))
        self.assertEqual(mat4(0.5), mat4(0.5).round(1))
        self.assertEqual(mat4(0.5), mat4(0.51).round(1))
        self.assertEqual(mat4(-0.5), mat4(-0.49).round(1))
        self.assertEqual(mat4(-0.5), mat4(-0.5).round(1))
        self.assertEqual(mat4(-0.5), mat4(-0.51).round(1))

    def test_aritm(self):
        self.assertEqual(mat4(1)+mat4(2), mat4(3))
        self.assertEqual(mat4(2)-mat4(1), mat4(1))

    def test_has_translation(self):
        self.assertFalse(mat4(1).has_translation())
        self.assertFalse(mat4(2).has_translation())
        self.assertFalse(mat4(1).rotate_axis((1, 2, 3), 23.).has_translation())
        self.assertTrue(mat4(1).translate((1,2,3)).has_translation())

    def test_has_rotation(self):
        self.assertFalse(mat4(1).has_rotation())
        self.assertFalse(mat4(1).translate((1, 2, 3)).has_rotation())
        self.assertTrue(mat4(1).rotate_x(0.01).has_rotation())

    def test_transpose(self):
        self.assertEqual(mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transpose(),
                         mat4((1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)))
        self.assertEqual(mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transposed(),
                         mat4((1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)))
        self.assertEqual(mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)).transposed().transposed(),
                         mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)))

    def test_scalar_aritm(self):
        self.assertEqual(mat4(1) + 1, mat4((2,1,1,1, 1,2,1,1, 1,1,2,1, 1,1,1,2)))
        self.assertEqual(mat4(1) * 3, mat4(3))
        self.assertEqual(mat4(2) - 1, mat4((1,-1,-1,-1, -1,1,-1,-1, -1,-1,1,-1, -1,-1,-1,1)))
        self.assertEqual(mat4(2) / 4, mat4(.5))

    def test_scalar_aritm_inpl(self):
        a = mat4(1)
        a += 1
        self.assertEqual(a, mat4((2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2)))
        a = mat4(1)
        a *= 3
        self.assertEqual(a, mat4(3))
        a = mat4(2)
        a -= 1
        self.assertEqual(a, mat4((1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1)))
        a = mat4(2)
        a /= 4
        self.assertEqual(a, mat4(.5))

    def test_mat4_x_vec3(self):
        self.assertEqual(mat4(1) * (1,2,3), vec3(1,2,3))
        self.assertEqual(mat4(2) * (1,2,3), vec3(2,4,6))

    def test_set_translate(self):
        self.assertEqual( (mat4().set_translate((1,2,3)) * (3,3,3)), (4,5,6))
        with self.assertRaises(TypeError):
            mat4().set_translate(1)
        with self.assertRaises(TypeError):
            mat4().set_translate((1,2))

    def test_translate(self):
        self.assertEqual( (mat4().translate((1,2,3)) * (3,3,3)), (4,5,6) )
        self.assertEqual( (mat4().translate((1,2,3)).translate((1,2,3)) * (3,3,3)), (5,7,9) )

    def test_set_rotate(self):
        self.assertEqual( (mat4().set_rotate_x(90) * (1,2,3)).round(), vec3((1,-3,2)) )
        self.assertEqual( (mat4().set_rotate_y(90) * (1,2,3)).round(), vec3((3,2,-1)) )
        self.assertEqual( (mat4().set_rotate_z(90) * (1,2,3)).round(), vec3((-2,1,3)) )

        self.assertEqual( (mat4().set_rotate_axis((1,0,0), 90) * (1,2,3)).round(), vec3((1,-3,2)) )
        self.assertEqual( (mat4().set_rotate_axis((0,1,0), 90) * (1,2,3)).round(), vec3((3,2,-1)) )
        self.assertEqual( (mat4().set_rotate_axis((0,0,1), 90) * (1,2,3)).round(), vec3((-2,1,3)) )

    def test_rotate(self):
        self.assertEqual( (mat4().rotate_x(90) * (1,2,3)).round(), vec3((1,-3,2)) )
        self.assertEqual( (mat4().rotate_x(90).rotate_y(90) * (1,2,3)).round(), vec3((2,-3,-1)) )
        self.assertEqual( (mat4().rotate_x(90).rotate_y(90).rotate_z(90) * (1,2,3)).round(), vec3((3,2,-1)) )

        self.assertEqual( (mat4().rotate_axis((1,0,0),90).rotate_axis((0,1,0), 90).rotate_axis((0,0,1), 90)
                            * (1,2,3)).round(), vec3((3,2,-1)) )

    def test_compare_rotate_vec(self):
        v = vec3((1,2,3))
        self.assertAlmostEquals( mat4().rotate_x(90) * v, v.rotated_x(90) )
        self.assertAlmostEquals( mat4().rotate_y(90) * v, v.rotated_y(90) )
        self.assertAlmostEquals( mat4().rotate_z(90) * v, v.rotated_z(90) )

        self.assertAlmostEquals( mat4().rotate_z(90).rotate_y(-90) * v, v.rotated_z(90).rotated_y(-90) )
        self.assertAlmostEquals( mat4().rotate_z(90).rotate_y(-90).rotated_x(90) * v,
                                     v.rotated_z(90).rotated_y(-90).rotated_x(90) )

    def test_scale(self):
        self.assertEqual( (mat4().set_scale(2) * (1,2,3)), (2,4,6) )
        self.assertEqual( (mat4().scale(2) * (1,2,3)), (2,4,6) )
        self.assertEqual( (mat4().scale(2).scale(2) * (1,2,3)), (4,8,12) )
        self.assertEqual( (mat4().scale(10).set_scale(2) * (1,2,3)), (2,4,6) )

    def test_position(self):
        self.assertEqual( mat4().translate((1,2,3)).position(), (1,2,3))
        self.assertEqual( mat4().translate((1,2,3)).rotate_x(90).position(), (1,-3,2))
        self.assertEqual( mat4().rotate_x(90).translate((1,2,3)).position(), (1,2,3))
        a = mat4().rotate_x(90).translate((1,2,3))
        self.assertEqual(a.position(), a * (0,0,0))