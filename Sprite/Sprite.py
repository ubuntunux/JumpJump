import Utility as Util
from Utility import *
import math
from kivy.graphics import Scale, Rotate, PushMatrix, PopMatrix, Translate, \
                          UpdateNormalMatrix



#---------------------#
# CLASS : SpriteMgr
#---------------------#
class SpriteMgr(Widget, Singleton, object):
  def __init__(self):
    Widget.__init__(self)
    self.spriteList = []
    Util.MyRoot.instance().regist(self)
  
  def reset(self):
    for sprite in self.spriteList:
      if sprite.parent:
        sprite.parent.remove_widget(sprite)
    self.spriteList = [] 
    
  def regist(self, sprite):
    if sprite not in self.spriteList:
      self.spriteList.append(sprite)     
  
  def remove(self, sprite):
    if sprite in self.spriteList:
      if sprite.parent:
        sprite.parent.remove_widget(sprite)
      self.spriteList.pop(sprite)
      
  def update(self, dt):
    for sprite in self.spriteList:
      if sprite.parent:
        sprite.update(dt)
        
#---------------------#
# CLASS : Sprite
#---------------------#
class Sprite(Widget, object):
  def __init__(self, pos=cXY, size=(100.0, 100.0), **kargs):
    Widget.__init__(self, pos=pos, size=size)
    self.box = None
    self.oldPos = None
    self.boxPos = None
    self.boxRot = None
    self.boxScale = None
    self.color = None
    self.source = None
    self.texture = None
    self.collision = False
    self.collisionSpace = (0.0, 0.0, Util.W, Util.H)
    self.elastin = 0.3
    self.friction = 0.8
    self.gravity = 0.0
    self.vel = [0.0, 0.0]
    self.rotate = 0.0
    self.rotateVel = 0.0
    self.scaling = 1.0
    self.radius = 0
    self.opacity = 1.0
    self.offset = (0.0, 0.0)
    self.realSize = (0,0)
    self.isGround = False
    self.isTouched = False
    self.isAttached = False
    self.touchable = True
    self.throwable = True
    self.touchOffset = (0,0)
    self.updateRotation = True
    self.updateTranslate = True
    self.attachOffsetList = {}
    
    # set argment
    for key in kargs:
      if not hasattr(self, key):
        raise AttributeError(self.__class__.__name__ + " not found " + key)
      setattr(self, key, kargs[key])
    # if vel is maybe tuple, convert to list
    self.vel = list(self.vel)
      
    # clamp
    self.elastin = max(min(self.elastin, 1.0), 0.0)
    
    if self.source != None:
      self.texture = self.source.texture
              
    with self.canvas:
      self.color = Color(1,1,1,1)
      self.box = Rectangle(texture=self.texture, pos=(0,0), size=self.size)
    with self.canvas.before:
      PushMatrix()
      self.boxPos = Translate(0,0)
      self.boxRot = Rotate(angle=0, axis=(0,0,1), origin=mul(mul(self.size, 0.5), self.scaling))
      self.boxScale = Scale(1,1,1)
    with self.canvas.after:
      PopMatrix()
        
    self.boxPos.x = self.pos[0] + (-self.size[0] * 0.5)
    self.boxPos.y = self.pos[1] + (-self.size[1] * 0.5)
    self.pos = (0,0)
    self.oldPos = (self.boxPos.x, self.boxPos.y)
    self.boxRot.origin = mul(mul(self.size, 0.5), self.scaling)
    self.boxRot.angle = self.rotate
    self.boxScale.xyz = (self.scaling, self.scaling, self.scaling) 
    self.realSize = mul(self.size, self.scaling)
    self.radius = math.sqrt((self.realSize[0] * 0.5) ** 2 + (self.realSize[1] * 0.5) ** 2)
    # regist
    SpriteMgr.instance().regist(self)
    
  def on_touch_down(self, touch):
    if not touch.grab_current and not self.isTouched:
      if self.touchable and not self.isAttached:
        if touch.pos[0] > self.boxPos.x and touch.pos[1] > self.boxPos.y and \
          touch.pos[0] < self.boxPos.x + self.realSize[0] and touch.pos[1] < self.boxPos.y + self.realSize[1]:
            self.isTouched = True
            self.setVelocity(0,0)
            self.touchOffset = sub((self.boxPos.x, self.boxPos.y), touch.pos)
            self.setUpdateTranslate(False)
            touch.grab_current = self
          
  def on_touch_move(self, touch):
    if touch.grab_current is self:
      self.setPos(*add(touch.pos, self.touchOffset))
      self.updateAttachObjPos()
  
  def on_touch_up(self, touch):
    if touch.grab_current is self:
      self.isTouched = False 
      self.setPos(*add(touch.pos, self.touchOffset))
      if touch.time_update > 0 and self.throwable:
        self.setVelocity(*add(self.vel, div((touch.dx, touch.dy), Util.fFrameTime)))
      self.setUpdateTranslate(True)
      touch.ungrab(self)
      
  def setUpdateTranslate(self, bUpdate):
    self.updateTranslate = bUpdate
    
  @property
  def center(self):
    return (self.boxPos.x + self.realSize[0] * 0.5, self.boxPos.y + self.realSize[1] * 0.5)
    
  @center.setter
  def center(self, centerPos):
    self.boxPos.x = centerPos[0] - self.realSize[0] * 0.5
    self.boxPos.y = centerPos[1] - self.realSize[1] * 0.5
    
  def getPos(self):
    return (self.boxPos.x, self.boxPos.y)
      
  def setPos(self, x, y):
    self.oldPos = (self.boxPos.x, self.boxPos.y)
    self.boxPos.x = x
    self.boxPos.y = y
    
  def getDir(self):
    return normalize(self.vel)
    
  def getVelocity(self):
    return (self.vel[0], self.vel[1])
    
  def setVelocity(self, vx, vy):
    self.vel[0] = vx
    self.vel[1] = vy
    
  def getRotate(self):
    return self.boxRot.angle
    
  def setRotate(self, angle):
    self.boxRot.angle = angle
    
  def getRotateVel(self):
    return self.rotateVel
    
  def setRotateVel(self, vel):
    self.rotateVel = vel
    
  def getScale(self):
    return self.scaling
    
  def setScale(self, scale):
    self.scaling = scale
    self.realSize = mul(self.size, self.scaling)
    self.boxScale.xyz = (scale, scale, scale)
  
  def setAttached(self, isAttached):
    self.isAttached = isAttached
    
  def attach(self, child, offset = None):
    if not isinstance(child, Sprite):
      raise TypeError("It is not instance of Sprite")
    if child not in self.attachOffsetList:
      child.setAttached(True)
      if offset == None:
        offset = sub(child.getPos(), self.getPos())
      self.attachOffsetList[child] = offset
      
  def detach(self, child):
    if child in self.attachOffsetList:
      child.setAttached(False)
      self.attachOffsetList.pop(child)
      
  def detach_all(self):
    while self.attachOffsetList:
      self.detach(self.attachOffsetList.keys()[0])
      
  def updateAttachObjPos(self):
    for child in self.attachOffsetList:
      child.setPos(*add(self.getPos(), self.attachOffsetList[child]))

  def update(self, fFrameTime):
    if self.updateTranslate and not self.isAttached:
      # set gravity
      if self.gravity != 0:
        self.vel[1] -= self.gravity * fFrameTime
      
      # adjust velocity, move
      self.oldPos = (self.boxPos.x, self.boxPos.y)
      if self.vel[0] != 0:
        self.boxPos.x += self.vel[0] * fFrameTime
      if self.vel[1] != 0:
        self.boxPos.y += self.vel[1] * fFrameTime
      
      if self.collision:
        if self.boxPos.x < self.collisionSpace[0]:
          self.boxPos.x = self.collisionSpace[0] * 2.0 - self.boxPos.x
          self.vel[0] = -self.vel[0] * self.friction
        elif self.boxPos.x > self.collisionSpace[2] - self.realSize[0]:
          self.boxPos.x = (self.collisionSpace[2] - self.realSize[0]) * 2.0 - self.boxPos.x
          self.vel[0] = -self.vel[0] * self.friction
        if self.boxPos.y < self.collisionSpace[1]:
          self.boxPos.y = self.collisionSpace[1] * 2.0 - self.boxPos.y
          self.vel[1] = -self.vel[1] * self.elastin
          if self.elastin == 0.0 or self.vel[1] > 0.0 and self.vel[1] <= abs(self.gravity * fFrameTime):
            self.vel[1] = 0.0
            self.boxPos.y = self.collisionSpace[1]
        elif self.boxPos.y > self.collisionSpace[3] - self.realSize[1]:
          self.boxPos.y = (self.collisionSpace[3] - self.realSize[1]) * 2.0 - self.boxPos.y
          self.vel[1] = -self.vel[1] * self.elastin
      
      if self.oldPos[1] == self.boxPos.y and self.vel[1] == 0.0:
        self.isGround = True
      else:
        self.isGround = False
        
      # update attach obj pos
      self.updateAttachObjPos()
          
    if self.updateRotation:
      if self.rotateVel != 0.0:
        self.boxRot.angle += self.rotateVel * fFrameTime