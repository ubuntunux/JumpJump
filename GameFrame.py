from Utility import *
from ResourceMgr import gResMgr
from Stage import gStageMgr
from Constants import *


class Score(Singleton):
  def __init__(self):
    self.widget = Widget()
    self.score = 0
    self.score_label = Label(text="", center=(cX, H - kivy.metrics.dp(20)), \
      font_size="20dp")
    self.widget.add_widget(self.score_label)
    self.setScore(0)
  
  def reset(self):
    pass
    
  def addScore(self, score):
    self.setScore(self.score + score)
    
  def setScore(self, score):
    self.score = score
    self.score_label.text = "Score : " + str(self.score)
    

class GameScreen(Singleton):
  def __init__(self):
    self.screen = Screen(name="game screen")

    # add bg
    self.layer_bg = Widget()
    self.layer_bg.name="layer_bg"
    self.screen.add_widget(self.layer_bg)

    # add fx layer
    self.layer_fx = Widget()
    self.layer_fx.name = "layer_fx"
    self.screen.add_widget(self.layer_fx)
    
    # add ui layer
    self.layer_ui = Widget()
    self.layer_ui.name = "layer_ui"
    self.layer_ui = FloatLayout(size_hint=(1,1))
    self.btn_left = Button(size_hint=(0.5, 1), background_color=(1,1,1,0))
    self.btn_right = Button(size_hint=(0.5, 1), background_color=(1,1,1,0), pos_hint={"right":1})
    self.layer_ui.add_widget(self.btn_left)
    self.layer_ui.add_widget(self.btn_right)
    self.screen.add_widget(self.layer_ui)

    with self.screen.canvas:
      self.color = Color(0,0,0,1)
      Rectangle(pos=(0,0), size=WH)
      
  def bind_btn_left(self, func):
    self.btn_left.bind(on_press=lambda inst:func(True))
    self.btn_left.bind(on_release=lambda inst:func(False))
  
  def bind_btn_right(self, func):
    self.btn_right.bind(on_press=lambda inst:func(True))
    self.btn_right.bind(on_release=lambda inst:func(False))
  
  def recvResourceName(self, resName):
    log(resName)
  
  def reset(self):
    self.clear_widgets()
    self.layer_ui.add_widget(self.btn_left)
    self.layer_ui.add_widget(self.btn_right)
  
  def show(self):
    gMyRoot.add_screen(self.screen)
    gMyRoot.current_screen(self.screen)
    
  def close(self):
    self.clear_widgets()
    gMyRoot.remove_screen(self.screen)
      
  def screen_black(self):
    self.color.a = 1.0
    
  def screen_transition(self, t=0.5):
    self.color.a = 1.0
    anim = Animation(a = 0.0, duration = t)
    anim.start(self.color)
    
  def clear_widgets(self):
    self.clear_bg()
    self.clear_fx()
    self.clear_ui()
  
  def clear_fx(self): self.layer_fx.clear_widgets() 
  def clear_ui(self):self.layer_ui.clear_widgets()  
  def clear_bg(self): self.layer_bg.clear_widgets()
  def add_to_fx(self, widget): self.layer_fx.add_widget(widget)
  def add_to_ui(self, widget): self.layer_ui.add_widget(widget)   
  def add_to_bg(self, widget): self.layer_bg.add_widget(widget)
  def remove_from_fx(self, widget):
    if widget in self.layer_fx.children:
      self.layer_bg.remove_widget(widget)
  def remove_from_bg(self, widget):
    if widget in self.layer_bg.children:
      self.layer_bg.remove_widget(widget)
  def remove_from_ui(self, widget):
    if widget in self.layer_ui.children:
      self.layer_ui.remove_widget(widget)


class GameFrame(Singleton):
  def __init__(self):
    self.callback_on_closed = None
    self.ui = GameScreen()
    self.score = Score()
    
  def buttonBind(self, lfunc, rfunc):
    self.ui.bind_btn_left(lfunc)
    self.ui.bind_btn_right(rfunc)
    
  def start(self, callback_on_closed=None):
    self.callback_on_closed = callback_on_closed
    
    # clear ui
    self.ui.reset()
    self.ui.add_to_ui(self.score.widget)
    
    gStageMgr.setParentLayer(self.ui.layer_bg)
    gStageMgr.reset()
    
    gMyRoot.setTouchPrev(self.touchPrev)
    gMyRoot.regist(self)
    
    self.ui.screen_transition(1.0)
    self.ui.screen_black()
    self.ui.show()
    
  def touchPrev(self):
    self.ui.close()
    gMyRoot.remove(self)
    gMyRoot.setTouchPrev(None)
    if self.callback_on_closed:
      self.callback_on_closed()
    
  def update(self, dt):
    gStageMgr.update()

gGameFrame = GameFrame.instance()