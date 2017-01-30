import ConfigParser
import traceback

import Utility as Util
from Utility import *

directory = os.path.split(__file__)[0]
configFile = os.path.join(directory, "filebrowser.cfg")
szFileBrowserOpen = "filebrowser open layout"
szFileBrowserSaveAs = "filebrowser saveas layout"

#---------------------#
# CLASS : TouchableLabel
#---------------------#  
class TouchableLabel(Label):
  isDirType = False
  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      fileBrowser = FileBrowser.instance()
      selectfile = os.path.join(fileBrowser.lastDir, self.text[2:] if self.isDirType else self.text)
      if os.path.isdir(selectfile):
        fileBrowser.open_directory(selectfile)
      elif os.path.isfile(selectfile):
        fileBrowser.select_file(selectfile)
      
  def setType(self, isDir):
    self.isDirType = isDir
    if isDir:
      self.color = [1,1,0.5,2]
      self.text = "> " + self.text
    else:
      self.color = [1,1,1,1]
      
       
#---------------------#
# CLASS : FileBrowser
#---------------------#    
class FileBrowser(Singleton):
  def __init__(self):
    self.caller = None
    self.lastDir = os.path.abspath(".")
    self.mode = ""
    self.oldTouchPrev = None
    # filename input layout
    self.filenameLayout = BoxLayout(orientation = "horizontal", size_hint=(1, None))
    self.filenameInput = TextInput(text="input filename", multiline = False, padding_y="15dp", font_name=defaultFont, size_hint=(1,None))
    self.filenameInput.height = self.filenameInput.minimum_height
    self.filenameLayout.height = self.filenameInput.height
    self.filenameInput.bind(focus=self.inputBoxFocus) 
    # alternative paste function
    def paste():
      self.filenameInput.insert_text(gMyRoot.getClipboard())
    if gMyRoot.useAlternativePaste:
      self.filenameInput.paste = paste
      
    self.btn_ok = Button(text="Ok", size_hint=(0.2,1), background_color=[1,1,1,2])
    def func_ok(inst):
      if self.mode == szFileBrowserOpen:
        self.open_file()
      elif self.mode == szFileBrowserSaveAs:
        self.save_as()
    self.btn_ok.bind(on_release = func_ok)
    self.filenameLayout.add_widget(self.filenameInput)
    self.filenameLayout.add_widget(self.btn_ok)
    
    # file browser
    self.fileLayout = BoxLayout(orientation="vertical", size_hint=(1,None))
    self.fileSV = ScrollView(size_hint=(1,1))
    self.fileSV.add_widget(self.fileLayout)
    
    # current directory
    self.curDir = Label(text="", text_size=(W * 0.9, None), size_hint_y=None, height=kivy.metrics.dp(50))
    
    #  rowser layout
    self.browserLayout = BoxLayout(orientation="vertical", pos_hint={"top":1}, size_hint=(1,1))
    self.browserLayout.add_widget(self.curDir)
    self.browserLayout.add_widget(self.fileSV)
    self.browserLayout.add_widget(self.filenameLayout)
    self.popup = Popup(title = "File Browser", content=self.browserLayout, auto_dismiss=False, size_hint=(1, 0.8)) 
    self.load_config()

  def load_config(self):
    if not os.path.isfile(configFile):
      return
    parser = ConfigParser.SafeConfigParser()
    parser.read(configFile)
    
    # load document section
    lastDir_section = "LastDirectory"
    self.lastDir = "."
    if parser.has_section(lastDir_section):
      if parser.has_option(lastDir_section, "directory"):
        self.lastDir = parser.get(lastDir_section, "directory")
    
  def save_config(self):
    # make section
    if os.path.exists(self.lastDir):
      parser = ConfigParser.SafeConfigParser()
      lastDir_section = "LastDirectory"
      parser.add_section(lastDir_section)
      parser.set(lastDir_section, 'directory', self.lastDir) 
      with open(configFile, 'w') as f:
        parser.write(f)

  def open_directory(self, lastDir):
    absPath = os.path.abspath(lastDir)
    try:
      lastDir, dirList, fileList = os.walk(absPath).next()
    except:
      log(traceback.format_exc())
      toast("Cannot open directory")
      return False
    self.lastDir = absPath
    self.curDir.text = self.lastDir
    self.fileLayout.clear_widgets()
    fileList = sorted(fileList, key=lambda x:x.lower())
    dirList = sorted(dirList, key=lambda x:x.lower())
    fileList = dirList + fileList
    fileList.insert(0, "..")
    labelHeight = kivy.metrics.dp(25)
    for filename in fileList:
      absFilename = os.path.join(self.lastDir, filename)
      label = TouchableLabel(text=filename, font_size="15dp", size_hint_y = None, size=(W*0.9, labelHeight), shorten=True, shorten_from="right", halign="left")
      label.text_size = label.size
      label.setType(os.path.isdir(absFilename))
      self.fileLayout.add_widget(label)
    self.fileLayout.height = labelHeight * len(self.fileLayout.children)
  
  def open_file(self):
    self.close()
    if self.filenameInput.text:
      filename = os.path.join(self.lastDir, self.filenameInput.text)
      self.caller.callback_open_file(filename)
    
  def save_as(self):
    self.close()
    if self.filenameInput.text:
      filename = os.path.join(self.lastDir, self.filenameInput.text)
      self.caller.callback_save_as(filename)
    
  def select_file(self, selectfile):
    # lastdir
    self.lastDir, filename = os.path.split(selectfile)
    if not os.path.isdir(self.lastDir):
      self.lastDir = os.path.abspath(".")
    # set filename
    self.filenameInput.text = filename
      
  def showOpenLayout(self, caller):
    self.mode = szFileBrowserOpen
    self.btn_ok.text = "Open"
    self.openLayout(caller)
  
  def showSaveAsLayout(self, caller):
    self.mode = szFileBrowserSaveAs
    self.btn_ok.text = "Save"  
    self.openLayout(caller)
    
  def openLayout(self, caller):
    self.caller = caller
    if self.caller:
      if not hasattr(self.caller, "callback_open_file"):
        raise AttributeError("FileBrowser caller must implement callback_open_file(filename)")
      if not hasattr(self.caller, "callback_save_as"):
        raise AttributeError("FileBrowser caller must implement callback_save_as(filename)")
      if not hasattr(self.caller, "callback_filebrowser_closed"):
        raise AttributeError("FileBrowser caller must implement callback_filebrowser_closed()")
    if self.touchPrev != gMyRoot.getTouchPrev():
      self.oldTouchPrev = gMyRoot.getTouchPrev()
    gMyRoot.setTouchPrev(self.touchPrev)   
    self.filenameInput.text = ""
    self.popup.open()
    self.open_directory(self.lastDir)   
     
  def close(self):
    self.save_config()
    self.inputBoxForceFocus(False)
    self.popup.dismiss()
    gMyRoot.setTouchPrev(self.oldTouchPrev)
    if self.caller:
      self.caller.callback_filebrowser_closed()
     
  def touchPrev(self):
    if self.filenameInput.focus:
      self.inputBoxForceFocus(False)
    else:
      self.close()
    
  def inputBoxForceFocus(self, bFocus):
    if self.filenameInput and bFocus != self.filenameInput.focus:
      self.reFocusInputText = False
      self.filenameInput.focus = bFocus 
      
  def inputBoxFocus(self, inst, bFocus):
    bAlwaysPreserveFocus = True
    if not bFocus:
      if self.reFocusInputText:
        self.reFocusInputText = bAlwaysPreserveFocus
        inst.focus = True
    self.reFocusInputText = bAlwaysPreserveFocus
    self.refreshLayout()
    
  def refreshLayout(self):
    if self.browserLayout.size_hint_y != None:
      self.browserLayout.size_hint_y = None
      self.browserLayout_height = self.browserLayout.height
    
    if self.filenameInput.focus: 
      offset = gMyRoot.getKeyboardHeight() - self.browserLayout.pos[1]
      self.browserLayout.height = self.browserLayout_height - offset
    else:
      self.browserLayout.height = self.browserLayout_height
    