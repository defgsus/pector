import pyglet
import pyshaders
from csg.glsl import render_glsl
from pector import vec3

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
uniform vec2 iResolution;
uniform vec2 iUV;
uniform vec3 iHitPos;

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
    ro = vec3(1,2,5.)+0.0001;
    rd = normalize(vec3(uv, -1.2));
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

    col.x += smoothstep(1.,.0, length(po - iHitPos));

    return sqrt(col);
}

void main()
{
    vec2 uv = v_pos.xy * vec2(iResolution.x/iResolution.y, 1.);

    vec3 col = vec3(0.);

#if 0
    float d = DE(vec3(uv*4.,0));
    col += smoothstep(2., 0., d) * 0.1;
    col.y += smoothstep(0.02, 0., abs(d)-0.01);
    col.y += smoothstep(0.01, 0., d) * 0.1;
#else
    col = render(uv);
#endif
    //col += smoothstep(0.02,0., length(uv - iUV));
    gl_FragColor = vec4(col,1);
}
"""

class RenderWindow(pyglet.window.Window):

    def __init__(self, dist_field):
        super(RenderWindow, self).__init__(width=640, height=480, resizable=True)
        self.shader = None
        self.dist_field = dist_field
        self.uv = (0,0)
        self.hit_pos = vec3()

    def compile(self):
        try:
            self.shader = pyshaders.from_string(
                                vert_src,
                                frag_src % { "DE": render_glsl(self.dist_field) } )
            self.shader.use()
        except pyshaders.ShaderCompilationError as e:
            print(e.logs)
            exit()

    def on_close(self):
        self.shader.clear()

    def on_draw(self):
        self.clear()
        if not self.shader:
            self.compile()
        if "iResolution" in self.shader.uniforms:
            self.shader.uniforms.iResolution = (self.width, self.height)
        if "iUV" in self.shader.uniforms:
            self.shader.uniforms.iUV = self.uv
        if "iHitPos" in self.shader.uniforms:
            self.shader.uniforms.iHitPos = tuple(self.hit_pos)
        pyglet.graphics.draw(6, pyglet.gl.GL_TRIANGLES,
                             ('v2f', (-1,-1, 1,-1, -1,1
                                      ,1,-1, 1,1, -1,1))#(0,0, window.width,0, 0,window.height,
                                     # window.width,0, window.width,window.height, 0,window.height))
                             )

    def on_key_press(self, sym, mod):
        self.close()

    def on_mouse_press(self, x, y, button, modifiers):
        ray = self.get_ray(x,y)
        t = self.dist_field.sphere_trace(ray[0], ray[1])
        self.hit_pos = ray[0] + ray[1] * t
        print("ro %s, rd %s, t %g, hit %s" % (ray[0], ray[1], t, self.hit_pos))

    def get_ray(self, x, y):
        self.uv = ((x/self.width*2.-1.) * self.width / self.height,
                   y/self.height*2.-1.)
        ro = vec3(1, 2, 5.) + 0.0001
        rd = vec3(self.uv[0], self.uv[1], -1.2).normalize()
        return (ro, rd)


def render_csg(dist_field):
    RenderWindow(dist_field=dist_field)
    pyglet.app.run()

