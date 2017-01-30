import math, time
import Utility
from Utility import *
from kivy.animation import Animation
from Sprite import Sprite, SpriteMgr
from Particle import gFxMgr
from Character import gCharacterMgr
from Stuff import gStuffMgr
from ResourceMgr import gResMgr

from Constants import *
import GameFrame
import Character

class StageManager(Singleton):
  def __init__(self):
    self.inited = False
    self.stageProps = None
    self.currentStage = None
    self.player = None
    self.parentLayer = None
    self.spriteMgr = None
  
  def setParentLayer(self, parentLayer):
    self.parentLayer = parentLayer
    
  def reset(self):
    self.spriteMgr = SpriteMgr.instance()
    self.spriteMgr.reset()
    
    self.stageProps = gResMgr.getProperty("stage")
    prop = self.stageProps.properties[0]
    stage = Stage(prop)
    stage.reset()
    self.parentLayer.add_widget(stage.layer_bg)
    self.currentStage = stage
    
    self.player = Character.Player.instance()
    
    # init fx manager
    gFxMgr.setLayer(stage.layer_fx)
    gFxMgr.reset()
    gFxMgr.setActive(True)
    # create a hit fx particle
    particleInfo = dict(texture=gResMgr.getTexture('star'), scaling=Var(0.3, 0.7), rotateVel=Var(720.0), rotate=Var(0.0, 360), 
      lifeTime=Var(1.5,2.0), vel=Var([-200.0, 400.0], [200.0, 500.0]), gravity=Var(2000.0))
    gFxMgr.create_emitter(PARTICLE_HIT, particleInfo, 3)
    
    # reset managers
    gStuffMgr.setParentLayer(stage.layer_bg)
    gStuffMgr.reset()
    gCharacterMgr.setParentLayer(stage.layer_bg)
    gCharacterMgr.reset(stage.getSpace())
    
  def getEnemyCount(self):
    return self.currentStage.getEnemyCount()
      
  def update(self):
    if self.currentStage:
      self.currentStage.update()
      gStuffMgr.update()
      gCharacterMgr.update()
      
      if self.player.isDead:
        self.reset()

# manage character spawn, background
class Stage():
  def __init__(self, prop):
    self.prop = prop
    self.size = [W * prop["width"], H * prop["height"]]
    self.scale = self.prop["scale"]
    self.layer_bg = Sprite(pos=[0,0], size=self.size, gravity=0, texture=prop["image"].texture)
    self.layer_fx = Sprite(pos=[0,0], size=[0,0])
    self.layer_bg.add_widget(self.layer_fx)
    self.layer_bg.setScale(self.scale)
    self.layer = None
  
  def reset(self):
    self.player = Character.Player.instance()
 
  def getScale(self):
    return self.scale
    
  def getSpace(self):
    return (0,0,self.size[0], self.size[1])
  
  def getEnemyCount(self):
    return self.prop["enemyCount"]
    
  def update(self):
    playerPos = self.player.getPos()
    x = max(min(0, cX - playerPos[0] * self.scale), min(W - self.size[0] * self.scale, (W - self.size[0] * self.scale) * 0.5))
    y = max(min(0, cY - playerPos[1] * self.scale), min(H - self.size[1] * self.scale, (H - self.size[1] * self.scale) * 0.5))
    self.layer_bg.setPos(x, y)
    

gStageMgr = StageManager.instance()