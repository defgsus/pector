from vec3 import vec3
import random

def rnd_vec3(mi=-1., ma=1.):
    return vec3((random.uniform(mi, ma),
                 random.uniform(mi, ma),
                 random.uniform(mi, ma)))

def use_case_1():
    rnd = random.random()

    pos = [rnd_vec3() for i in range(32)]
    imp = [rnd_vec3() for i in range(32)]

    for it in range(100):
        for i in range(len(pos)):
            for j in range(i+1, len(pos)):
                d = (pos[j] - pos[i])
                l = d.length()
                d /= l
                a = 0.02 * l * d
                imp[i] += a
                imp[j] -= a


# TODO: i get
#   File "/usr/lib/python3.4/cProfile.py", line 22, in <module>
#     run.__doc__ = _pyprofile.run.__doc__
#   AttributeError: 'module' object has no attribute 'run'
# without these:
def run(): pass
def runctx(): pass

def do_profile():
    import cProfile
    prof = cProfile.Profile()
    prof.run("use_case_1()")
    prof.print_stats()


if __name__ == "__main__":
    do_profile()