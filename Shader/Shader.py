from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty
from kivy.graphics import RenderContext, Fbo, Color, Rectangle

fs_header = '''
#ifdef GL_ES
precision highp float;
#endif
varying vec4 frag_color;
varying vec2 tex_coord0;
uniform sampler2D texture0;
uniform float time;
uniform vec2 uv_panning;
uniform float uv_rotation;
'''

fs_default = fs_header + '''
uniform vec4 diffuse_color;
void main() {
    vec2 uv = tex_coord0;
    gl_FragColor = texture2D(texture0, uv)*diffuse_color;
}
'''

fs_panning = fs_header + '''
void main() {
    vec2 uv = tex_coord0 + uv_panning * time;
    gl_FragColor = texture2D(texture0, uv);
}
'''

fs_rotation = fs_header + '''
void main() {
    float fRot = time * uv_rotation;
    vec2 uv = tex_coord0 - vec2(0.5, 0.5);
    uv = cos(fRot)*uv + sin(fRot)*vec2(uv.y, -uv.x);
    uv += vec2(0.5, 0.5);
    gl_FragColor = texture2D(texture0, uv);
}
'''

class ShaderScatter(Scatter):
    def __init__(self, source=None, texture=None, repeat=False, shader=fs_default, uv_panning=[1.0,1.0], uv_rotation=1.0, **kwargs):
        if texture == None:
            if source == None:
                return
            else:
                texture=Image(source=source).texture
        self.canvas = RenderContext()
        Scatter.__init__(self, **kwargs)
        self.shader_fs(shader)
        self.diffuse_color=[1.0,1.0,1.0,1.0]
        self.uv_panning=uv_panning
        self.uv_rotation=uv_rotation
        self.texture=texture
        if repeat:
            self.texture.wrap = 'repeat'
        
        with self.canvas:
            Color(1,1,1)
            self.rect = Rectangle(texture=self.texture, size=self.size)
        Clock.schedule_interval(self.update_glsl, 0)

    def update_glsl(self, *largs):
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['diffuse_color'] = self.diffuse_color
        self.canvas['uv_panning'] = self.uv_panning
        self.canvas['uv_rotation'] = self.uv_rotation
        self.canvas['projection_mat'] = Window.render_context['projection_mat']

    def shader_fs(self, value):
        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')

class ShaderTreeApp(App):
    def build(self):
        self.root = FloatLayout()
        with self.root.canvas:
            Color(0.3,0.3,0.3)
            Rectangle(size=Window.size)
        texture = Image(source= 'data/logo/kivy-icon-24.png' ).texture
        sw = ShaderScatter(shader=fs_rotation, pos=[300,300], texture=texture, size=(300, 300))       
        self.root.add_widget(sw)
        return self.root

if __name__ == '__main__':
    ShaderTreeApp().run()