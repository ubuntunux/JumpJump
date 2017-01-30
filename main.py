from Utility import *
from GameFrame import gGameFrame
from FileBrowser import FileBrowser

class Main(Singleton):
  def __init__(self):
    self.screen = Screen(name="main")
    self.layout = BoxLayout(orientation="vertical", size_hint=(0.8, 0.4))
    self.layout.pos = sub(cXY, (W*0.4, H*0.2))
    btn_start = Button(text="Start")
    btn_start.bind(on_release=self.startGame)
    btn_exit = Button(text="Exit")
    btn_exit.bind(on_release=self.exit)
    self.layout.add_widget(btn_start)
    self.layout.add_widget(btn_exit)
    self.screen.add_widget(self.layout)
    
  def exit(self, *args):
    gMyRoot.popup("Exit?", "", gMyRoot.exit, None)
    
  def start(self):
    gMyRoot.setTouchPrev(self.exit)
    gMyRoot.current_screen(self.screen)
    
  def startGame(self, *args):
    gGameFrame.start(callback_on_closed=self.start)
    
  def update(self, dt):
    pass

if __name__ in ('__android__', '__main__'):
  gMyRoot.run( Main.instance() )