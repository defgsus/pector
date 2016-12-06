import pyglet
import pyshaders
from csg.glsl import render_glsl
from pector import vec3, mat4



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


//float DE(in vec3 p) { return length(p)-1.; }
%(DE)s

vec3 DE_norm(in vec3 p)
{
    vec2 e = vec2(0.001, 0.);
    return normalize(vec3(
        DE(p + e.xyy) - DE(p - e.xyy),
        DE(p + e.yxy) - DE(p - e.yxy),
        DE(p + e.yyx) - DE(p - e.yyx) ));
}

float sphere_trace(in vec3 ro, in vec3 rd)
{
    float t = 0.;
    for (int i=0; i<150 && t < 100.; ++i)
    {
        float d = DE(ro + rd * t);
        if (d < 0.001)
            return t;
        t += d;
    }
    return -1.;
}

vec3 sky_c(in vec3 rd)
{
    return mix(vec3(0.5,.3,.1)*.5,
               vec3(0.2,.5,.8)*.6, rd.y*.5+.5);
}

vec3 light(in vec3 p, in vec3 n, in vec3 refl, in vec3 lp, in vec3 co)
{
    vec3 ln = normalize(lp - p);
    float ph = max(0., dot(n, ln));
    float sh = max(0., dot(refl, ln));
    return co * pow(ph, 2.)
         + co * pow(sh, 9.) * .5;
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
    float t = sphere_trace(ro, rd);

    if (t < 0.)
        return sky_c(rd);

    vec3 po = ro+t*rd;
    vec3 n = DE_norm(po);
    vec3 refl = reflect(rd, n);

    col += sky_c(refl)*.3;
    col += (sky_c(rd)*.2+.4) * pow(max(0., dot(rd, refl)), 7.);
    col += light(po, n, refl, vec3(10,10,-3), vec3(.6,.7,1.));
    col += light(po, n, refl, vec3(-2,-4,10), vec3(1,.7,.5));

    col += smoothstep(.2,.0, length(po - u_hit_pos)) * vec3(0,1,1);
    col += light(po, n, refl, u_hit_pos, vec3(0,1,1)) * .4;

    return sqrt(col);
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
    gl_FragColor = vec4(col,1);
}
"""

class Spaceship:
    def __init__(self):
        self.delta = 0.01
        self.reset()

    def reset(self):
        self.transform = mat4()
        self.velocity = vec3(0)
        self.rotate = vec3(0)

    def integrate(self):
        self.transform.translate(self.velocity * self.delta)
        self.transform.rotate_z((self.rotate.y * 12. +self.rotate.z*20.) * self.delta)
        self.transform.rotate_y(self.rotate.y * 20. * self.delta)
        self.transform.rotate_x(self.rotate.x * 20. * self.delta)

        self.velocity -= self.delta * self.velocity
        self.rotate -= self.delta * self.rotate

    def check_keys(self, keys):
        amt = self.delta * 4
        if keys[pyglet.window.key.W]:
            self.velocity.z -= amt * max(1.,min(8., 1.-.2*self.velocity.z))
        if keys[pyglet.window.key.S]:
            self.velocity.z += amt * max(1.,min(8., 1.+.2*self.velocity.z))
        if keys[pyglet.window.key.A]:
            self.velocity.x -= amt
        if keys[pyglet.window.key.D]:
            self.velocity.x += amt
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
        super(RenderWindow, self).__init__(width=640, height=480, resizable=True,
                                           vsync=True)
        self.shader = None
        self.dist_field = dist_field
        self.uv = (0,0)
        self.is_hit = False
        self.hit_pos = vec3()
        self.transform = mat4().translate(vec3(0,0,5)+0.001)
        self.spaceship = Spaceship()
        self.spaceship.transform = self.transform
        self.spaceship.delta = 1.
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)

        pyglet.clock.schedule_interval(self.update, 1.0 / 20.0)
        pyglet.clock.set_fps_limit(20)

    def compile(self):
        try:
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

