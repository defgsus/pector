from csg import *
import csg.glsl
import csg_shader_window

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


def render(csg):
    try:
        import sys
        size = (int(sys.argv[1]), int(sys.argv[2]))
    except BaseException:
        size = (80, 10)
    try:
        scale = float(sys.argv[3])
    except BaseException:
        scale = .1
    print_slice(csg, size=size, scale=scale)


def csg_0():
    o = Union([
        Sphere(transform=mat4().translate((-1,0,0))),
        Sphere(radius=.75),
        Sphere(transform=mat4().translate((+1, 0, 0)), radius=.5),
    ])
    #o = Fan(o.set_transform(mat4().translate((0,3,0))), axis=2, angle=(0,90))
    return o


def csg_1():
    stripes = Repeat(
            Tube(radius=.3, axis=1)#, transform=mat4().rotate_z(22.5).translate((2,0,0)))
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
    return c

def csg_2():
    return Union([
        Union([
            Union([Sphere()
                    ]
                    , transform=mat4().translate((0, 0, 1)))
                ], transform=mat4().translate((0, 1, 0))
            )
        ], transform=mat4().translate((1, 0, 0))
    )


import random
def random_object(only_primitives=False):
    if only_primitives:
        classes = [Sphere, Tube]
    else:
        classes = [Union, Difference, Intersection,
                   Repeat,
                   Sphere, Tube]
    c = random.choice(classes)()
    if hasattr(c, "radius"):
        c.radius = round(random.uniform(.01, 2.), 3)
    if hasattr(c, "axis"):
        c.axis = random.randint(0,2)
    if hasattr(c, "repeat"):
        c.repeat = vec3([random.uniform(1.5,5.) for i in range(3)])

    return c

def csg_rnd():
    root = Union()
    for i in range(20):
        objs = list(root.nodes_as_set())
        for j in range(3):
            n = random.choice(objs)
            if n.can_have_nodes:
                c = random_object()
                n.add_node(c)

    objs = root.nodes_as_set()
    for o in objs:
        if not o.nodes and not isinstance(o, Primitive):
            o.add_node(random_object(only_primitives=True))

    return root

def csg_3():
    spheres = Union([
            Fan(axis=2, angle=(0, 90),
                object=Sphere(transform=mat4().translate((0,2,0)))
                ),
            Fan(axis=2, angle=(0, 90),
                object=Sphere(radius=.5, transform=mat4().translate((0, 3.5, 0)))
                ),
            Fan(axis=2, angle=(0, 90), transform=mat4().rotate_z(30),
                object=Sphere(radius=.25, transform=mat4().translate((0, 2.5, 0)))
                ),
        ])
    return Union([
        Union([
            spheres.copy(),
            #Repeat(repeat=vec3(20,20,0), object=
            Fan(axis=2, angle=(0,30),
                object=spheres.copy().set_transform(mat4().translate((0,6.,-10.)))
                )#)
        ]),
        Repeat(repeat=vec3(4),
               object=Sphere(radius=0.05)
               )
        #Difference([
        #    Tube(axis=1, transform=mat4().translate((3,0,0)))
        #])
    ])

def csg_4():
    cones = Intersection([
        Tube(radius=5),
        Repeat(repeat=vec3(0,2,2),
               object=DeformFunction(py_func=lambda pos: pos.rotate_x(pos.x),
                                     glsl_func="""
                                     float a = pos.x;
                                     mat2 r = mat2(cos(a), sin(a), -sin(a), cos(a));
                                     pos.yz = r * pos.yz;
                                     """,
                    object = Difference([
                        Tube(radius=.5),
                        Repeat(repeat=(0.81,0,0),
                               object=Fan(axis=0, angle=(-360./12.,360./12.),
                                          object=Sphere(radius=0.4, transform=mat4().translate((0,0,.59)))
                                         )
                              ),
                        Repeat(repeat=(0.05, 0, 0),
                               object=Fan(axis=0, angle=(-2, 2),
                                          object=Sphere(radius=0.02, transform=mat4().translate((0, 0, .5)))
                                         )
                              )
                        ])
                   )
               )
        ])
    return Union([
        cones.copy().set_transform(mat4().rotate_y(90).translate((.5,.5,0))),
        cones.copy().set_transform(mat4().rotate_z(45).translate((0, 0, -10)))
    ])

def csg_5():
    o = Tube(radius=0.1, axis=1)
    o = Fan(o, axis=2)
    o = Repeat(o, repeat=(2,2,0))
    o = Fan(o, axis=2, angle=(0,60))
    o = Repeat(o, repeat=(5,5,0))
    o = Fan(o, axis=2, angle=(0, 90))
    o = Fan(o.set_transform(mat4().translate((0,0,6))), axis=1, angle=(0,60))
    o = Fan(o, axis=2, angle=(0, 60))
    o = Repeat(o, repeat=vec3(36,36,0))

    return o;

def csg_6():
    o = Difference([
        Plane(normal=(0,1,0)),
        Repeat(repeat=(2,0,2),
               object=Sphere(radius=.5))
    ])
    #o = Union([o.copy(), Sphere(transform=mat4().translate((0,2,0)))])
    #o = Union([o.copy(), Tube(axis=2)])
    o = Fan(o.set_transform(mat4().translate((0,-12, 0))), axis=2, angle=(180, 40) )
    o = Repeat(o, repeat=vec3(24, 0, 0))
    o = Fan(o.set_transform(mat4().translate((13,0, 0))), axis=1, angle=(90, 80) )
    return o


c = csg_5()
#print( csg.glsl.render_glsl(c) )
#render(c)
csg_shader_window.render_csg(c)
