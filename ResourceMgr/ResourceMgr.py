import os

import Utility as Util
from Utility import *

from ActorProperty import ActorProperty

directory = "Gamedata"

class ID(int):pass

class Resource:
 def __init__(self, name):
  self.name = name
  self.tag = []
  self.image = None
  self.sound = None
  self.prop = None
  
 def addTag(self, tag):
   if not self.isTag(tag):
     self.tag.append(tag)
     self.tag.sort()
 
 def isTag(self, tag):
    if type(tag) == tuple or type(tag) == list:
      for i in tag:
        if i in self.tag:
          return True
      return False
    else:
      return tag in self.tag
      
 def isEmpty(self):
   return not (self.image or self.sound or self.prop)  

 def setImage(self, image):
  self.image = image
  if image:
    image.name = self.name
    image.resource = self

 def setSound(self, sound):
  self.sound = sound
  if sound:
    sound.name = self.name
    sound.resource = self
  
 def setProperty(self, prop):
  self.prop = prop
  if prop:
    prop.name = self.name
    prop.resource = self
  
 def getName(self):
  return self.name
  
 def getTags(self):
   return self.tag
   
 def hasImage(self):
   return self.image != None
   
 def hasTexture(self):
   return self.image != None
   
 def hasSound(self):
   return self.sound != None
   
 def hasProperty(self):
   return self.prop != None
   
 def getImage(self):
  return self.image
    
 def getTexture(self):
  return self.image.texture

 def getSound(self):
  return self.sound
  
 def getProperty(self):
  return self.prop
  
 def playSound(self, loop=False):
  if self.sound:
   self.loop = loop
   self.sound.play()
   
 def stopSound(self):
  if self.sound:
   self.sound.stop()


class ResourceMgr(Singleton):
 inited = False
 tags = {}
 resources = {}
 images = {}
 sounds = {}
 properties = {}
 
 def __init__(self):
   if self.inited:
     return
   self.inited = True
   ignoredir = os.path.join(os.path.abspath('.'), '.kivy')
  
   # write resource list
   with open('resources_log.txt','w') as f:
     for dirname, dirnames, filenames in os.walk('.'):
       if os.path.abspath(dirname)[:len(ignoredir)] == ignoredir:
         continue
       for filename in filenames:
         ext = os.path.splitext(filename)[1].lower()
         name = os.path.splitext(filename)[0]
         key = name.lower()
         filepath = os.path.join(dirname, filename)
         res = self.resources[key] if key in self.resources else Resource(key)
         if ext in ['.png','.jpg']:
           res.setImage(Image(source = filepath))
           res.addTag('image')
           self.regist_tag('image', res)
           self.images[key] = res
         elif ext in ['.mp3','.wav', '.ogg']:
           res.setSound(SoundLoader.load(filepath))
           res.addTag('sound')
           self.regist_tag('sound', res)
           self.sounds[key] = res
         elif ext == ".prop":
           prop = ActorProperty(filepath)
           res.setProperty(prop)
           res.addTag('property')
           self.regist_tag('property', res)
           self.properties[name] = res 
         else:
           continue
           
         for tag in filepath.split(os.sep)[1:-1]:
           tag = tag.lower()
           res.addTag(tag)
           self.regist_tag(tag, res)
         self.resources[key] = res
         # write resource list
         f.write(filepath+'\n')
         
 def loadProperty(self):
   for prop in self.properties:
     prop = self.properties[prop].getProperty()
     prop.load()
         
 def newProperty(self):
    index = 0
    name = "untitle"
    while True:
      name = "untitle" + str(index)
      filename = os.path.join(directory, name + ".prop")
      if not os.path.exists(filename):
        break
      index += 1
    prop = ActorProperty(filename)
    res = self.resources[name] if name in self.resources else Resource(name)
    res.setProperty(prop)
    res.addTag('property')
    self.regist_tag('property', res)
    for tag in filename.split(os.sep)[1:-1]:
      tag = tag.lower()
      res.addTag(tag)
      self.regist_tag(tag, res)
    self.properties[name] = res
    self.resources[name] = res
    resourceViewer.dirty = True
    return prop
    
 def removeProperty(self, name):
   if name in self.properties:
     res = self.properties.pop(name)
     res.setProperty(None)
     if res.isEmpty() and name in self.resources:
       self.resources.pop(name)
     resourceViewer.dirty = True
 
 def getPropertyNames(self):
   return self.properties.keys()
   
 def getPropertyList(self):
   return self.properties.values()
   
 def renameProperty(self, oldName, newName):
   if oldName != newName and \
       oldName in self.properties and \
       newName not in self.properties:
     resourceViewer.dirty = True
     oldRes = self.properties.pop(oldName)
     if newName not in self.resources:
       self.resources[newName] = Resource(newName)
     self.resources[newName].setProperty(oldRes.getProperty()) 
     oldRes.setProperty(None)
     if oldRes.isEmpty() and oldName in self.resources:
       self.resources.pop(oldName)
     self.properties[newName] = self.resources[newName]
         
 def getSoundIcon(self):
   return self.getTexture("speaker_icon")
            
 def getTagList(self):
   return self.tags.keys()

 def regist_tag(self, tag, resource):
   if tag not in self.tags:
     self.tags[tag] = [resource]
   elif resource not in self.tags[tag]:
     self.tags[tag].append(resource)
     
 def getResourceByTag(self, *tags):
   result = set()
   for tag in tags:
     if tag in self.tags:
       if result:
         result &= set(self.tags[tag])
       else:
         result = set(self.tags[tag])
     else:
       return []
   return list(result)
   
 def getCount(self):
  return len(self.resources)
 
 def getResourceNames(self):
   return self.resources.keys()
    
 def getResourceList(self):
   return self.resources.values()
 
 def getImageNames(self):
   return self.images.keys()
   
 def getImageList(self):
   return self.images.values()
 
 def getSoundNames(self):
   return self.sounds.keys()
   
 def getSoundList(self):
   return self.sounds.values()
    
 def getResource(self, name = ''):
   return self.resources[name] if name in self.resources else None
  
 def getResource_Rnd(self):
  return random.choice(self.resources.values())
 
 def getDefaultImage(self):
  return self.images["default_image"].getImage()
  
 def getImage(self, name=''):
  return self.images[name].getImage() if name in self.images else None

 def getRandomImage(self):
  return random.choice(self.images.values()).getImage()

 def getTexture(self , name=''):
  return self.images[name].getTexture() if name in self.images else None

 def getDefaultTexture(self):
  return self.images["default_image"].getTexture()
 
 def getRandomTexture(self):
  return random.choice(self.images.values()).getTexture()

 def getProperty(self , name=''):
  return self.properties[name].getProperty() if name in self.properties else None

 def getDefaultProperty(self):
  return self.properties["default_property"].getProperty()
 
 def getRandomProperty(self):
  return random.choice(self.properties.values()).getProperty()
 
 def getSound(self , name=''):
  return self.sounds[name].getSound() if name in self.sounds else None

 def getDefaultSound(self):
  return self.sounds["default_sound"].getSound()
 
 def getRandomSound(self):
  return random.choice(self.sounds.values()).getSound()
 
 def playSound(self, name='', loop=False):
  snd = self.getSound(name)
  if snd:
    snd.loop=loop
    snd.play()
    
 def stopSound(self, name=''):
  snd = self.getSound(name)
  if snd:
    snd.stop()

 def playRandomSound(self):
  snd = self.getRandomSound()
  if snd:
    snd.play()


class ResourceImage(Image):
  def __init__(self, resource, **kargs):
    super(ResourceImage, self).__init__(**kargs)
    if type(resource) == imageType:
      self.texture = resource.texture
    elif type(resource) == soundType:
      self.texture = gResMgr.getSoundIcon()
    self.resource = resource
    
  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      if type(self.resource) == soundType:
        resourceItem = SoundItem(self.resource.resource)
        resourceItem.on_touch_do()
      elif type(self.resource) == imageType:
        resourceItem = ImageItem(self.resource.resource)
        resourceItem.on_touch_do()


class ResourceItem(BoxLayout):
  iconSizeHintX = 0.15
  labelSizeHintX = 1.0 - iconSizeHintX
  labelHeight = kivy.metrics.dp(15)
  labelPadding = kivy.metrics.dp(0)
  layoutHeight = labelHeight * 5
  lineHeight = 0
  popupLayout = None
  gb = float(2 ** 30)
  mb = float(2 ** 20)
  kb = float(2 ** 10)
  
  def __init__(self, resource, *args, **kargs):
    BoxLayout.__init__(self, orientation="horizontal", height=self.layoutHeight, *args, **kargs)
    self.isTouched = False
    self.name = resource.getName()
    self.resource = resource
    self.image = None
    self.oldTouchPrev = None
    self.popup = None
    
    # select button
    button_width = kivy.metrics.dp(15) * 5
    self.select_btn = Button(text="Select", background_color=(0.6, 0.6, 0.6, 1.0), font_size="15dp", size_hint=(None, 1), width=button_width)  
    self.select_btn.bind(on_release=lambda x:resourceViewer.closeWidget(self.getResource()))
    self.add_widget(self.select_btn)
    
    # add layout
    self.iconLayout = AnchorLayout(size_hint=(None,None), size=(self.layoutHeight, self.layoutHeight), padding=[0,self.labelPadding,0,self.labelPadding])
    self.iconBtn = Button()
    self.iconBtn.bind(on_release=self.on_touch_do)
    self.iconLayout.add_widget(self.iconBtn)
    self.add_widget(self.iconLayout)
    
    # info label
    self.infoLayout = BoxLayout(orientation="vertical", size_hint=(self.labelSizeHintX, 1), padding=[0,self.labelPadding,0,self.labelPadding])
    self.info_label = Button(background_color=(0.7, 0.6, 0.5, 1.0), halign="left", font_size="10dp", size_hint=(1, 1), padding=[kivy.metrics.dp(5), ]*2)
    self.info_label.text = "Name : " + self.name
    self.info_label.text += "\nTags : " + ", ".join(resource.getTags())
    self.info_label.size = (self.width*self.labelSizeHintX - button_width, self.layoutHeight)
    self.info_label.text_size=self.info_label.size
    self.info_label.bind(on_release=self.on_touch_do)
    self.infoLayout.add_widget(self.info_label)
    self.add_widget(self.infoLayout)
  
  def refresh_info(self):
    pass   
    
  def getResource(self):
    return self.resource
  
  def getFileSize(self, filename):
    if os.path.exists(filename):
      size = os.path.getsize(filename)
      if size > self.gb:
        return "%.1fGb" % (size / self.gb)
      elif size > self.mb:
        return "%.1fMb" % (size / self.mb)
      elif size > self.kb:
        return "%.1fKb" % (size / self.kb)
      else:
        return "%dByte" % size
    else:
      return ""
  
  def on_touch_do(self, *args):
    self.oldTouchPrev = gMyRoot.getTouchPrev()
    gMyRoot.setTouchPrev(self.touchPrev)
    self.popupLayout = Button(background_color=(0,0,0,0.3), size_hint=(None,None), size=WH)
    self.popupLayout.bind(on_release=self.touchPrev)
    size = min(W, H) * 0.5
    img_size=(size,size) 
    scatter=Scatter(size=img_size, pos=sub(cXY, mul(img_size, 0.5)))
    scatter.add_widget(Image(source=self.image.source, size=img_size, allow_stretch=True))
    self.popupLayout.add_widget(scatter)
    self.popup = Popup(title=self.name, content=self.popupLayout, size_hint=(1,1))
    self.popup.open()

  def touchPrev(self, *args):
    gMyRoot.setTouchPrev(self.oldTouchPrev)
    self.popup.dismiss()
    
    
class ImageItem(ResourceItem):
  def __init__(self, resource, *args, **kargs):
    ResourceItem.__init__(self, resource, *args, **kargs)
    self.content = resource.getImage()
    self.image = resource.getImage()
    # add icon
    self.iconBtn.background_normal = self.image.source
    self.iconBtn.size_hint=(0.9, 0.9/self.image.image_ratio)  
    # add image info
    self.info_label.text = "\n".join([self.info_label.text, "Source : " + self.image.source, "Size : " + str(self.image.texture_size), "FileSize : " + self.getFileSize(self.image.source)])
 
  def getResource(self):
    return self.content
    
class SoundItem(ResourceItem):
  def __init__(self, resource, *args, **kargs):
    ResourceItem.__init__(self, resource, *args, **kargs)
    self.content = resource.getSound()
    self.image = gResMgr.getImage("speaker_icon")
    # add icon
    self.iconBtn.background_normal = self.image.source
    self.iconBtn.size_hint=(0.5, 0.5/self.image.image_ratio)  
    # add sound info
    self.info_label.text = "\n".join([self.info_label.text, "Source : " + self.content.source, "Length : " + str(self.content.length), "FileSize : " + self.getFileSize(self.content.source)])
  
  def getResource(self):
    return self.content
    
  def on_touch_do(self, *args):
    super(SoundItem, self).on_touch_do()
    if self.content.state == "play":
      self.content.stop() 
    self.content.play()
    # auto dissmiss
    Clock.schedule_once(self.touchPrev, max(1.0, self.content.length))
      
  def touchPrev(self, *args):
    Clock.unschedule(self.touchPrev)
    super(SoundItem, self).touchPrev()
    if self.content.state == "play":
      self.content.stop()
      
class PropertyItem(ResourceItem):
  def __init__(self, resource, *args, **kargs):
    ResourceItem.__init__(self, resource, *args, **kargs)
    self.content = resource.getProperty()
    self.image = gResMgr.getImage("doc_icon")
    # add icon
    self.iconBtn.background_normal = self.image.source
    self.iconBtn.size_hint=(0.5, 0.5/self.image.image_ratio)  
    # add file info
    self.refresh_info()
    
  def refresh_info(self):
    button_width = kivy.metrics.dp(15) * 5
    self.info_label.text = "Name : " + self.content.name
    self.info_label.text += "\nTags : " + ", ".join(self.resource.getTags())
    self.info_label.size = (self.width*self.labelSizeHintX - button_width, self.layoutHeight)
    self.info_label.text_size=self.info_label.size
    self.info_label.text = "\n".join([self.info_label.text, "Filename : " + self.content.filename, "FileSize : " + self.getFileSize(self.content.filename)]) 
  
  def on_touch_do(self, *args):
    self.content.open(resourceViewer.add_items)
    
    
class ResourceViewer(Singleton):
  def __init__(self):
    self.resMgr = None
    self.screen = None
    self.callbackOnClose = []
    self.oldTouchPrev = []
    self.oldScreen = []
    self.inited = False
    self.opened = False
    self.dirty = True
    
  def init(self):
    self.resMgr = ResourceMgr.instance()
    self.screen = Screen(name="Resource Viewer")
    self.callbackOnClose = []
    self.oldTouchPrev = []
    self.oldScreen = []
    self.items = []
    self.imageItems = []
    self.soundItems = []
    self.propertyItems = []
    layout = BoxLayout(orientation="vertical", size=WH)
    layout.add_widget(Widget(size_hint_y=None, height=kivy.metrics.dp(30)))
    # new property button
    self.btn_newProp = Button(text="New Property")
    def newProperty(*args):
      prop = gResMgr.newProperty()
      prop.open(self.add_items)
    self.btn_newProp.bind(on_release=newProperty)
    
    # menus
    menuHeight = kivy.metrics.dp(40)
    menuLayout = BoxLayout(orientatuon="horizontal", size_hint=(1,None), height=menuHeight)
    self.btn_image = ToggleButton(text="Image", state="down")
    self.btn_sound = ToggleButton(text="Sound")
    self.btn_prop = ToggleButton(text="Property")
    self.btn_image.bind(on_release=lambda x:self.add_items())
    self.btn_sound.bind(on_release=lambda x:self.add_items())
    self.btn_prop.bind(on_release=lambda x:self.add_items())
    text_search = TextInput(text="Search", size_hint_x=2, multiline=False, font_name=defaultFont, background_color=(.1, .1, .1, 1), foreground_color=(1,1,1,1), font_size="14dp", padding_x="20dp", padding_y="10dp")
    def focus(inst, focus):
      if focus:
        text_search.text = ""
    def search(textInput):
      self.add_items(textInput.text)
    text_search.bind(on_text_validate=search, focus=focus)
    
    menuLayout.add_widget(self.btn_image)
    menuLayout.add_widget(self.btn_sound)
    menuLayout.add_widget(self.btn_prop)
    menuLayout.add_widget(text_search)
    layout.add_widget(menuLayout)
    
    # scroll
    scrollLayout = BoxLayout(orientation="horizontal", size_hint=(1,1))
    scroll = ScrollView(size_hint=(1,1))
    # regist items
    self.resLayout = BoxLayout(orientation="vertical", size_hint=(1, None))
    scroll.add_widget(self.resLayout)
    
    self.add_items()
    
    scrollLayout.add_widget(scroll)
    layout.add_widget(scrollLayout)
    self.screen.add_widget(layout)
    self.inited = True
    
  def refresh_items(self):
    resourceNames = self.resMgr.getResourceNames()
    resourceNames.sort()
    imageItems = []
    soundItems = []
    propertyItems = []
    for resName in resourceNames:
      resource = self.resMgr.getResource(resName)
      image = resource.getImage()
      sound = resource.getSound()
      prop = resource.getProperty() 
     
      def refreshList(content, contentItems, addedItems, contentClass):
        if content:
          for item in contentItems:
            if content == item.content:
              addedItems.append(item)
              item.refresh_info()
              break
          else:
            contentItem = contentClass(resource, size_hint=(None,None), width=W)
            contentItems.append(contentItem)
            addedItems.append(contentItem)
            self.items.append(contentItem)
      refreshList(image, self.imageItems, imageItems, ImageItem)
      refreshList(sound, self.soundItems, soundItems, SoundItem)
      refreshList(prop, self.propertyItems, propertyItems, PropertyItem)
      
    def removeItems(contentItems, addedItems):
      removeList = []
      for item in contentItems:
        if item not in addedItems:
          removeList.append(item)
      for removeItem in removeList:
        contentItems.remove(removeItem)
        self.items.remove(removeItem)
    removeItems(self.imageItems, imageItems)
    removeItems(self.soundItems, soundItems)
    removeItems(self.propertyItems, propertyItems)   
    
  def add_items(self, searchText=""):
    if self.dirty:
      self.refresh_items()
      self.dirty = False
      
    self.resLayout.clear_widgets()
    resLayoutHeight = 0
    # new property
    if self.btn_prop.state=="down": 
      resLayoutHeight += self.btn_newProp.height
      self.resLayout.add_widget(self.btn_newProp)  
    # add items
    for item in self.items:
      if searchText:
        searchText = searchText.lower()
        res = gResMgr.getResource(item.name)
        if res and searchText in res.getName():
          # find tag
          pass
        else:
          for tag in res.getTags():
            if searchText in tag:
              # find tag
              break
          else:
            continue
        
      if self.btn_image.state == "down" and isinstance(item, ImageItem): 
        resLayoutHeight += item.height
        self.resLayout.add_widget(item)
      elif self.btn_sound.state=="down" and isinstance(item, SoundItem): 
        resLayoutHeight += item.height
        self.resLayout.add_widget(item)
      elif self.btn_prop.state=="down" and isinstance(item, PropertyItem): 
        resLayoutHeight += item.height
        self.resLayout.add_widget(item)
    self.resLayout.height = resLayoutHeight
    
  def openWidget(self, callbackOnClose=None):
    if not self.inited: 
      self.init()
    self.callbackOnClose.append(callbackOnClose)
    self.oldTouchPrev.append(gMyRoot.getTouchPrev())
    self.oldScreen.append(gMyRoot.get_current_screen())
    gMyRoot.setTouchPrev(self.closeWidget)
    gMyRoot.current_screen(self.screen)
    self.opened = True
    
  def closeWidget(self, resource=None):
    # restore old screen,touchprev
    if self.oldTouchPrev:
      lastTouchPrev = self.oldTouchPrev.pop()
      if lastTouchPrev:
        gMyRoot.setTouchPrev(lastTouchPrev)
    gMyRoot.remove_screen(self.screen)
    if self.oldScreen:
      lastSreen = self.oldScreen.pop()
      if lastSreen:
        gMyRoot.current_screen(lastSreen)
    if self.callbackOnClose:
      lastCallBack = self.callbackOnClose.pop()
      if lastCallBack:
        lastCallBack(resource)
    self.opened = False
      

#---------------------#
# set global instance
#---------------------#
gResMgr = ResourceMgr.instance()
resourceViewer = ResourceViewer.instance()
defaultImage = gResMgr.getDefaultImage()
defaultTexture = gResMgr.getDefaultTexture()
defaultSound = gResMgr.getDefaultSound()
defaultProperty = gResMgr.getDefaultProperty()
imageType = type(defaultImage)
textureType = type(defaultTexture)
soundType = type(defaultSound)
propertyType = type(defaultProperty)
resourceTypes = (imageType, textureType, soundType, propertyType)
types = [ID, int, float, str, list, imageType, soundType, propertyType]
typeNames = ["ID", "Int", "Float", "String", "List", "Image", "Sound", "Property"]
defaultValues = [0, 0, 0.0, "", [], defaultImage, defaultSound, defaultProperty]

gResMgr.loadProperty()