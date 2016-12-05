import pyglet
import pyshaders


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
void main()
{
    gl_FragColor = vec4(v_pos.x,v_pos.y,1,1);
}
"""

class RenderWindow(pyglet.window.Window):

    def __init__(self, frag_src=frag_src):
        super(RenderWindow, self).__init__(width=640, height=480, resizable=True)
        self.shader = None
        self.frag_src = frag_src

    def compile(self):
        try:
            self.shader = pyshaders.from_string(vert_src, self.frag_src)
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
        pyglet.graphics.draw(6, pyglet.gl.GL_TRIANGLES,
                             ('v2f', (-1,-1, 1,-1, -1,1
                                      ,1,-1, 1,1, -1,1))#(0,0, window.width,0, 0,window.height,
                                     # window.width,0, window.width,window.height, 0,window.height))
                             )

    def on_key_press(self, key, mod):
        self.close()


def render_frag(frag_src):
    RenderWindow(frag_src = frag_src)
    pyglet.app.run()

if __name__ == "__main__":
    window = RenderWindow()
    pyglet.app.run()
