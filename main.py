__version__ = "0.1.0"
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from objloader import ObjFile
try:
	import androidhelper as droid
	ANDROID=True
except ImportError:
	ANDROID=False
	  
class InterfaceManager(BoxLayout):
    def __init__(self, **kwargs):
        super(InterfaceManager, self).__init__(**kwargs)

        self.first = Button(text="Load a model")
        self.first.bind(on_press=self.show_second)

        self.second = LoadDialog()
        self.second.bind(on_press=self.show_final)

        self.final = Button(text="View")
        self.add_widget(self.first)

    def show_second(self, button):
        self.clear_widgets()
        self.add_widget(self.second)

    def show_final(self):
        self.clear_widgets()
        self.add_widget(renderer)

class LoadDialog(BoxLayout):
	"""Load dialog"""
	def load(self):
		"""Loads defined image"""
		global renderer
		try:
			selected_model_filename = self.ids['load_filechooser'].selection[0]
			renderer = Renderer(selected_model_filename)
			print renderer.filename
			self.parent.show_final()	
		except IndexError:
			print 'Please select a valid model'		
	
	def cancel(self):
		"""Dismisses the popup"""
		load_popup.dismiss()
		
	def get_home(self):
		if ANDROID:
			return '/sdcard'
		else:
			return '.'

class Renderer(Widget):
    def __init__(self, filename, **kwargs): 
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        self.scene = ObjFile(resource_find(filename))			
        self.filename = filename
        super(Renderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        Clock.schedule_interval(self.update_glsl, 1 / 60.)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, *largs):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj
        self.canvas['diffuse_light'] = (4.0, 1.0, 0.8)
        self.canvas['ambient_light'] = (0.1, 0.1, 0.1)
        self.rot.angle += 0.25

    def setup_scene(self):
        Color(1,1,1,1)
        PushMatrix()
        Translate(0, 0, -3)
        self.rot = Rotate(1, 0, 1, 0)
        m = list(self.scene.objects.values())[0]
        UpdateNormalMatrix()
        self.mesh = Mesh(
            vertices=m.vertices,
            indices=m.indices,
            fmt=m.vertex_format,
            mode='triangles',
        )
        PopMatrix()

class RendererApp(App):
    def build(self):
        return InterfaceManager(orientation='vertical')
        
if __name__ == "__main__":
    RendererApp().run()
