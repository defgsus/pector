import pyglet, pyshaders, math
from csg.glsl import render_glsl
from pector import vec3, mat4, quat



vert_src = """
in vec4 pos;
varying vec4 v_pos;
void main()
{
    v_pos = pos;
    gl_Position = pos;
}
"""

frag_src = """
in vec4 v_pos;
uniform vec2 u_resolution;
uniform vec2 u_mouse_uv;
uniform vec3 u_hit_pos;
uniform mat4 u_transform;
uniform mat4 u_ship1;
uniform mat4 u_ship1_i;

%(DE)s
#line 27

vec3 ship1_pos = (u_ship1 * vec4(0,-.5,-2,1)).xyz;

float sdBox( vec3 p, vec3 b )
{
  vec3 d = abs(p) - b;
  return min(max(d.x,max(d.y,d.z)),0.0) + length(max(d,0.0));
}

float DE_ship(in vec3 p)
{
    p = (u_ship1_i * vec4(p, 1.)).xyz;
    //p += vec3(0,0,-5);
    float d = sdBox(p, vec3(0.5, 0.2, 1.));
    d = min(d, sdBox(p, vec3(2., 0.2, 0.2)));
    d = min(d, sdBox(p-vec3(0,0.4,.8), vec3(0.1, 0.2, 0.2)));
    return d;
}

float DE1(in vec3 p) { return min(DE(p), DE_ship(p)); }

vec3 DE_norm(in vec3 p)
{
    vec2 e = vec2(0.001, 0.);
    return normalize(vec3(
        DE1(p + e.xyy) - DE1(p - e.xyy),
        DE1(p + e.yxy) - DE1(p - e.yxy),
        DE1(p + e.yyx) - DE1(p - e.yyx) ));
}

vec3 light_acc;
float sphere_trace(in vec3 ro, in vec3 rd)
{
    float t = 0.;
    for (int i=0; i<150 && t < 100.; ++i)
    {
        float d = DE1(ro + rd * t);
        if (d < 0.001)
            return t;
        light_acc += dot(rd, normalize(ro+rd*t - ship1_pos));
        t += d;
    }
    return -1.;
}

vec3 sky_c(in vec3 rd)
{
    vec3 col = mix(vec3(0.5,.3,.1)*.2,
                   vec3(0.2,.5,.8)*.3, rd.y*.5+.5);
    col *= .5;
    col *= sin(rd*3.)*.1+.9;
    return col;
}

vec3 light(in vec3 p, in vec3 n, in vec3 refl, in vec3 lp, in vec3 co)
{
    vec3 ln = normalize(lp - p);
    float ph = max(0., dot(n, ln));
    float sh = max(0., dot(refl, ln));
    vec3 col = co * pow(ph, 2.)
             + co * pow(sh, 9.) * .5;
    col /= (1. + length(lp-p));
    return col;
}

void get_ray(in vec2 uv, out vec3 ro, out vec3 rd)
{
    ro = vec3(0,0,0);
    rd = normalize(vec3(uv, -1.2));

    ro = (u_transform * vec4(ro, 1.)).xyz;
    rd = (u_transform * vec4(rd, 0.)).xyz;
}

vec3 render(in vec2 uv)
{
    vec3 ro, rd, col=vec3(0);
    get_ray(uv, ro, rd);
    light_acc = vec3(0);
    float t = sphere_trace(ro, rd);

    if (t < 0.)
        col = sky_c(rd);
    else
    {
        vec3 po = ro+t*rd;
        vec3 n = DE_norm(po);
        vec3 refl = reflect(rd, n);

        col += sky_c(refl)*.2;
        col += 0.1 * (sky_c(rd)*.2+.4) * pow(max(0., dot(rd, refl)), 7.);
        col += light(po, n, refl, vec3(10,10,-3), vec3(.6,.7,1.));
        col += light(po, n, refl, ship1_pos, vec3(1,.9,.5));

        col += smoothstep(.2,.0, length(po - u_hit_pos)) * vec3(0,1,1);
        //col += light(po, n, refl, u_hit_pos, vec3(0,1,1)) * .4;

        col = mix(col, sky_c(rd), smoothstep(3., 80., t));
    }

    float l = max(0., dot(rd, normalize(ship1_pos-ro)));
    col += .1 * vec3(1,.9,.5)*pow(l,3.+length(ship1_pos-ro));

    return col;
}

void main()
{
    vec2 uv = v_pos.xy * vec2(u_resolution.x/u_resolution.y, 1.);

    vec3 col = vec3(0.);

#if 0
    float d = DE(vec3(uv*4.,0));
    col += smoothstep(2., 0., d) * 0.1;
    col.y += smoothstep(0.02, 0., abs(d)-0.01);
    col.y += smoothstep(0.01, 0., d) * 0.1;
#else
    col = render(uv);
#endif
    //col += smoothstep(0.02,0., length(uv - u_mouse_uv));
    gl_FragColor = vec4(sqrt(col),1);
}
"""


CITY_MAP = """
#include <dh/hash>
#include <noise>
#include <fnoise>
#include <iq/vnoise>
#include <iq/distfunc>
#include <intersect>
#include <rotate>

float smin( float a, float b, float k = 32.)
{
    float res = exp( -k*a ) + exp( -k*b );
    return -log( res )/k;
}

vec3 smin(in vec3 a, in vec3 b, float k = 32.)
{
	return vec3(smin(a.x, b.x, k), smin(a.y,b.y,k), smin(a.z,b.z,k));
}



vec3 citymap(in vec3 p)
{
	float mag, ac = 0.;
	for (int i = 0; i < 42; ++i)
	{
		mag = dot(p, p);
		p = abs(p) / mag - vec3(.5, .2, 1.578);
		ac += mag;
	}
	ac = max(ac / 200., smoothstep(1,0,ac/50.));
	return vec3(ac) * (0.8+0.2*clamp(p, 0., 1.));
}

const float GRID = 10.;
const float MAX_SIZE = GRID * 0.9;

float de_building(in vec3 p, in vec3 seed)
{
	vec3 si = hash3(seed);
	si.y = pow(si.y, 4.);
	si = 0.1 + 0.9 * si;
	si *= MAX_SIZE / 2.;
	si.y *= 4.;

	//float rot = floor( hash1(seed*1.1+2.3) * 3.) / 2.;
	//p.xz = rotate(p.xz, 90. * rot);

	// outer wall
	float d = sdBox(p, si);
	// inner wall
	d = max(d, -sdBox(p, si*0.9));
	// windows
	si *= 0.1 + .7*hash3(seed*1.2+3.1);
	si.y = 0.1 + mod(si.y, 1.);
	p = mod(p, si) - si / 2.;
	d = max(d, -sdBox(p, si*.4));
	return d;
}

float de_rnd_building(in vec3 p)
{
	vec3 pos = p;
	pos.xz = mod(pos.xz, GRID) - GRID / 2.;
	return de_building(pos, floor(p/GRID).xzz);
}

float de_indust(in vec3 p)
{
	float d = GRID-MAX_SIZE;
	for (int i=0; i<5; ++i)
	{
		d = min(d, de_rnd_building(p));
		p.xz += GRID * (1. + hash2(100.-i));
	}

	return d;
}

float DE(in vec3 p)
{
	float d = dot(p, vec3(0,1,0));
	d = min(d, de_indust(p));
	return d;
}

const float DE_FUDGE = 0.5;

float DE_trace(in vec3 ro, in vec3 rd, in float len = 10., int steps = 100)
{
	float t = 0.;
	for (int i=0; i<steps && t < len; ++i)
	{
		vec3 p = ro + t * rd;
		float d = DE(p);

		t += d * DE_FUDGE;
	}
	return t;
}

float DE_ambient(in vec3 ro, in vec3 rd, int steps = 20)
{
	float t = 0.0003, ma = 0.;
	for (int i=0; i<steps; ++i)
	{
		float d = DE(ro + t * rd);
		ma = max(ma, d);
		if (d < 0.0001) break;
		t += d * DE_FUDGE;
	}
	return min(1., ma/4.);
}

float DE_shadow(in vec3 ro, in vec3 rd, float maxt, int k = 8., int steps = 20)
{
    float t = 0.001, res = 1.0;
    for (int i=0; i<steps && t < maxt; ++i)
    {
        float h = DE(ro + rd * t);
        if( h<0.001 )
            return 0.0;
        res = min( res, k*h/t );
        t += h * DE_FUDGE;
    }
    return res;
}
"""

class Spaceship:
    def __init__(self, dist_field):
        self.delta = 0.01
        self.reset()
        self.dist_field = dist_field
        self.follower = []
        self.second = 0.

    def add_follower(self):
        f = Spaceship(self.dist_field)
        f.delta = self.delta
        f.transform = self.transform.copy().translate((0,0,-10))
        f.velocity = self.velocity.copy()
        f.rotate = self.rotate.copy()
        self.follower.append(f)


    def reset(self):
        self.transform = mat4()
        self.velocity = vec3(0)
        self.rotate = vec3(0)

    def integrate(self):
        self.second += self.delta
        self.transform.translate(self.velocity * self.delta)
        self.transform.rotate_z((self.rotate.y * 12. +self.rotate.z*20.) * self.delta)
        self.transform.rotate_y(self.rotate.y * 20. * self.delta)
        self.transform.rotate_x(self.rotate.x * 20. * self.delta)

        self.collide()

        self.velocity -= self.delta * self.velocity
        self.rotate -= self.delta * self.rotate

        for f in self.follower:
            f.delta = self.delta
            f.follow( self.transform.translated((0,0,-10)).position() )
            #f.cruise()
            f.integrate()

    def cruise(self):
        t = self.second
        self.rotate += self.delta * vec3(math.sin(t), math.sin(t*1.31), math.sin(t*.797))
        self.velocity.z -= self.delta * 10.

    def follow(self, pos):
        d = self.transform.inversed_simple() * pos
        di = d.length()
        if di < 0.01:
            return
        d.normalize_safe()
        q = vec3(0,0,-1).get_rotation_to(d)
        adjust = max(0.,min(1., (di-2.)/40.)) * 10.
        q = quat().lerp(q, self.delta*adjust).normalize()
        self.transform *= q.as_mat4()
        self.velocity.z -= self.delta * max(1.,-d.z * 10. -self.velocity.z*.5)


    def collide(self):
        p = self.transform.copy().translate(self.velocity * self.delta).position()
        d = self.dist_field.get_distance(p)
        if d < 0.0:
            self.transform.translate(-d*1.1 * self.dist_field.get_normal(p))
            n = self.dist_field.get_normal(p)
            self.velocity.reflect(n)

            #self.transform.reflect(n).rotate_z(180)

    def check_keys(self, keys):
        amt = self.delta * 4
        if keys[pyglet.window.key.W]:
            self.velocity.z -= amt * max(1.,min(8., 1.-.2*self.velocity.z))
        if keys[pyglet.window.key.S]:
            self.velocity.z += amt * max(1.,min(8., 1.+.2*self.velocity.z))
        if keys[pyglet.window.key.A]:
            self.velocity.x -= amt * max(1.,min(8., 1.-.2*self.velocity.x))
        if keys[pyglet.window.key.D]:
            self.velocity.x += amt * max(1.,min(8., 1.+.2*self.velocity.x))
        if keys[pyglet.window.key.Q]:
            self.rotate.z += amt
        if keys[pyglet.window.key.E]:
            self.rotate.z -= amt
        if keys[pyglet.window.key.UP]:
            self.rotate.x += amt
        if keys[pyglet.window.key.DOWN]:
            self.rotate.x -= amt
        if keys[pyglet.window.key.LEFT]:
            self.rotate.y += amt
        if keys[pyglet.window.key.RIGHT]:
            self.rotate.y -= amt



class RenderWindow(pyglet.window.Window):

    def __init__(self, dist_field):
        super(RenderWindow, self).__init__(width=480, height=320, resizable=True,
                                           vsync=True)
        self.shader = None
        self.dist_field = dist_field
        self.uv = (0,0)
        self.is_hit = False
        self.hit_pos = vec3()
        self.transform = mat4().translate(vec3(0,0,5)+0.001)
        self.spaceship = Spaceship(self.dist_field)
        self.spaceship.transform = self.transform
        self.spaceship.delta = 1.
        self.spaceship.add_follower()
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        pyglet.clock.schedule_interval(self.update, 1.0 / 20.0)
        pyglet.clock.set_fps_limit(20)

    def compile(self):
        try:
            #frag = frag_src % {"DE": CITY_MAP}
            frag = frag_src % {"DE": render_glsl(self.dist_field)}
            print(frag)
            self.shader = pyshaders.from_string(
                                vert_src,
                                frag )
            self.shader.use()
        except pyshaders.ShaderCompilationError as e:
            print(e.logs)
            exit()

    def on_close(self):
        self.shader.clear()

    def update(self, dt):
        self.spaceship.delta = dt
        self.spaceship.check_keys(self.keys)
        self.spaceship.integrate()
        self.transform = self.spaceship.transform
        self.move_outside()

    def on_draw(self):
        self.clear()
        if not self.shader:
            self.compile()

        if "u_resolution" in self.shader.uniforms:
            self.shader.uniforms.u_resolution = (self.width, self.height)
        if "u_mouse_uv" in self.shader.uniforms:
            self.shader.uniforms.u_mouse_uv = self.uv
        if "u_hit_pos" in self.shader.uniforms:
            self.shader.uniforms.u_hit_pos = tuple(self.hit_pos)
        if "u_transform" in self.shader.uniforms:
            self.shader.uniforms.u_transform = self.transform.as_list_list(row_major=True)
        if self.spaceship.follower:
            if "u_ship1" in self.shader.uniforms and self.spaceship.follower:
                self.shader.uniforms.u_ship1 = self.spaceship.follower[0].transform.as_list_list(row_major=True)
            if "u_ship1_i" in self.shader.uniforms and self.spaceship.follower:
                self.shader.uniforms.u_ship1_i = self.spaceship.follower[0].transform.inversed_simple().as_list_list(row_major=True)

        pyglet.graphics.draw(6, pyglet.gl.GL_TRIANGLES,
                             ('v2f', (-1,-1, 1,-1, -1,1
                                      ,1,-1, 1,1, -1,1))#(0,0, window.width,0, 0,window.height,
                             # window.width,0, window.width,window.height, 0,window.height))
                             )

    def on_key_press(self, sym, mod):
        if sym == pyglet.window.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, button, modifiers):
        self.y_down = y
        self.x_down = x
        ray = self.get_ray(x,y)
        t = self.dist_field.sphere_trace(ray[0], ray[1])
        self.is_hit = t > 0.
        self.hit_pos = ray[0] + ray[1] * t
        #print("ro %s, rd %s, t %g, hit %s" % (ray[0], ray[1], t, self.hit_pos))

    def on_mouse_drag(self, x, y, dx, dy, but, mod):
        use_pivot = self.is_hit and not but == 4

        self.transform.rotate_x(dy)
        self.transform.rotate_y(-dx)

        if use_pivot:
            pivot = self.transform * self.hit_pos
            m = self.transform.position_cleared()
            X = m * (1, 0, 0)
            Y = m * (0, 1, 0)
            p = self.transform.position() - self.hit_pos
            p.rotate_axis(X, dy)
            p.rotate_axis(Y, -dx)
            p += self.hit_pos
            self.transform.set_position(p)
            self.move_outside()

    def on_mouse_scroll(self, x, y, sx, sy):
        self.transform.translate((0,0,sy))
        self.move_outside()


    def get_uv(self, x, y):
        return ((x / self.width * 2. - 1.) * self.width / self.height,
                y / self.height * 2. - 1.)

    def get_ray(self, x, y):
        self.uv = self.get_uv(x, y)
        ro = self.transform.position()
        m = self.transform.copy()
        m.set_position((0,0,0))
        rd = m * vec3(self.uv[0], self.uv[1], -1.2).normalize()
        return (ro, rd)

    def move_outside(self):
        return
        limit = .01
        min_step = .2
        p = self.transform.position()
        d = self.dist_field.get_distance(p)
        tries = 0
        while d < limit and tries < 5:
            if d < 0.:
                if d > -min_step:
                    d = -min_step
            else:
                if d < min_step:
                    d = min_step
            p += d * self.dist_field.get_normal(p)
            d = self.dist_field.get_distance(p)
            tries += 1
        self.transform.set_position(p)


def render_csg(dist_field):
    w = RenderWindow(dist_field=dist_field)
    pyglet.app.run()

