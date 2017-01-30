import math, time
import Utility
from Utility import *
from kivy.animation import Animation
from Sprite import Sprite
from Particle import gFxMgr
from ResourceMgr import gResMgr

import GameFrame
from Constants import *
from Character import gCharacterMgr, gPlayer

class StuffManager(Singleton):
  def __init__(self):
    self.traps = []
    self.parentLayer = None
  
  def setParentLayer(self, parentLayer):
    self.parentLayer = parentLayer
  
  def reset(self):
    self.destroy()
    
    self.traps = []
    
    props = gResMgr.getProperty("trap")
    '''
    for i, prop in enumerate(props.properties):
      pos = (random.uniform(0, W), CHARACTER_SIZE[1] * 0.5) 
      trap = Trap(pos, CHARACTER_SIZE, prop)
      trap.reset()
      self.parentLayer.add_widget(trap.getSprite())
      self.traps.append(trap)
    '''
      
  def destroy(self):
    pass
      
  def update(self):
    for trap in self.traps:
      trap.update()
      

class Trap():
  def __init__(self, pos, size, prop):
    self.damage = prop["damage"]
    self.attackrange = prop["range"]
    self.sprite = Sprite(pos=pos, size=size, touchable=False, throwable=False, collision=False, texture=prop["image"].texture)
    self.particleName = PARTICLE_TRAP_FIRE + str(id(self))
    # create a fire trap particle
    particleInfo = dict(loop=-1,texture=gResMgr.getTexture('explosion'), fade=1, delay=Var(0.0,1.0), offset=Var((-20,20), (-20,20)),
      lifeTime=Var(0.5,1.5), sequence=[4,4], vel=Var([200, 500], [-200, 600]), scaling=Var(1.0, 2.5), gravity=Var(0.0))
    particle = gFxMgr.create_emitter(self.particleName, particleInfo, 10)
    particle.play_particle_with(self.sprite, True)
  
  def reset(self):
    pass
  
  def destroy(self):
    pass
    
  def __del__(self):
    gFxMgr.remove_emitter(self.particleName)
    self.particleName = ""
    
  def getSprite(self):
    return self.sprite
    
  def update(self):
    characters = gCharacterMgr.getCharacters()
    for character in characters:
      pass
    

gStuffMgr = StuffManager.instance()