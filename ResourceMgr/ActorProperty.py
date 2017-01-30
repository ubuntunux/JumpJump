from collections import OrderedDict
import os
from copy import deepcopy
from functools import partial

from toast import toast
from Utility import *
from FileBrowser import FileBrowser
import ResourceMgr as ResMgr
from ResourceMgr import *

class ActorProperty:
  labelWidth = kivy.metrics.dp(150)
  labelHeight = kivy.metrics.dp(30)
  padding = kivy.metrics.dp(3)
  textSize = kivy.metrics.dp(15)
  font_size="15dp"
    
  # properties must be namedtuple
  def __init__(self, filename): 
    self.filename = filename
    self.directory = os.path.split(filename)[0]
    self.name = os.path.splitext(os.path.split(filename)[1])[0]
    self.loaded = False
    self.opened = False
    self.callback_on_close = None
    self.oldTouchPrev = None
    self.dirty = False
    self.removeRowButtons = []
    self.uniqueValues = {}

    self.fields = OrderedDict()
    self.properties = []
    self.lastFieldNameLabel = None
    self.lastInputField = None
    self.currentIndex = 0
    self.initialized = False
    
  def initialize(self):
    # layout
    self.popup = Popup(title="Create Actor", size_hint=(1, 1), autodismiss=True)
    layout = BoxLayout(orientation="vertical", size_hint=(1,1))
    
    # header layout
    headerLayout = BoxLayout(size_hint=(1, None), height=self.labelHeight)
    layout.add_widget(headerLayout)
    label = Label(text="Table name: ", font_size=self.font_size, font_name=defaultFont, multiline=False, size_hint=(0.5, 1))
    headerLayout.add_widget(label)
    self.nameText = TextInput(text=self.name, font_size=self.font_size, font_name=defaultFont, multiline=False, size_hint=(1, 1))
    self.nameText.oldText = self.name
    self.nameText.bind(on_text_validate=self.validateFilenameText)
    headerLayout.add_widget(self.nameText)
    
    # data fileds
    scroll = ScrollView(size_hint=(1,1))   
    self.anchorLayout = AnchorLayout(anchor_x="left", anchor_y="top", size_hint=(None, None), height=(self.labelHeight * 2))
    self.fieldLayout = BoxLayout(orientation="horizontal", size_hint=(1, 1))
    self.anchorLayout.add_widget(self.fieldLayout)
    scroll.add_widget(self.anchorLayout)
    layout.add_widget(scroll)
    self.popup.content = layout
    
    # dropdown - type change
    self.dropDown = DropDown(autodismiss=True, font_size=self.font_size, font_name=defaultFont, size_hint=(None, None), size=(self.textSize*8, self.labelHeight))
    self.dropDown.opened = False 
    def setDropDownOpened(opened):
      self.dropDown.opened = opened
    self.dropDown.bind(on_dismiss=lambda x:setDropDownOpened(False))
    # add type button
    for typeName in ResMgr.typeNames:
      btn = Button(text=typeName, size_hint=(1,None), font_size=self.font_size, height=self.labelHeight, background_color=(0.2, 0.2, 0.2, 1.0)) 
      btn.typeIndex = ResMgr.typeNames.index(typeName)
      btn.typeName = ResMgr.types[btn.typeIndex]
      btn.value = ResMgr.defaultValues[btn.typeIndex]
      btn.bind(on_release=lambda inst:self.typeChange(self.lastFieldNameLabel.text, inst.typeName, inst.value))
      self.dropDown.add_widget(btn)
    
    # build field
    self.delLayout = BoxLayout(orientation="vertical", size_hint=(None, 1), width=self.textSize*2)
    # empty widget
    self.delLayout.add_widget(Widget(size_hint=(1,2)))
    self.fieldLayout.add_widget(self.delLayout)
    self.anchorLayout.width += self.delLayout.width
    # add column
    for fieldName in self.fields.keys():
      self.addColumn(fieldName)
      
    # menu button layout
    menuBtnLayout = BoxLayout(size_hint=(1, None), height=self.labelHeight)
    layout.add_widget(menuBtnLayout)
    
    # add column button
    btn = Button(text="Add Column", font_size=self.font_size, size_hint_y=None, height=self.labelHeight)
    btn.bind(on_release=lambda x:self.addColumn("new"))
    menuBtnLayout.add_widget(btn)
    
    # add raw button
    btn = Button(text="Add Row", font_size=self.font_size, size_hint_y=None, height=self.labelHeight)
    btn.bind(on_release=lambda x:self.addRowDatas())
    menuBtnLayout.add_widget(btn)
    
    btn = Button(text="Clear")
    btn.bind(on_release=lambda x:self.clear()) 
    menuBtnLayout.add_widget(btn)
    
    # close button
    btn = Button(text="Close", font_size=self.font_size, size_hint_y=None, height=self.labelHeight)
    btn.bind(on_release=lambda x:self.close())
    menuBtnLayout.add_widget(btn)
    
    # load data
    self.load()
    
    # buid ui
    if len(self.properties) > 0:
      # self.properties must be empty before build ui. So, let it make copy data.
      props = deepcopy(self.properties)
      self.properties = []
      # create ui
      prop = props[0]
      types = [type(prop[key]) for key in prop]
      for i, column in enumerate(prop):
        self.addColumn(column, types[i])
      
      for prop in props:
        self.addRowDatas(prop)
    self.initialized = True
    
  def load(self):  
    if self.loaded or not os.path.exists(self.filename):
      return
    
    f = open(self.filename, "r")
    lines = list(f)
    f.close()
    
    # save field names
    columns = eval(lines[0].strip())
    # save types
    types = eval(lines[1].strip())
    types = [ResMgr.types[ResMgr.typeNames.index(t)] for t in types]
    
    self.properties = []
    for line in lines[2:]: 
      datas = eval(line.strip())
      for i in range(len(datas)):
        dataType = types[i]
        if dataType in ResMgr.resourceTypes:
          if dataType == ResMgr.imageType:
            datas[i] = ResMgr.gResMgr.getImage(datas[i])
          elif dataType == ResMgr.textureType:
            datas[i] = ResMgr.gResMgr.getTexture(datas[i])
          elif dataType == ResMgr.soundType:
            datas[i] = ResMgr.gResMgr.getSound(datas[i])
        else:
          datas[i] = dataType(datas[i])
      datas = OrderedDict(zip(columns, datas))
      self.properties.append(datas)
    self.loaded = True
        
  def save(self):
    if not os.path.exists(self.directory):
      os.mkdir(self.directory)
      
    # delete file because table is empty
    if len(self.fields.keys()) == 0:
      if os.path.exists(self.filename):
        os.remove(self.filename)
      ResMgr.gResMgr.removeProperty(self.name)
      return
      
    f = open(self.filename, "w")
    # save field names
    columns = [fieldName for fieldName in self.fields.keys()]
    f.writelines(str(columns)+"\n")
    # save types
    types = [self.fields[fieldName]["type"] for fieldName in self.fields]
    types = [ResMgr.typeNames[ResMgr.types.index(t)] for t in types]
    f.writelines(str(types)+"\n")
    
    # save data     
    for prop in self.properties:
      datas = map(self.resourceToString, prop.values())
      f.writelines(str(datas) + "\n")
    f.close()
    
  def resourceToString(self, resource):
      if type(resource) in ResMgr.resourceTypes:
         return resource.name
      else:
         return resource
         
  def clear(self):
    while self.removeRowButtons:
      self.removeRowDatas(self.removeRowButtons[0])
    
    fieldNames = self.fields.keys() 
    for fieldName in fieldNames:
      btn = self.fields[fieldName]["remove_button"]
      self.removeColumn(btn)
  
  def addColumn(self, fieldName, dataType=float):
      # check exist filed
      if fieldName in self.fields:
        newFieldName = fieldName
        i = 1
        while newFieldName in self.fields:
          newFieldName = "%s_%02d" % (fieldName, i)
          i += 1
        fieldName = newFieldName
      
      # add field, set attributes
      self.fields[fieldName] = {}
      self.fields[fieldName]["column"] = None
      self.fields[fieldName]["remove_button"] = None
      self.fields[fieldName]["label"] = None
      self.fields[fieldName]["inputField"] = []
      self.fields[fieldName]["icon"] = []
      self.fields[fieldName]["type"] = None
      self.fields[fieldName]["type_change"] = None
      
      # a column layout
      column = BoxLayout(orientation="vertical", size_hint=(None, 1), width=self.labelWidth)
      self.fields[fieldName]["column"] = column
      self.fieldLayout.add_widget(column)
      
      # field name
      fieldNameLayout = BoxLayout(orientation="horizontal")
      column.add_widget(fieldNameLayout)
      
      fieldNameLabel = TextInput(text=fieldName, font_size=self.font_size, font_name=defaultFont, multiline=False, size_hint=(1, None), height=self.labelHeight)
      fieldNameLabel.fieldName = fieldName
      fieldNameLabel.lastText = fieldNameLabel.text
      fieldNameLabel.bind(focus=self.focusFieldNameLabel, on_text_validate=self.validateFieldNameLabel)
      fieldNameLayout.add_widget(fieldNameLabel)
      self.fields[fieldName]["label"] = fieldNameLabel
      
      # remove property button
      btn = Button(text="X", font_name=defaultFont, font_size=self.font_size, size_hint=(None, 1), width=self.labelHeight)
      btn.bind(on_release=self.removeColumn)
      btn.fieldName = fieldName
      fieldNameLayout.add_widget(btn)
      self.fields[fieldName]["remove_button"] = btn
        
      # dataType change button - open the dropdown menu
      btn = Button(text="Type", size_hint_y=None, height=self.labelHeight)
      # choose data type to change type
      def openDataType(inst, fieldName):
        self.lastFieldNameLabel = fieldNameLabel
        self.dropDown.open(inst)
        self.dropDown.opened = True
      btn.bind(on_release = lambda inst:openDataType(inst, fieldName))
      column.add_widget(btn)
      
      # set reference data tyle button
      self.fields[fieldName]["type_change"] = btn
      
      # add datas
      for i in range(len(self.properties)):
        self.addColumnData(column, fieldName, i)
      
      # set data type
      self.typeChange(fieldName, dataType, ResMgr.defaultValues[ResMgr.types.index(dataType)])
      
      # refresh layout height
      self.anchorLayout.width += self.labelWidth
      
  def removeColumn(self, btnInstance):
    # pop
    field = self.fields.pop(btnInstance.fieldName)
    layout = field["column"]
    layout.parent.remove_widget(layout)
    # pop properties
    for prop in self.properties:
      prop.pop(btnInstance.fieldName)
    # pop unique id column
    if btnInstance.fieldName in self.uniqueValues:
      self.uniqueValues.pop(btnInstance.fieldName)
    
    # refresh layout height
    self.anchorLayout.width -= self.labelWidth
  
  def addColumnData(self, columnLayout, fieldName, index, value=None):
      # data input field
      inputField = TextInput(size_hint=(1,1), font_size=self.font_size, font_name=defaultFont, multiline=False)
      # input field layout
      inputFieldLayout = BoxLayout(size_hint=(1, None), height=self.labelHeight)
      inputFieldLayout.add_widget(inputField)
      columnLayout.add_widget(inputFieldLayout)
      
      # user data
      inputField.fieldName = fieldName # fieldname
      inputField.lastText = "" # last value for rollback
      inputField.bind(focus=self.focusInputField, on_text_validate=self.validateInputField)
      self.fields[fieldName]["inputField"].append(inputField)
      self.fields[fieldName]["icon"].append(None)
      defaultType = self.fields[fieldName]["type"] or float
      typeIndex = ResMgr.types.index(defaultType)
      
      defaultValue = value or ResMgr.defaultValues[typeIndex]
      self.setColumnData(fieldName, index, defaultType, defaultValue)
    
  def setColumnData(self, fieldName, index, dataType, value):   
    if dataType not in ResMgr.types:
      return
      
    # set data type
    inputField = self.fields[fieldName]["inputField"][index]
    prop = self.properties[index]
    if dataType in ResMgr.resourceTypes:
      if type(value) in (unicode, str):
        if dataType == ResMgr.imageType:
          value = ResMgr.gResMgr.getImage(value)
        elif dataType == ResMgr.textureType:
          value = ResMgr.gResMgr.getTexture(value)
        elif dataType == ResMgr.soundType:
          value = ResMgr.gResMgr.getSound(value)
      if value == None:
        value = ResMgr.defaultValues[ResMgr.types.index(dataType)]
      # resource data type
      prop[fieldName] = value
      inputField.text = value.resource.name
      inputField.lastText = inputField.text
      self.validateInputField(inputField)
    else:
      # check unique type, and if it's not unique let it make unique
      if dataType == ResMgr.ID:
        if value in self.uniqueValues[fieldName]:
          for i in range(len(self.uniqueValues[fieldName])+1):
            if i not in self.uniqueValues[fieldName]:
              value = i
              self.uniqueValues[fieldName].append(i)
              break
        else:
          self.uniqueValues[fieldName].append(value)
      # general data type
      prop[fieldName] = value
      inputField.text = str(value)
      inputField.lastText = inputField.text
      # remove icon
      self.removeResourceIcon(fieldName, index)
  
  # type changed
  def typeChange(self, fieldName, newType, defaultValue=None): 
    if fieldName in self.fields and self.fields[fieldName]["type"] == newType:
      return
    typeIndex = ResMgr.types.index(newType)
    dataType = newType
    value = ResMgr.defaultValues[typeIndex] if defaultValue == None else defaultValue
    dataTypeBtn = self.fields[fieldName]["type_change"]
    dataTypeBtn.text = ResMgr.typeNames[typeIndex]
    
    # set new type
    self.fields[fieldName]["type"] = dataType
    
    # add unique type
    if dataType == ResMgr.ID:
      self.uniqueValues[fieldName] = []
    
    # set fielddata to default value of the type  
    for i in range(len(self.properties)):
      self.setColumnData(fieldName, i, dataType, value)
    # close drop down
    self.dropDown.dismiss()
    
  def addRowDatas(self, datas=None):
    if len(self.fields) == 0:
      return
    # add raw data
    self.properties.append(OrderedDict())
    index = len(self.properties)-1
    # add raw data remive button
    btn = Button(text="X")
    self.delLayout.add_widget(btn)
    btn.bind(on_release=self.removeRowDatas)
    self.removeRowButtons.append(btn)
    
    # add column datas
    for fieldName in self.fields.keys():
      column = self.fields[fieldName]["column"]
      value = datas[fieldName] if datas else None
      self.addColumnData(column, fieldName, index, value)
    # refresh layout height
    self.anchorLayout.height += self.labelHeight
  
  def removeRowDatas(self, inst):
    # child[0] is empty widget, so do -1
    index = len(self.delLayout.children) - self.delLayout.children.index(inst)-2
    prop = self.properties.pop(index)
    # pop unique value
    for fieldName in prop.keys():
      if self.fields[fieldName]["type"] == ResMgr.ID and prop[fieldName] in self.uniqueValues[fieldName]:
        self.uniqueValues[fieldName].remove(prop[fieldName])
    self.delLayout.remove_widget(inst)
    self.removeRowButtons.remove(inst)
    
    for key in self.fields.keys():
      inputField = self.fields[key]["inputField"][index]
      icon = self.fields[key]["icon"][index]
      inputFieldLayout = inputField.parent 
      inputFieldLayout.remove_widget(inputField)
      if inputFieldLayout.parent:
        inputFieldLayout.parent.remove_widget(inputFieldLayout)   
      if icon:
        inputFieldLayout.remove_widget(icon)
      self.fields[key]["inputField"].pop(index)
      self.fields[key]["icon"].pop(index)
    # refresh layout height
    self.anchorLayout.height -= self.labelHeight
    
  def removeResourceIcon(self, fieldName, index):
    # remove icon
    icon = self.fields[fieldName]["icon"][index]
    if icon and icon.parent:
      icon.parent.remove_widget(icon)
      self.fields[fieldName]["icon"][index] = None
 
  def open(self, callback_on_close):
    if not self.initialized:
      self.initialize()
      
    self.opened = True
    self.callback_on_close = callback_on_close
    self.oldTouchPrev = gMyRoot.getTouchPrev()
    gMyRoot.setTouchPrev(self.touchPrev)
    self.popup.open()
    
  def close(self):
    self.opened = False
    self.save()
    gMyRoot.setTouchPrev(self.oldTouchPrev)
    self.popup.dismiss()
    self.dropDown.dismiss()
    
    if self.callback_on_close:
      self.callback_on_close()
      self.callback_on_close = None
    
  def openResourceviewer(self):
    self.popup.dismiss()
    ResMgr.resourceViewer.openWidget(self.setDataToResource)
    
  def validateFilenameText(self, nameText):
    nameText.text = nameText.text.lower()
    newFilename = os.path.join(self.directory, nameText.text + ".prop")
    if nameText.text == "" or os.path.exists(newFilename):
      nameText.text = nameText.oldText
      return
    elif nameText.text == nameText.oldText:
      return
        
    nameText.oldText = nameText.text
    oldFilename = self.filename
    self.filename = newFilename
    
    # rename resource
    ResMgr.gResMgr.renameProperty(self.name, nameText.text)
    
    # rename old file
    if os.path.exists(oldFilename):
      os.rename(oldFilename, self.filename)
    
  def focusFieldNameLabel(self, fieldNameLabel, focus):
    if focus:
      self.lastFieldNameLabel = fieldNameLabel
    else:
      self.validateFieldNameLabel(fieldNameLabel)
      
  def validateFieldNameLabel(self, fieldNameLabel):
    if fieldNameLabel.text == "" or (fieldNameLabel.text != fieldNameLabel.lastText and fieldNameLabel.text in self.fields):
      log("Wrong field name.")
      # rollback
      fieldNameLabel.text = fieldNameLabel.lastText
    # change field name
    elif fieldNameLabel.text != fieldNameLabel.lastText:
      if fieldNameLabel.lastText in self.fields:
        oldFieldName = fieldNameLabel.lastText
        newFieldName = fieldNameLabel.text
        column = self.fields.pop(oldFieldName)
        self.fields[newFieldName] = column
        fieldNameLabel.lastText = newFieldName
        # replace unique values
        if self.fields[newFieldName]["type"] == ResMgr.ID:
          self.uniqueValues[newFieldName] = self.uniqueValues.pop(oldFieldName)
        
        # edit property
        for prop in self.properties:
          prop[newFieldName] = prop.pop(oldFieldName)
        
        def setFieldName(item, newFieldName):
          if hasattr(item, "fieldName"):
            item.fieldName = newFieldName
            
        for attr in self.fields[newFieldName].keys():
          if type(self.fields[newFieldName][attr]) in (list, tuple):
            for item in self.fields[newFieldName][attr]:
              setFieldName(item, newFieldName)
          else:
            setFieldName(self.fields[newFieldName][attr], newFieldName)
    
  def focusInputField(self, inputField, focus):
    if focus:
      self.lastInputField = inputField
      if self.fields[self.lastInputField.fieldName]["type"] in ResMgr.resourceTypes:
        inputField.focus = False
        self.openResourceviewer()
    else:
      self.validateInputField(inputField)
      
  def validateInputField(self, inputField):  
    if inputField.text == None:
      inputField.text = ""
      
    fieldName = inputField.fieldName
    index = self.fields[fieldName]["inputField"].index(inputField)
    prop = self.properties[index]
    
    self.lastInputField = inputField
    dataType = self.fields[inputField.fieldName]["type"]
    # check resource type
    if dataType in ResMgr.resourceTypes:
      resource = ResMgr.gResMgr.getResource(inputField.text)
      if resource:
        if dataType == ResMgr.imageType:
          self.setDataToResource(resource.getImage(), inputField)
        elif dataType == ResMgr.soundType:
          self.setDataToResource(resource.getSound(), inputField)
        # backup current value
        inputField.lastText = inputField.text
      else:
        # rollback
        inputField.text = inputField.lastText
    # general data type - int, float....
    else:
      typeIndex = ResMgr.types.index(dataType)
      try:
        # try to convert data type
        value = dataType(self.lastInputField.text)
        prop[fieldName] = value
        # backup current value
        inputField.lastText = inputField.text
      except:
        log("Wrong type inputed.")
        # rollback
        inputField.text = inputField.lastText
        
  def setDataToResource(self, resource, inputField=None):
    if self.opened:
      self.popup.open()
      
    if not inputField:
      inputField = self.lastInputField
    
    index = self.fields[inputField.fieldName]["inputField"].index(inputField)
    dataType = self.fields[inputField.fieldName]["type"]
    prop = self.properties[index]
    if type(resource) == dataType:
      inputField.text = resource.name
      inputField.lastText = inputField.text
      prop[inputField.fieldName] = resource
      # remove icon and resource viewer button
      self.removeResourceIcon( inputField.fieldName, index )
      
      # add icon
      icon = ResMgr.ResourceImage(resource=resource, size_hint=(None,1))
      self.fields[inputField.fieldName]["icon"][index] = icon
      inputField.parent.add_widget(icon)
    
  def touchPrev(self):
    if self.dropDown.opened:
      self.dropDown.dismiss()
    elif self.nameText.focus:
      self.nameText.focus = False
    elif self.lastFieldNameLabel and self.lastFieldNameLabel.focus:
      self.lastFieldNameLabel.focus = False
    elif self.lastInputField and self.lastInputField.focus:
      self.lastInputField.focus = False
    else:
      self.close()