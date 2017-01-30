import math, time
import Utility
from Utility import *
from kivy.animation import Animation
from Sprite import Sprite
from Particle import gFxMgr
from ResourceMgr import gResMgr

from Constants import *
import GameFrame
import Stage


class CharacterMgr(Singleton):
  def __init__(self):
    self.characters = []
    self.monsters = []
    self.player = None
    self.stageMgr = None
    self.parentLayer = None
  
  def setParentLayer(self, parentLayer):
    self.parentLayer = parentLayer
    
  def clear(self):
    for character in self.characters:
      character.destroy()
    self.monsters = []
    self.characters = []
  
  def reset(self, space):
    self.monsters = []
    self.characters = []
    self.stageMgr = Stage.gStageMgr
    
    # add player
    playerIndex = 4 # A bee
    props = gResMgr.getProperty("character")
    prop = props.properties[playerIndex]
    pos = (CHARACTER_SIZE[0], CHARACTER_SIZE[1] * 0.5)
    gPlayer.init(pos, CHARACTER_SIZE, prop)
    gPlayer.reset(space)
    self.parentLayer.add_widget(gPlayer.getSprite())
    self.player = gPlayer
    # bind input button
    GameFrame.gGameFrame.buttonBind(self.player.setMoveLeft, self.player.setMoveRight)
    self.characters.append(self.player)
      
    # add monster
    count = self.stageMgr.getEnemyCount()
    for i in range(count):
      n = playerIndex
      while n == playerIndex:
        n = random.randrange(0, len(props.properties))
      prop = props.properties[n]
      pos = (random.uniform(SEARCH_RANGE * 1.5, W), CHARACTER_SIZE[1] * 0.5) 
      monster = Monster()
      monster.init(pos, CHARACTER_SIZE, prop)
      monster.reset(space)
      self.parentLayer.add_widget(monster.getSprite())
      self.monsters.append(monster)
      self.characters.append(monster)
      
  def getMonsters(self):
    return self.monsters
  
  def getCharacters(self):
    return self.characters
  
  def update(self):
    for character in self.characters:
      character.update()
    
    # check collide
    hitList = set()
    collideOnlyPlayer = True
    for i, A in enumerate(self.characters):
      if A.isDead:
        continue
      posA = A.getPos()
      vA = A.getVelocity()
      lA = getDist(vA)
      nA = normalize(vA)
      for B in [gPlayer,] if collideOnlyPlayer else self.characters[i+1:]:
        if A == B or B.isDead:
          continue
        posB = B.getPos()
        dist = getDist(posA, posB)
        if dist < 100.0:
          v = normalize(sub(posA, posB))
          vB = B.getVelocity()
          lB = getDist(vB)
          nB = normalize(vB)
          d = -dot(v, nA)
          isHit = False
          if d > 0.0:
            isHit = True
            A.setVelocity(*sub(A.getVelocity(), vA))
            B.setVelocity(*add(B.getVelocity(), mul(vA, d)))
            rV = mul(v, dot(v, mul(nA, -1.0)))
            rV = sub(mul(rV, 2.0), mul(nA, -1.0))
            rV = mul(normalize(rV), lA * (1.0-d))
            A.setVelocity(*add(A.getVelocity(), rV))
          d = dot(v, nB)
          if d > 0.0:
            isHit = True
            A.setVelocity(*add(A.getVelocity(), mul(vB, d)))
            B.setVelocity(*sub(B.getVelocity(), vB))
            v = mul(v, -1.0)
            rV = mul(v, dot(v, mul(nB, -1.0)))
            rV = sub(mul(rV, 2.0), mul(nB, -1.0)) 
            rV = mul(normalize(rV), lB * (1.0-d))
            B.setVelocity(*add(B.getVelocity(), rV))
          # check damage
          if isHit and (gPlayer == A or gPlayer == B):
            if abs(v[0]) < DAMAGE_ANGLE:
              if posA[1] > posB[1]:
                hitList.add(B)
              else:
                hitList.add(A)
          # set damage and set score
          self.process_hit(hitList)
          
  def process_hit(self, hitList):         
    for hitted in hitList:
      hitted.setDamage()
      if hitted is not self.player:
        GameFrame.gGameFrame.score.addScore(SCORE_HIT)
      if hitted.isDead and hitted in self.characters:
        if hitted is not self.player:
          GameFrame.gGameFrame.score.addScore(SCORE_KILL)
        self.characters.remove(hitted)
  
  
class BaseCharacter():
  def __init__(self):
    self.prop = None
    self.maxHp = MAXHP
    self.hp = self.maxHp
    self.frameTime = 0.0
    self.damageTime = 0.0
    self.idleTime = 0.0
    self.patrolTime = 0.0
    self.isHitted = False
    self.isDead = False
    self.isMoveLeft = False
    self.isMoveRight = False
    self.target = None
    self.sprite = None
    self.state = StateMachine()
    self.STATE_IDLE = StateItem()
    self.STATE_PATROL = StateItem()
    self.STATE_TRACE = StateItem()
    self.STATE_DEAD = StateItem()
    self.state.addState(self.STATE_IDLE)
    self.state.addState(self.STATE_PATROL)
    self.state.addState(self.STATE_TRACE)
    self.state.addState(self.STATE_DEAD)
    
  def init(self, pos, size, prop):
    self.prop = prop
    self.sprite = Sprite(pos=pos, size=size, gravity=GRAVITY, friction=FRICTION, elastin=ELASTIN, collision=True, collisionSpace=WORLD_REGION, texture=prop["image"].texture)
    self.registStates()
    
  def reset(self, space):
    self.hp = self.maxHp
    self.target = None
    self.frameTime = 0.0
    self.damageTime = 0.0
    self.isHitted = False
    self.isDead = False
    self.isMoveLeft = False
    self.isMoveRight = False
    self.sprite.color.rgba = (1,1,1,1)
    self.sprite.collisionSpace = space
    self.state.setState(self.STATE_IDLE)
  
  def destroy(self):
    pass
    
  def getPos(self):
    return self.sprite.getPos()
    
  def getVelocity(self):
    return self.sprite.getVelocity()
  
  def setVelocity(self, vx, vy):
    self.sprite.setVelocity(vx, vy)
    
  def setMoveLeft(self, isMove):
    self.isMoveLeft = isMove
    
  def setMoveRight(self, isMove):
    self.isMoveRight = isMove
    
  def getSprite(self):
    return self.sprite
  
  def update(self):
    self.frameTime = Utility.getFrameTime()
    self.state.updateState()
    
    if self.isDead:
      return
      
    if self == gPlayer or self.state.isState(self.STATE_TRACE):
      self.updateTrace()
      
    if self.isHitted:
      self.updateHit()
  
  def updateTrace(self):     
      # set jump
      if self.sprite.isGround:
        ratio = abs(self.sprite.getVelocity()[0] / MAX_MOVE_SPEED)
        self.sprite.setVelocity(self.sprite.getVelocity()[0], JUMP + JUMP * ratio * 0.05)
        
      if self.isMoveLeft:
        vx, vy = self.getVelocity()
        if vy < 0.0:
          vy -= MOVE_ACCELERATE * self.frameTime
        if vx > -MAX_MOVE_SPEED:
          vx -= MOVE_ACCELERATE * self.frameTime
          if vx < -MAX_MOVE_SPEED:
            vx = -MAX_MOVE_SPEED
        self.setVelocity(vx, vy)
      elif self.isMoveRight:
        vx, vy = self.getVelocity()
        if vy < 0.0:
          vy -= MOVE_ACCELERATE * self.frameTime
        if vx < MAX_MOVE_SPEED:
          vx += MOVE_ACCELERATE * self.frameTime
          if vx > MAX_MOVE_SPEED:
            vx = MAX_MOVE_SPEED
        self.setVelocity(vx, vy)
      if not self.isMoveLeft and not self.isMoveRight:
        vx, vy = self.getVelocity()
        if vx != 0.0:
          if vx > 0.0:
            vx -= MOVE_ACCELERATE * self.frameTime
            if vx < 0.0:
              vx = 0.0
          else:
            vx += MOVE_ACCELERATE * self.frameTime
            if vx > 0.0:
              vx = 0.0
          self.setVelocity(vx, vy)
  
  def updateHit(self):
    if self.damageTime > DAMAGE_TIME:
      self.isHitted = False
      self.sprite.color.rgba = (1,1,1,1)
    else:
      self.damageTime += Utility.getFrameTime()
      bright = 1.0 + DAMAGE_BRIGHT * abs(math.sin(self.damageTime * DAMAGE_SPEED))
      self.sprite.color.rgba = (bright, bright, bright, bright - 0.7)
    
  def setDamage(self, n=1):
    if self.isHitted:
      return
    
    gFxMgr.get_emitter(PARTICLE_HIT).play_particle_with(self.sprite, True)
    self.isHitted = True
    self.damageTime = 0.0
    self.hp -= n
    if self.hp <= 0:
      self.hp = 0
      self.state.setState(self.STATE_DEAD)
      
  def registStates(self):
    self.STATE_DEAD.onEnter = self.stateDeadOnEnter
    
  def stateDeadOnEnter(self):
    self.isDead = True
    if self.sprite.parent:
      self.sprite.parent.remove_widget(self.sprite)
    

class Player(BaseCharacter, Singleton):  
  def reset(self, space):
    BaseCharacter.reset(self, space)
    self.state.setState(self.STATE_TRACE)


class Monster(BaseCharacter):
  def reset(self, space):
    BaseCharacter.reset(self, space)
    self.state.setState(self.STATE_PATROL)
  
  def registStates(self):
    BaseCharacter.registStates(self)
    self.STATE_IDLE.onEnter = self.stateIdleOnEnter  
    self.STATE_IDLE.onUpdate = self.stateIdleOnUpdate
    self.STATE_PATROL.onEnter = self.statePatrolOnEnter  
    self.STATE_PATROL.onUpdate = self.statePatrolOnUpdate  
    self.STATE_TRACE.onEnter = self.stateTraceOnEnter
    self.STATE_TRACE.onUpdate = self.stateTraceOnUpdate 
  
  def stateIdleOnEnter(self):
    self.idleTime = random.uniform(*IDLE_TIME)
    self.setVelocity(0, 0)
    
  def stateIdleOnUpdate(self):
    self.idleTime -= self.frameTime
    if self.idleTime < 0.0:
      self.state.setState(self.STATE_PATROL)
    
  def statePatrolOnEnter(self):
    speed = PATROL_MOVE_SPEED
    if random.uniform(0.0, 0.5) > 0.5:
      speed = -speed
    self.setVelocity(speed, 0)
    self.patrolTime = random.uniform(*PATROL_TIME)
      
  def statePatrolOnUpdate(self):
    self.patrolTime -= self.frameTime
    if self.patrolTime < 0.0:
      self.state.setState(self.STATE_IDLE)
         
    # search target
    target = Player.instance()
    if target and not target.isDead:
      dx = self.getPos()[0] - target.getPos()[0]
      if abs(dx) < SEARCH_RANGE:
        self.target = target
        self.state.setState(self.STATE_TRACE)
      
  def stateTraceOnEnter(self):
    pass
      
  def stateTraceOnUpdate(self):
    if self.target and not self.target.isDead:
      # update trace
      dx = self.getPos()[0] - self.target.getPos()[0]  
      dy = self.getPos()[1] - self.target.getPos()[1]
      # attack
      if ATTACK_RANGE < abs(dx):
        self.setMoveLeft(dx > 0.0)
        self.setMoveRight(not self.isMoveLeft)
      # evade
      '''
      elif abs(dx) < EVADE_RANGE and dy < 0.0:
        self.setMoveLeft(dx < 0.0)
        self.setMoveRight(not self.isMoveLeft)
      '''
    elif self.sprite.isGround:
      self.target = None
      self.setMoveLeft(False)
      self.setMoveRight(False)
      self.state.setState(self.STATE_PATROL)
    

gCharacterMgr = CharacterMgr.instance()
gPlayer = Player.instance()