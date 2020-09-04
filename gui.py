# notes:
# the program flow goes as follows: __main__ -> ltEditor.__init__ -> ltEditor.startMenu() -> ltEditor.main(), the last being the actual main


#---imports---
import tkinter as tk
from tkinter import ttk
import configparser
from tkinter import filedialog
from PIL import ImageTk, Image
import enum
import os
from pathlib import Path
#own imports
import ltc
import jobh
import windowItemModule as wim
import tooltip
#---core variables---
root = tk.Tk()
#config = configparser.ConfigParser()
#---core functions---
def switchFileTypes(ltEditorObj):
    ltEditorObj.__del__(wclosed=False)
    newLte = LtEditor(root)
def resource_path(relative_path):
    #""" Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
def getWindowSize(window):
    width = window.winfo_width()
    height = window.winfo_height()
    midwidth = round(width/2)
    midheight = round(height/2)
    return (midwidth,midheight)

#---classes / gui---
class ObjectType(enum.Enum):
    LT = "LogicTree"
    BL = "BranchingLevel"
    BS = "BranchSet"
    BR = "Branch"
class ViewObject:
    def __init__(self,master,type,ltcobject,file_type,ltEditor,parent=None,xpos=None,ypos=None):
        self.master = master # window / frame
        self.parent = parent # viewobject parent
        self.type = type # type of viewobject, see ObjectType enum
        self.ltcobject = ltcobject # actual logic tree object
        self.level = None # level / depth of branching
        self.file_type = file_type
        self.lteditor = ltEditor
        self.add_child_name = None
        self.xpos = xpos
        self.ypos = ypos

        #detect level
        if self.type == ObjectType.BL:
            self.level = 0
        elif self.type == ObjectType.BS:
            self.level = 1
        elif self.type == ObjectType.BR:
            self.level = 2
        elif self.type is not ObjectType.LT:
            raise ValueError("Invalid ViewObject type, refer to ObjectType enum")

        #---gui
        self.Frame = tk.Frame(self.master)
        self.Frame.pack(anchor=tk.NW,padx=5,fill="x")

        #canvas
        if self.type is not ObjectType.BL and self.type is not ObjectType.LT:
            size = 25
            self.CanvasWidth = size+(self.level*size)
            self.Canvas = tk.Canvas(self.Frame,height=size,width=self.CanvasWidth,bg="blue")
            self.Canvas.config(bg=self.master.master.master["background"])
            self.Canvas.pack(side=tk.LEFT)

            half = round(size/2)+2 # half of size
            posx = self.CanvasWidth-half # pos x

            self.Canvas.create_line(posx,0,posx,half) # vertical line
            self.Canvas.create_line(posx,half,self.CanvasWidth,half) # horizontal line

        # label
        if self.type is not ObjectType.LT:
            self.Label = tk.Label(self.Frame,anchor="w")
            self.label_def = self.Label["bg"]
            add_child_name = ObjectType.BL
            str = None
            if self.type == ObjectType.BL:
                str = "BranchingLevel (branchingLevelId: %s)"%self.ltcobject.blId
                add_child_name = ObjectType.BS
            elif self.type == ObjectType.BS:
                add_child_name = ObjectType.BR
                if self.file_type == "Source Model Logic Tree":
                    str = "BranchSet (branchSetId: {})(uncertaintyType: {})".format(self.ltcobject.realBsId, self.ltcobject.uncertaintyType)
                elif self.file_type == "GMPE":
                    str = "BranchSet (branchSetId: {})(uncertaintyType: {})(applyToTectonicRegionType: {})".format(self.ltcobject.realBsId, self.ltcobject.uncertaintyType,self.ltcobject.applyToTectonicRegionType)
            elif self.type == ObjectType.BR:
                if self.file_type == "Source Model Logic Tree":
                    str = "Branch (branchId: {})(uncertaintyModel: {})(uncertaintyWeight: {})".format(self.ltcobject.realBId, self.ltcobject.uncertaintyModel,self.ltcobject.uncertaintyWeight)
                elif self.file_type == "GMPE":
                    str = "Branch (branchId: {})(gmpeTable: {})(uncertaintyWeight: {})".format(self.ltcobject.realBId, self.ltcobject.GMPETable,self.ltcobject.uncertaintyWeight)
            self.Label.config(text=str,width=200)
            def enter(e):
                self.Label.config(bg="gainsboro")
                self.lteditor.rightclickable = False
                #print(self.lteditor.rightclickable)
            def leave(e):
                self.Label.config(bg=self.label_def)
                self.lteditor.rightclickable = True
                #print(self.lteditor.rightclickable)
            self.Label.bind("<Enter>", enter)
            self.Label.bind("<Leave>", leave)
            self.Label.pack(side=tk.LEFT)

            self.add_child_name = add_child_name

            # rightclick menu
            m = tk.Menu(self.Label, tearoff=0)
            if type is not ObjectType.BR:
                m.add_command(label="Add "+add_child_name.value,command=self.addW)
                m.add_separator()
            m.add_command(label="Edit",command=self.editW)
            m.add_separator()
            m.add_command(label="Delete",command=self.delete)

            # binds
            def right_click_popup(event):
                try:
                    self.xpos = event.x_root
                    self.ypos = event.y_root
                    popup = m.tk_popup(event.x_root, event.y_root)
                finally:
                    m.grab_release()
            def double_click_popup(event):
                try:
                    self.editW(xpos=event.x_root,ypos=event.y_root)
                finally:
                    m.grab_release()
            self.Label.bind("<Button-3>", right_click_popup)
            self.Label.bind('<Double-Button-1>', double_click_popup)
        else:
            self.add_child_name = ObjectType.BL
    def __del__(self,total_del=False):
        try:
            self.Frame.destroy()
        except:
            pass
        if total_del==True:
            self.delete()
    def addW(self,**kwargs):
        self.windowOptions = {}
        self.windowOptions["_values"] = {}
        #gui
        top = tk.Toplevel(self.master)

        top.resizable(False,False)
        top.iconbitmap(self.lteditor.icon)
        self.windowOptions["top"]=top
        top.title("Add "+self.add_child_name.value)

        if self.add_child_name == ObjectType.BL:
            width=100
            height=80
            self.placeInCenter(width,height,window=top,xpos=self.xpos,ypos=self.ypos)
        elif self.add_child_name == ObjectType.BS:
            width=200
            height=100
            self.placeInCenter(width,height,window=top,xpos=self.xpos,ypos=self.ypos)
        elif self.add_child_name == ObjectType.BR:
            width=330
            height=150
            self.placeInCenter(width,height,window=top,xpos=self.xpos,ypos=self.ypos)

        #properties
        properties = ltc.Properties()
        for property in properties.getImportance(1,type=self.add_child_name):
            if property.native_file_type is None or property.native_file_type == self.file_type:
                self.windowOptions["_values"][property.name] = tk.StringVar()
                if property.auto == True:
                    self.windowOptions[property.name+"O"] = wim.AutoObject(self.windowOptions["top"],wim.windowObject.ENTRY,label=property.name+":",stringvar=self.windowOptions["_values"][property.name],_checkbuttoncommand=lambda checked:top.geometry(""))
                else:
                    self.windowOptions[property.name+"O"] = wim.Entry(self.windowOptions["top"],type=wim.windowObject.FULL_ENTRY,label=property.name+":",stringvar=self.windowOptions["_values"][property.name])
        def submit(properties):
            dict = {}
            for key,stringvar in self.windowOptions["_values"].copy().items():
                if key == "bsId":
                    dict["realBsId"] = stringvar.get()
                elif key == "bId":
                    dict["realBId"] = stringvar.get()
                else:
                    dict[key] = stringvar.get()
                    if dict[key] == "" and properties.getProperty(key,1,type=self.add_child_name).auto is not True:
                        self.lteditor.createPopup(wtitle="Error",wdescription="Please enter a valid "+key)
                        return 'No '+key
            if self.add_child_name.value == ObjectType.BL.value:
                if dict["blId"] == "":
                    dict["blId"] = "def"
                self.lteditor.logic_tree.addBranchingLevel(**dict)
            elif self.add_child_name.value == ObjectType.BS.value:
                if dict["realBsId"] == "":
                    dict["realBsId"] = "def"
                if dict["uncertaintyType"] == "":
                    dict["uncertaintyType"] = "default"
                self.ltcobject.addBranchSet(**dict)
            elif self.add_child_name.value == ObjectType.BR.value:
                if dict["realBId"] == "":
                    dict["bId"] = "def"
                    dict["realBId"] = None
                self.ltcobject.addBranch(**dict)
            self.lteditor.outputLogicTree()
            self.windowOptions["top"].destroy()

        self.windowOptions["submitButtonO"] = wim.SubmitButton(self.windowOptions["top"],buttontext="Add",no_destroy=True,command=lambda: submit(properties))
    def editW(self,xpos=None,ypos=None,**kwargs):
        self.windowOptions = {}
        self.windowOptions["_values"] = {}
        #gui
        top = tk.Toplevel(self.master)

        top.resizable(False,False)
        top.iconbitmap(self.lteditor.icon)
        self.windowOptions["top"]=top
        top.title("Edit "+self.type.value)

        if self.type == ObjectType.BL:
            width=380
            height=80
        elif self.type == ObjectType.BS:
            width=380
            height=100
        elif self.type == ObjectType.BR:
            width=380
            height=150
        if xpos == None and ypos == None:
            self.placeInCenter(width,height,window=top,xpos=self.xpos,ypos=self.ypos)
        else:
            self.placeInCenter(width,height,window=top,xpos=xpos,ypos=ypos)

        #properties
        properties = ltc.Properties()
        for property in properties.getImportance(1,type=self.type):
            if property.native_file_type is None or property.native_file_type == self.file_type:
                self.windowOptions["_values"][property.name] = tk.StringVar()
                self.windowOptions[property.name+"O"] = wim.Entry(self.windowOptions["top"],type=wim.windowObject.FULL_ENTRY,label=property.name+":",stringvar=self.windowOptions["_values"][property.name])
                self.windowOptions["_values"][property.name].set(getattr(self.ltcobject,property.name))

        def submit():
            for key,stringvar in self.windowOptions["_values"].copy().items():
                newkey = key
                if key == "bsId":
                    newkey = "realBsId"
                elif key == "bId":
                    newkey = "realBId"
                else:
                    if stringvar.get() == "":
                        self.lteditor.createPopup(wtitle="Error",wdescription="Please enter a valid "+newkey)
                        return 'No '+newkey
                setattr(self.ltcobject,newkey,stringvar.get())

            self.windowOptions["top"].destroy()
            self.lteditor.outputLogicTree()

        self.windowOptions["submitButtonO"] = wim.SubmitButton(self.windowOptions["top"],buttontext="Add",command=submit,no_destroy=True)
        top.geometry("")
    def delete(self):
        if self.type == ObjectType.BL:
            self.ltcobject.logicTree.deleteBranchingLevel(self.ltcobject.blId)
        elif self.type == ObjectType.BS:
            self.ltcobject.branchLevel.deleteBranchSet(realBsId=self.ltcobject.realBsId)
        elif self.type == ObjectType.BR:
            self.ltcobject.branchSet.deleteBranch(self.ltcobject.bId)
        self.lteditor.outputLogicTree()
        del self
    def placeInCenter(self,width,height,window=None,place=True,xpos=None,ypos=None,geostring_only=False): #fixes x,y placement of window
        if window is None:
            window=self.master
        if xpos is not None and ypos is not None:
            x = xpos - (width //2)
            y = ypos - (height //2)
        else:
            x = (window.winfo_screenwidth() // 2) - (width //2)
            y = (window.winfo_screenheight() // 2) - (height //2)
        geostring = "{}x{}+{}+{}".format(width,height,x,y)
        if geostring_only:
            return geostring
        if place==True:
            window.geometry(geostring)
        else:
            window.geometry(geostring)
class LtEditor:
    #---event methods---
    def __init__(self, master,*args, **kwargs):
        # init is not actually where the main portion of the gui inits, main_init is
        self.tk = master # actual tkinter instance
        self.tk.withdraw() # hide the legitmate tkinter instance
        self.master = tk.Toplevel() # create our actual window
        self.master.withdraw() # hide the window temporarily
        self.file_type = None # default file type
        self.logic_tree = None # logic tree
        self.file_path = None # saved/opened file path
        self.unsavedChanges = False # keep track of unsaved changes
        self.jf = None # job file class
        self.config_path = "config.ini"
        #self.master.resizable(False,False)

        # all config file configurable settings
        #config list
        self.config_list = jobh.configList()
        #default path setting
        self.default_path_obj = jobh.configItem("default_path","core")
        self.config_list.add(self.default_path_obj)
        #view setting
        self.view_obj = jobh.configItem("view","preferences")
        self.view_obj.value = tk.StringVar() # viewmode (mode to display logictree object in): xml, Simplified
        self.config_list.add(self.view_obj)

        # read config file
        self.readConfigFile()

        #check for image files
        try: # check for icon
            f = open("icon.ico")
            f.close()
            self.icon=r"icon.ico"
        except:
            self.icon=resource_path(r"icon.ico")
        try:
            f = open(r"logo.png")
            f.close()
            self.logo=r"logo.png"
        except:
            self.logo=resource_path(r"logo.png")

        self.master.iconbitmap(self.icon)
        self.startMenu() # run the start menu, get the file type
    def __del__(self,wclosed=False):
        if wclosed==True:
            self.tk.quit()
            self.tk.destroy()
        else:
            try:
                if self.master is not None:
                    self.master.destroy()
            except:
                pass
    def __repr__(self):
        pass

    #---core functions---
    def startMenu(self):
        #top
        top = tk.Toplevel(self.tk)
        top.resizable(False,False)
        top.iconbitmap(self.icon)
        top.title("OQInputFiles - Select a file type")
        width = 325
        height = 300
        x = (top.winfo_screenwidth() // 2) - (width //2)
        y = (top.winfo_screenheight() // 2) - (height //2)
        top.geometry("{}x{}+{}+{}".format(width,height,x,y))

        # delete self on toplevel window close
        top.protocol("WM_DELETE_WINDOW", top.quit)
        #logo
        logoFile=ImageTk.PhotoImage(file=self.logo)
        logo = tk.Label(top,image=logoFile)
        logo.image=logoFile
        logo.pack()
        #button function
        def buttonClick(mode="smlt"):
            self.file_type=mode
            top.destroy()
            if self.file_type=="job.ini":
                self.job_main()
            else:
                self.main()
        #smlt button
        smltButton = tk.Button(
            top,
            width=30,
            height=2,
            pady=10,
            text="Source Model Logic Tree",
            command=lambda: buttonClick(mode="Source Model Logic Tree") # button for the source model logic tree file_type
        ).pack()
        #gmpe button
        gmpeButton = tk.Button(
            top,
            width=30,
            height=2,
            pady=10,
            text="GMPE",
            command=lambda: buttonClick(mode="GMPE") # button for the gmpe file_type
        ).pack()
        #job.ini button
        jobButton = tk.Button(
            top,
            width=30,
            height=2,
            pady=10,
            text="Job.ini",
            command=lambda: buttonClick(mode="job.ini")
        ).pack() #creates the startmenu. when done with the startmenu, it runs main.
    def placeInCenter(self,width,height,window=None,place=True,xpos=None,ypos=None,geostring_only=False): #fixes x,y placement of window
        if window is None:
            window=self.master
        if xpos is not None and ypos is not None:
            x = xpos - (width //2)
            y = ypos - (height //2)
        else:
            x = (window.winfo_screenwidth() // 2) - (width //2)
            y = (window.winfo_screenheight() // 2) - (height //2)
        geostring = "{}x{}+{}+{}".format(width,height,x,y)
        if geostring_only:
            return geostring
        if place==True:
            window.geometry(geostring)
        else:
            window.geometry(geostring)
    def pToOutput(self,text): # print to output
        if self.outputArea == None:
            return False
        elif isinstance(self.outputArea, tk.Frame):
            return False
        self.outputArea.configure(state=tk.NORMAL)
        self.outputArea.delete(1.0, "end")
        self.outputArea.insert("end", text)
        self.outputArea.configure(state=tk.DISABLED)
    def outputLogicTree(self,ltobj=None,file_type=None,viewmode=None): # displays the logic tree in either the xml or simplfiied format
        if ltobj==None:
            ltobj=self.logic_tree
        if file_type==None:
            file_type=self.file_type
        if viewmode == None:
            viewmode = self.view_obj.value.get()
        try:
            self.Canvas.destroy()
        except:
            pass
        try:
            self.scrollbar.destroy()
        except:
            pass
        try:
            self.container.destroy()
        except:
            pass
        try:
            self.outputArea.destroy()
        except:
            pass
        try:
            self.outputScroll.destroy()
        except:
            pass
        try:
            self.blankspace.destroy()
        except:
            pass

        if viewmode == "Simplified":
            self.container = container = tk.Frame(self.master)

            self.Canvas = tk.Canvas(container)
            self.outputArea = ttk.Frame(self.Canvas)
            self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.Canvas.yview)
            self.Canvas.create_window((0, 0), window=self.outputArea, anchor="nw")
            self.Canvas.configure(yscrollcommand=self.scrollbar.set)
            self.outputArea.bind("<Configure>",lambda e: self.Canvas.configure(scrollregion=self.Canvas.bbox("all")))
            self.Canvas.pack(side=tk.TOP,fill="both",expand=1,anchor=tk.NW)
            self.scrollbar.pack(side=tk.RIGHT,fill="y")
            container.pack(fill="both",expand=1,padx=5)

            for a,b in ltobj.blList.copy().items():
                bl = ViewObject(self.outputArea,ObjectType.BL,b,self.file_type,self)
                for k,l in b.branchSetList.copy().items():
                    bs = ViewObject(self.outputArea,ObjectType.BS,l,self.file_type,self,parent=bl)
                    for x,z in l.branchList.copy().items():
                        br = ViewObject(self.outputArea,ObjectType.BR,z,self.file_type,self,parent=bs)
            #blank space for righclick add branchlevel
            def do_popup(event):
                try:
                    self.xpos2 = event.x_root
                    self.ypos2 = event.y_root
                    popup = m.tk_popup(event.x_root, event.y_root)
                finally:
                    m.grab_release()

            m = tk.Menu(container,tearoff=0)
            def addf():
                self.ltviewobject.xpos = self.xpos2
                self.ltviewobject.ypos = self.ypos2
                self.ltviewobject.addW()
            m.add_command(label="Add BranchingLevel",command=addf)
            #self.blankspace = tk.Frame(self.outputArea)
            #self.blankspace.pack(fill="both",expand="yes")
            #self.blankspace.bind("<Button-3>", do_popup)
        elif viewmode == "XML":
            self.outputArea = tk.Text(
                self.master,
                bg="#e6e6e6",
                state=tk.DISABLED
            )
            self.outputScroll = tk.Scrollbar(self.master, command=self.outputArea.yview)
            self.outputArea.configure(yscrollcommand=self.outputScroll.set)
            self.outputArea.pack(side=tk.LEFT, fill=tk.BOTH,expand=True)
            self.outputScroll.pack(side=tk.RIGHT,fill=tk.Y)
            str = ltc.createXML(ltobj)
            self.pToOutput(str)
    def createPopup(self,wtype="message",wtitle="Popup",wdescription="Description",okfunc=None,yfunc=None,nfunc=None,oktext="Ok",ytext="Yes",ntext="No",xpos=None,ypos=None,nodestroy=False): # creates a popup
        #two types: message and yn
        top = tk.Toplevel(self.master)
        top.resizable(False,False)
        top.title(wtitle)
        self.placeInCenter(300,85,window=top,xpos=xpos,ypos=ypos)
        frame = tk.Frame(top)
        frame.pack(side=tk.TOP)
        bframe = tk.Frame(top)
        bframe.pack()

        desc = tk.Label(frame,text=wdescription)
        desc.configure(height=3)
        desc.pack()

        if wtype == "yn":
            ybutton = tk.Button(bframe,text=ytext,width=(len(ytext)*3))
            nbutton = tk.Button(bframe,text=ntext,width=(len(ytext)*3))
            ybutton.pack(side=tk.LEFT)
            nbutton.pack(side=tk.LEFT)
            if yfunc is None:
                def yfunc():
                    if nodestroy is False:
                        top.destroy()
                ybutton.configure(command=yfunc)
            else:
                def yfunc2():
                    yfunc()
                    if nodestroy is False:
                        top.destroy()
                ybutton.configure(command=yfunc2)
            if nfunc is None:
                def nfunc():
                    if nodestroy is False:
                        top.destroy()
                nbutton.configure(command=nfunc)
            else:
                def nfunc2():
                    nfunc()
                    if nodestroy is False:
                        top.destroy()
                nbutton.configure(command=nfunc2)
        else:
            button = tk.Button(frame,text=oktext,width=(len(oktext)*3))
            button.pack()
            if okfunc is None:
                def okfunc():
                    if nodestroy is False:
                        top.destroy()
                button.configure(command=okfunc)
            else:
                def okfunc2():
                    okfunc()
                    if nodestroy is False:
                        top.destroy()
                button.configure(command=okfunc2)
    def newLt(self,file_type=None): # deletes old logictree and creates a new one
        if self.logic_tree is not None:
            newLogTre=ltc.logicTreeC(file_type=self.logic_tree.file_type)
        else:
            if file_type == "Source Model Logic Tree":
                newLogTre=ltc.logicTreeC(file_type="SMLT")
            elif file_type == "GMPE":
                newLogTre=ltc.logicTreeC(file_type="GMPE")
        self.logic_tree = newLogTre
        self.file_path=None
        self.updateWindowTitle()
        self.outputLogicTree(viewmode=self.view_obj.value.get())
        return self.logic_tree
    def updateWindowTitle(self,unsaved=True): # updates the window title
        if unsaved==True:
            if self.file_path == None:
                self.master.title("OQInputFiles - "+self.file_type+" - *")
            else:
                self.master.title("OQInputFiles - "+self.file_type+" - "+self.file_path+"*")
        else:
            if self.file_path == None:
                self.master.title("OQInputFiles - "+self.file_type)
            else:
                self.master.title("OQInputFiles - "+self.file_type+" - "+self.file_path)
    def readConfigFile(self): # fetches the config value for the key given
        parser = configparser.ConfigParser()
        try:
            parser.read(self.config_path)
        except:
            print("No config.ini file, creating one...")
            self.updateConfigFile(newFile=True)
            return 'No config.ini file'
        for section in parser.sections():
            for i,v in parser.items(section):
                item = self.config_list.get(i,section)
                if isinstance(item.value,str):
                    item.set("value",v)
                elif isinstance(item.value,tk.StringVar):
                    item.value.set(v)
    def updateConfigFile(self): # loops through given dict, updating the config fike
        file = open(self.config_path,"w")
        parser = configparser.ConfigParser()
        for section in self.config_list.getSections():
            parser.add_section(section)
        for item in self.config_list.list:
            if isinstance(item.value,str) or isinstance(item.value,int):
                parser.set(item.section,item.key,item.value)
            elif isinstance(item.value,tk.StringVar):
                parser.set(item.section,item.key,item.value.get())

        parser.write(file)
        file.close()
    def getBlIdOptions(self, parent, noneCommand=None,checkBsExistence=False):
        blIdOptions = [] # list to hold all branchinglevel ids
        exists = False
        for i,v in self.logic_tree.blList.copy().items(): # loop through the branchlist and add ids as options to blIdOptions
            if len(v.branchSetList) > 0:
                exists = True # also check for a branch set
            blIdOptions.append(v.blId)
        if checkBsExistence == True:
            return exists
        else:
            if len(blIdOptions) > 0:
                return blIdOptions
            else:
                if noneCommand is not None:
                    noneCommand()
                return False
    def getBsIdOptions(self, parent, noneCommand=None,checkBExistence=False, type="external"):
        Options = [] # list to hold all branchinglevel ids
        exists = False
        for i,v in parent.branchSetList.copy().items(): # loop through the branchlist and add ids as options to blIdOptions
            if len(v.branchList) > 0:
                exists = True # also check for a branch set
            if type == "external":
                Options.append(v.realBsId)
            else:
                Options.append(v.bsId)
        if checkBExistence == True:
            return exists
        else:
            if len(Options) > 0:
                return Options
            else:
                if noneCommand is not None:
                    noneCommand()
                return False
    def getBIdOptions(self, parent, noneCommand=None, type="external"):
        Options = [] # list to hold all branchinglevel ids
        for i,v in parent.branchList.copy().items(): # loop through the branchlist and add ids as options to blIdOptions
            if type == "external":
                Options.append(v.realBId)
            else:
                Options.append(v.bId)
        if len(Options) > 0:
            return Options
        else:
            if noneCommand is not None:
                noneCommand()
            return False
    #---bound functions---
    # file dropdown
    def newFile(self,file_type=None): # creates a new file
        self.createPopup(wtype="yn",wtitle="New",wdescription="Are you sure you want to create a new file?\nYou will lose all unsaved data.",yfunc=self.newLt)
    def openFile(self,file_type=None): # opens file prompt then imports file
        try:
            tempfilepath = filedialog.askopenfilename(initialdir = self.default_path_obj.value,title = "Select file",filetypes = (("XML files","*.xml"),("all files","*.*")))
            if tempfilepath is not "":
                self.file_path = tempfilepath
            else:
                return "User canceled save"
        except:
            return "User canceled save"

        self.default_path_obj.value = str(Path(self.file_path).parent) # set default path

        if file_type==None:
            file_type = self.file_type

        templt = ltc.parseXML(self.file_path,file_type=file_type)
        if type(templt).__name__ == "str":
            return templt
        else:
            if self.logic_tree is not None:
                del self.logic_tree
            self.logic_tree = templt
        self.master.title("ltEditor - "+self.file_type+" - "+self.file_path)
        self.outputLogicTree()
    def saveFile(self,file_type=None,newFile=None): # saves a file to a specified location given in a prompt
        file = None
        openParam = ""
        if newFile is None:
            if self.file_path is None:
                newFile=True
            else:
                newFile=False
        if newFile == True:
            try:
                tempfilepath = filedialog.asksaveasfilename(initialdir = self.default_path_obj.value,title = "Select file",defaultextension=".xml",filetypes = (("XML file","*.xml"), ("all files","*.*")))
                if tempfilepath == "":
                    return "User canceled save"
                else:
                    self.file_path = tempfilepath
            except FileNotFoundError:
                return "User canceled save"
            openParam = "x"
        else:
            openParam = "w"

        self.default_path_obj.value = str(Path(self.file_path).parent) # set default path

        try:
            try:
                file = open(self.file_path,openParam)
            except FileNotFoundError:
                return "User canceled save"
        except FileExistsError:
            os.remove(self.file_path)
            try:
                file = open(self.file_path,openParam)
            except FileNotFoundError:
                return "User canceled save"
        file.truncate(0)
        strLt = ltc.createXML(self.logic_tree)
        file.write(strLt)
        file.close()
        file = open(self.file_path,"r")
        if file.read() == strLt:
            self.createPopup(wtitle="Saved Successfully",wdescription="The file has been saved successfully.")
            self.unsavedChanges=False
            self.master.title("ltEditor - "+self.file_type+" - "+self.file_path)
        else:
            self.createPopup(wtitle="Save unsuccesful",wdescription="The file has not been saved. Try again?",yfunc=saveFile)
        file.close()
    def saveAsFile(self,file_type=None): # always opens path prompt when saving
        self.saveFile(newFile=True)
    def exitButton(self): # exits program to desktop
        if self.unsavedChanges == True:
            self.createPopup(wtype="yn",wtitle="Quit to Main Menu?",wdescription="Are you sure you want to quit?\nAll unsaved data will be lost.",yfunc=self.master.quit)
        else:
            self.master.quit()
    def exitToMainMenuButton(self): # exits program to main menu
        if self.unsavedChanges == True:
            self.createPopup(wtype="yn",wtitle="Quit to Main Menu?",wdescription="Are you sure you want to quit to Main Menu?\nAll unsaved data will be lost.",yfunc=lambda: switchFileTypes(self))
        else:
            switchFileTypes(self)

    # Add Dropdown
    def addBlBs(self,file_type=None,blId="def",bsId="def",uncertaintyType="default",applyToTectonicRegionType="default"): # adds both a branchinglevel and branchset in one window
        if file_type is None:
            file_type = self.file_type
        self.windowOptions={}
        #new window
        top = tk.Toplevel(self.master)
        top.resizable(False,False)
        top.iconbitmap(self.icon)
        self.windowOptions["top"]=top
        top.title("Add BranchingLevel and BranchSet")
        width=400
        height=200
        self.placeInCenter(width,height,window=top)
        #declarations
        self.windowOptions["blId"] = blId
        self.windowOptions["bsId"] = bsId
        self.windowOptions["uncertaintyType"] = uncertaintyType
        self.windowOptions["applyToTectonicRegionType"] = applyToTectonicRegionType
        self.windowOptions["bsIdLabel"]=None
        self.windowOptions["bsIdBox"]=None
        self.windowOptions["blIdLabel"]=None
        self.windowOptions["blIdBox"]=None
        self.windowOptions["autoBlId"]=tk.IntVar()
        self.windowOptions["autoBsId"]=tk.IntVar()
        self.windowOptions["autoUncertaintyType"]=tk.IntVar()
        self.windowOptions["autoUncertaintyTypeBox"] = None
        self.windowOptions["autoUncertaintyTypeLabel"] = None
        self.windowOptions["aTTRBox"]=None
        self.windowOptions["aTTRLabel"] = None
        #autoblid
        def autoBlIdF():
            opt = self.windowOptions["autoBlId"]
            if opt.get() == 0:
                # uncheck
                if self.windowOptions["blIdLabel"] is not None:
                    self.windowOptions["blIdLabel"].destroy()
                if self.windowOptions["blIdBox"] is not None:
                    self.windowOptions["blIdBox"].destroy()
                opt.set(1)
            elif opt.get() == 1:
                # check
                self.windowOptions["blIdLabel"] = tk.Label(top,text="BlId:")
                self.windowOptions["blIdLabel"].grid(row=1,column=0)
                self.windowOptions["blIdBox"] = tk.Entry(top)
                self.windowOptions["blIdBox"].grid(row=1,column=1)
                opt.set(0)
        autoBlIdBox = tk.Checkbutton(top,text="Automatically Assign BlId",command=autoBlIdF)
        autoBlIdBox.deselect()
        autoBlIdBox.invoke()
        autoBlIdBox.grid(padx=20)

        #autobsid
        def autoBsIdF():
            opt = self.windowOptions["autoBsId"]
            if opt.get() == 0:
                # uncheck
                if self.windowOptions["bsIdLabel"] is not None:
                    self.windowOptions["bsIdLabel"].destroy()
                if self.windowOptions["bsIdBox"] is not None:
                    self.windowOptions["bsIdBox"].destroy()
                opt.set(1)
            elif opt.get() == 1:
                # check
                self.windowOptions["bsIdLabel"] = tk.Label(top,text="BsId:")
                self.windowOptions["bsIdLabel"].grid(row=2,column=0)
                self.windowOptions["bsIdBox"] = tk.Entry(top)
                self.windowOptions["bsIdBox"].grid(row=2,column=1)
                opt.set(0)
        autoBsIdBox = tk.Checkbutton(top,text="Automatically Assign BsId",command=autoBsIdF)
        autoBsIdBox.deselect()
        autoBsIdBox.invoke()
        autoBsIdBox.grid(row=0,column=1,padx=20)

        #auto uncertaintyType
        def autoUncertaintyTypeF():
            opt = self.windowOptions["autoUncertaintyType"]
            if opt.get() == 0:
                # uncheck
                if self.windowOptions["autoUncertaintyTypeLabel"] is not None:
                    self.windowOptions["autoUncertaintyTypeLabel"].destroy()
                if self.windowOptions["autoUncertaintyTypeBox"] is not None:
                    self.windowOptions["autoUncertaintyTypeBox"].destroy()
                top.geometry("")
                opt.set(1)
            elif opt.get() == 1:
                # check
                self.windowOptions["autoUncertaintyTypeLabel"] = tk.Label(top,text="uncertaintyType:")
                self.windowOptions["autoUncertaintyTypeLabel"].grid(row=4,column=0)
                self.windowOptions["autoUncertaintyTypeBox"] = tk.Entry(top)
                self.windowOptions["autoUncertaintyTypeBox"].grid(row=4,column=1)
                top.geometry("")
                opt.set(0)
        autoUncertaintyTypeCheck = tk.Checkbutton(top,text="Default uncertaintyType",command=autoUncertaintyTypeF)
        autoUncertaintyTypeCheck.deselect()
        autoUncertaintyTypeCheck.invoke()
        autoUncertaintyTypeCheck.grid(row=3,column=0,columnspan=2,padx=20)
        #applyToTectonicRegion
        if file_type=="GMPE":
            self.windowOptions["aTTRLabel"] = tk.Label(top,text="applyToTectonicRegionType:")
            self.windowOptions["aTTRLabel"].grid(row=5,column=0,columnspan=2)
            self.windowOptions["aTTRBox"] = tk.Entry(top,width=58)
            self.windowOptions["aTTRBox"].grid(row=6,column=0,columnspan=2)
            top.geometry("")

        # submit
        def addButtonF():
            if self.windowOptions["autoBlId"].get() == 0:
                if self.windowOptions["blIdBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid branchingLevelId")
                    return 'No branchingLevelId'
                self.windowOptions["blId"]=self.windowOptions["blIdBox"].get()
            if self.windowOptions["autoBsId"].get() == 0:
                if self.windowOptions["bsIdBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid branchSetId")
                    return 'No branchSetId'
                self.windowOptions["bsId"]=self.windowOptions["bsIdBox"].get()
            if self.windowOptions["autoUncertaintyType"].get() == 0:
                if self.windowOptions["autoUncertaintyTypeBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid uncertaintyType")
                    return 'No uncertaintyType'
                self.windowOptions["uncertaintyType"]=self.windowOptions["autoUncertaintyTypeBox"].get()
            if file_type == "GMPE":
                if self.windowOptions["aTTRBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid applyToTectonicRegionType")
                    return 'No applyToTectonicRegionType'
                self.windowOptions["applyToTectonicRegionType"]=self.windowOptions["aTTRBox"].get()
            tempBl = self.logic_tree.addBranchingLevel(blId=self.windowOptions["blId"])
            tempBlId = tempBl.blId
            tempBs = self.logic_tree.getBranchingLevel(tempBlId).addBranchSet(realBsId=self.windowOptions["bsId"],uncertaintyType=self.windowOptions["uncertaintyType"],applyToTectonicRegionType=self.windowOptions["applyToTectonicRegionType"])
            self.outputLogicTree(viewmode=self.view_obj.value.get())
            self.windowOptions["top"].destroy()
            self.unsavedChanges=True
            self.updateWindowTitle()


        addButton = tk.Button(top,text="Add",command=addButtonF,width=9)
        addButton.grid(row=7,column=0,columnspan=2,pady=5)

        #configurations
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)
        top.grid_columnconfigure(2, weight=1) # add branching level and branchset
    def addBl(self,file_type=None,blId="def"): # creates window and adds branchinglevel
        #declarations
        if file_type is None:
            file_type = self.file_type
        self.windowOptions={}
        self.windowOptions["blId"] = blId
        self.windowOptions["blIdLabel"]=None
        self.windowOptions["blIdBox"]=None
        self.windowOptions["autoBlId"]=tk.IntVar()
        self.windowOptions["autoBlId"].set(0)
        #top
        top = tk.Toplevel(self.master)
        top.resizable(False,False)
        self.windowOptions["top"]=top
        top.title("Add BranchingLevel")
        top.iconbitmap(self.icon)
        width=200
        height=100
        self.placeInCenter(width,height,window=top)
        #autobl
        def autoBlIdF():
            opt = self.windowOptions["autoBlId"]
            if opt.get() == 0:
                # uncheck
                if self.windowOptions["blIdLabel"] is not None:
                    self.windowOptions["blIdLabel"].destroy()
                if self.windowOptions["blIdBox"] is not None:
                    self.windowOptions["blIdBox"].destroy()
                opt.set(1)
            elif opt.get() == 1:
                # check
                self.windowOptions["blIdLabel"] = tk.Label(top,text="BlId:")
                self.windowOptions["blIdLabel"].grid(row=1,column=0)
                self.windowOptions["blIdBox"] = tk.Entry(top)
                self.windowOptions["blIdBox"].grid(row=1,column=1)
                opt.set(0)
        autoBlIdBox = tk.Checkbutton(top,text="Automatically Assign BlId",command=autoBlIdF)
        autoBlIdBox.deselect()
        autoBlIdBox.invoke()
        autoBlIdBox.grid(padx=20,columnspan=2)
        top.geometry("")
        #add button
        def addButtonF():
            if self.windowOptions["autoBlId"].get() == 0:
                if self.windowOptions["blIdBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid branchingLevelId")
                    return 'No branchingLevelId'
                self.windowOptions["blId"]=self.windowOptions["blIdBox"].get()
            tempBl = self.logic_tree.addBranchingLevel(blId=self.windowOptions["blId"])
            self.outputLogicTree(viewmode=self.view_obj.value.get())
            self.windowOptions["top"].destroy()
            self.updateWindowTitle()
            self.unsavedChanges=True
        addButton = tk.Button(top,text="Add",command=addButtonF,width=9)
        addButton.grid(row=7,column=0,columnspan=2,pady=5)


        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)
        top.grid_columnconfigure(2, weight=1) # add branchinglevel
    def addBs(self,bsId="def",uncertaintyType="default",applyToTectonicRegionType="default"): # creates a window and adds a branchset
        self.windowOptions = {}
        if len(self.logic_tree.blList) < 1:
            self.createPopup(wtitle="No branchLevel exists",wdescription="No branchLevel exists\nCreate one now?",wtype="yn",yfunc=self.addBl)
            print("No branchLevel, try again.")
            return("No branchLevel, try again.")
        top = tk.Toplevel(self.master)
        top.resizable(False,False)
        top.title("Add branchSet")
        top.iconbitmap(self.icon)
        width=300
        height=150
        self.placeInCenter(width,height,window=top)
        self.windowOptions["top"]=top
        self.windowOptions["blId"]=None
        self.windowOptions["blIdLabel"]=None
        self.windowOptions["blIdBox"]=None
        self.windowOptions["bsId"]=bsId
        self.windowOptions["bsIdLabel"]=None
        self.windowOptions["bsIdBox"]=None
        self.windowOptions["autoBsId"] =tk.IntVar()
        self.windowOptions["UncertaintyType"]=uncertaintyType
        self.windowOptions["autoUncertaintyType"]=tk.IntVar()
        self.windowOptions["autoUncertaintyTypeBox"] = None
        self.windowOptions["autoUncertaintyTypeLabel"] = None
        self.windowOptions["applyToTectonicRegionType"] = applyToTectonicRegionType
        self.windowOptions["aTTRBox"]=None
        self.windowOptions["aTTRLabel"] = None

        def autoBsIdF():
            opt = self.windowOptions["autoBsId"]
            if opt.get() == 0:
                # uncheck
                if self.windowOptions["bsIdLabel"] is not None:
                    self.windowOptions["bsIdLabel"].destroy()
                if self.windowOptions["bsIdBox"] is not None:
                    self.windowOptions["bsIdBox"].destroy()
                opt.set(1)
            elif opt.get() == 1:
                # check
                self.windowOptions["bsIdLabel"] = tk.Label(top,text="BsId:")
                self.windowOptions["bsIdLabel"].grid(row=2,column=0)
                self.windowOptions["bsIdBox"] = tk.Entry(top)
                self.windowOptions["bsIdBox"].grid(row=2,column=1)

                opt.set(0)
        autoBsIdBox = tk.Checkbutton(top,text="Automatically Assign BsId",command=autoBsIdF)
        autoBsIdBox.deselect()
        autoBsIdBox.invoke()
        autoBsIdBox.grid(row=0,column=0)

        #auto uncertaintyType
        def autoUncertaintyTypeF():
            opt = self.windowOptions["autoUncertaintyType"]
            if opt.get() == 0:
                # uncheck
                if self.windowOptions["autoUncertaintyTypeLabel"] is not None:
                    self.windowOptions["autoUncertaintyTypeLabel"].destroy()
                if self.windowOptions["autoUncertaintyTypeBox"] is not None:
                    self.windowOptions["autoUncertaintyTypeBox"].destroy()
                top.geometry("")
                opt.set(1)
            elif opt.get() == 1:
                # check
                self.windowOptions["autoUncertaintyTypeLabel"] = tk.Label(top,text="uncertaintyType:")
                self.windowOptions["autoUncertaintyTypeLabel"].grid(row=4,column=0)
                self.windowOptions["autoUncertaintyTypeBox"] = tk.Entry(top)
                self.windowOptions["autoUncertaintyTypeBox"].grid(row=4,column=1)
                top.geometry("")
                opt.set(0)
        autoUncertaintyTypeCheck = tk.Checkbutton(top,text="Default uncertaintyType",command=autoUncertaintyTypeF)
        autoUncertaintyTypeCheck.deselect()
        autoUncertaintyTypeCheck.invoke()
        autoUncertaintyTypeCheck.grid(row=0,column=1)
        #applyToTectonicRegion
        if self.file_type=="GMPE":
            self.windowOptions["aTTRLabel"] = tk.Label(top,text="applyToTectonicRegionType:")
            self.windowOptions["aTTRLabel"].grid(row=6,column=0,columnspan=2)
            self.windowOptions["aTTRBox"] = tk.Entry(top,width=58)
            self.windowOptions["aTTRBox"].grid(row=7,column=0,columnspan=2)
            top.geometry("")

        self.windowOptions["blIdLabel"] = tk.Label(top,text="branchLevel blId:")
        self.windowOptions["blIdLabel"].grid(row=5,column=0)
        self.windowOptions["blIdClicked"] = tk.StringVar()
        self.windowOptions["blIdClicked"].set("Select from list")
        blIdOptions = []
        for i,v in self.logic_tree.blList.copy().items():
            blIdOptions.append(v.blId)
        self.windowOptions["blIdBox"] = tk.OptionMenu(top, self.windowOptions["blIdClicked"],*blIdOptions)
        self.windowOptions["blIdBox"].grid(row=5,column=1)

        def addButtonF():
            if self.windowOptions["autoBsId"].get() == 0:
                if self.windowOptions["bsIdBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid branchSetId")
                    return 'No branchSetId'
                self.windowOptions["bsId"]=self.windowOptions["bsIdBox"].get()
            if self.windowOptions["autoUncertaintyType"].get() == 0:
                if self.windowOptions["autoUncertaintyTypeBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid uncertaintyType")
                    return 'No uncertaintyType'
                self.windowOptions["uncertaintyType"]=self.windowOptions["autoUncertaintyTypeBox"].get()
            if self.file_type == "GMPE":
                if self.windowOptions["aTTRBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid applyToTectonicRegionType")
                    return 'No applyToTectonicRegionType'
                self.windowOptions["applyToTectonicRegionType"]=self.windowOptions["aTTRBox"].get()
            tempbl = self.logic_tree.getBranchingLevel(self.windowOptions["blIdClicked"].get())
            if tempbl is not "Error":
                tempbl.addBranchSet(realBsId=self.windowOptions["bsId"],uncertaintyType=self.windowOptions["UncertaintyType"],applyToTectonicRegionType=self.windowOptions["applyToTectonicRegionType"])
                self.outputLogicTree(viewmode=self.view_obj.value.get())
                self.windowOptions["top"].destroy()
                self.updateWindowTitle()
                self.unsavedChanges=True
            else:
                self.createPopup(wtitle="Error",wdescription=("Please select a valid branchingLevelId"))


        addButton = tk.Button(top,text="Add",command=addButtonF,width=9)
        addButton.grid(row=8,column=0,columnspan=2,pady=5)

        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)
        top.grid_columnconfigure(2, weight=1) # add branchset
    def addBr(self,bId="def",uncertaintyModel=None,uncertaintyWeight=None,gmpeTable=None):
        self.windowOptions={}

        #checks
        if len(self.logic_tree.blList) < 1:
            self.createPopup(wtitle="No branchLevel exists",wdescription="No branchLevel exists\nCreate one now?",wtype="yn",yfunc=self.addBl)
            print("No branchLevel, try again.")
            return("No branchLevel, try again.")
        branchExists=False
        for i,v in self.logic_tree.blList.copy().items():
            if len(v.branchSetList) > 0:
                branchExists = True
        if branchExists == False:
            self.createPopup(wtitle="No branchSet exists",wdescription="No branchSet exists\nCreate one now?",wtype="yn",yfunc=self.addBs)
            print("No branchSet, try again.")
            return("No branchSet, try again.")
        #top
        top = tk.Toplevel(self.master)
        top.resizable(False,False)
        top.title("Add branch")
        top.iconbitmap(self.icon)
        self.placeInCenter(350,200,window=top)
        #blid
        def blIdDropDownClicked(value):
            self.windowOptions["bsIdMenu"].destroy()
            if len(self.logic_tree.getBranchingLevel(self.windowOptions["blIdClicked"].get()).branchSetList) < 1:
                bsIdOptions = ["No branchSets"]
                self.windowOptions["bsIdClicked"] = tk.StringVar()
                self.windowOptions["bsIdClicked"].set("...")
                self.windowOptions["bsIdMenu"] = tk.OptionMenu(top, self.windowOptions["bsIdClicked"],*bsIdOptions)
                self.windowOptions["bsIdMenu"].grid(row=0,column=3)
                return "No branchSets"
            # create the actual bsid dropdown
            self.windowOptions["bsIdClicked"] = tk.StringVar()
            self.windowOptions["bsIdClicked"].set("...")
            bsIdOptions = []
            for i,v in self.logic_tree.getBranchingLevel(self.windowOptions["blIdClicked"].get()).branchSetList.copy().items():
                bsIdOptions.append(v.realBsId)
            self.windowOptions["bsIdMenu"] = tk.OptionMenu(top, self.windowOptions["bsIdClicked"],*bsIdOptions)
            self.windowOptions["bsIdMenu"].grid(row=0,column=3)
            top.geometry("")

        blIdLabel = tk.Label(top,text="blId:")
        blIdLabel.grid(row=0,column=0)

        self.windowOptions["blIdClicked"] = tk.StringVar()
        self.windowOptions["blIdClicked"].set("...")
        blIdOptions = []
        for i,v in self.logic_tree.blList.copy().items():
            blIdOptions.append(v.blId)
        self.windowOptions["blIdMenu"] = tk.OptionMenu(top, self.windowOptions["blIdClicked"],*blIdOptions,command=blIdDropDownClicked)
        self.windowOptions["blIdMenu"].grid(row=0,column=1)
        #bsid
        bsIdLabel = tk.Label(top,text="bsId:")
        bsIdLabel.grid(row=0,column=2)
        bsIdOptions = ["Select a branchLevel first"]
        self.windowOptions["bsIdClicked"] = tk.StringVar()
        self.windowOptions["bsIdClicked"].set("...")
        self.windowOptions["bsIdMenu"] = tk.OptionMenu(top, self.windowOptions["bsIdClicked"],*bsIdOptions)
        self.windowOptions["bsIdMenu"].grid(row=0,column=3)
        #uncertaintyWeight
        uWLabel = tk.Label(top,text="uncertaintyWeight:")
        uWLabel.grid(row=1,column=0,columnspan=2)
        self.windowOptions["uWBox"]=tk.Entry(top)
        self.windowOptions["uWBox"].grid(row=1,column=2,columnspan=2)

        #self.windowOptions["gmpeBox"]=None
        #self.windowOptions["uMBox"]=None
        #gmpetable and uncertaintyModel
        if self.file_type == "GMPE":
            gmpeLabel = tk.Label(top,text="gmpeTable:")
            gmpeLabel.grid(row=2,column=0,columnspan=4)
            self.windowOptions["gmpeBox"]=tk.Entry(top,width=50)
            self.windowOptions["gmpeBox"].grid(row=3,column=0,columnspan=4,pady=(0,5),padx=(5,5))
        elif self.file_type == "Source Model Logic Tree":
            uMLabel = tk.Label(top,text="uncertaintyModel:")
            uMLabel.grid(row=2,column=0,columnspan=4)
            self.windowOptions["uMBox"]=tk.Entry(top,width=50)
            self.windowOptions["uMBox"].grid(row=3,column=0,columnspan=4,pady=(0,5),padx=(5,5))


        self.windowOptions["bId"] = bId
        self.windowOptions["autoBId"] = tk.IntVar()
        self.windowOptions["bIdLabel"] = None
        self.windowOptions["bIdBox"] = None
        self.windowOptions["top"] = top

        def autoBIdF():
            opt = self.windowOptions["autoBId"]
            if opt.get() == 0:
                # uncheck
                if self.windowOptions["bIdLabel"] is not None:
                    self.windowOptions["bIdLabel"].destroy()
                if self.windowOptions["bIdBox"] is not None:
                    self.windowOptions["bIdBox"].destroy()
                opt.set(1)
            elif opt.get() == 1:
                # check
                self.windowOptions["bIdLabel"] = tk.Label(top,text="bId:")
                self.windowOptions["bIdLabel"].grid(row=5,column=0,columnspan=2)
                self.windowOptions["bIdBox"] = tk.Entry(top)
                self.windowOptions["bIdBox"].grid(row=5,column=2,columnspan=2)
                opt.set(0)
        autoBIdBox = tk.Checkbutton(top,text="Automatically Assign bId",command=autoBIdF)
        autoBIdBox.deselect()
        autoBIdBox.invoke()
        autoBIdBox.grid(row=4,column=0,columnspan=4,padx=20)

        def addButtonF():
            if self.windowOptions["blIdClicked"].get()=="...":
                self.createPopup(wtitle="Error",wdescription="Please choose a branchLevel id")
                return 'No branchLevel id'
            elif self.windowOptions["bsIdClicked"].get()=="Select a branchLevel first":
                self.createPopup(wtitle="Error",wdescription="Please choose a valid branchSet")
                return 'Invalid branchSet'
            elif self.windowOptions["bsIdClicked"].get()=="...":
                self.createPopup(wtitle="Error",wdescription="Please choose a branchSet id")
                return 'No branchSet id'
            else:
                tempbsid=self.windowOptions["bsIdClicked"].get()
                tempfound=False
                for i,v in self.logic_tree.getBranchingLevel(self.windowOptions["blIdClicked"].get()).branchSetList.copy().items():
                    if v.realBsId==tempbsid:
                        tempfound=True
                if tempfound == False:
                    self.createPopup(wtitle="Error",wdescription="Please choose a valid branchSet")
                    return 'Invalid branchSet'
            if self.windowOptions["uWBox"].get() == "":
                self.createPopup(wtitle="Error",wdescription="Please enter a valid uncertaintyWeight value")
                return 'No uncertaintyWeight'

            if self.windowOptions["autoBId"].get()==0:
                if self.windowOptions["bIdBox"].get() == "":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid bId value")
                    return 'No bId'
                self.windowOptions["bId"] = self.windowOptions["bIdBox"].get()

            if self.file_type == "GMPE":
                if self.windowOptions["gmpeBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid gmpeTable value")
                    return 'No gmpeTable'
                tempbl = self.logic_tree.getBranchingLevel(self.windowOptions["blIdClicked"].get())
                tempbs = tempbl.getBranchSet(realBsId=self.windowOptions["bsIdClicked"].get(),type="obj")
                tempbs.addBranch(bId=self.windowOptions["bId"],uncertaintyWeight=self.windowOptions["uWBox"].get(),GMPETable=self.windowOptions["gmpeBox"].get())
                self.outputLogicTree(viewmode=self.view_obj.value.get())
                self.unsavedChanges=True
                self.updateWindowTitle()
                self.windowOptions["top"].destroy()
            elif self.file_type == "Source Model Logic Tree":
                if self.windowOptions["uMBox"].get()=="":
                    self.createPopup(wtitle="Error",wdescription="Please enter a valid uncertaintyModel value")
                    return 'No uncertaintyModel'
                tempbl = self.logic_tree.getBranchingLevel(self.windowOptions["blIdClicked"].get())
                tempbs = tempbl.getBranchSet(realBsId=self.windowOptions["bsIdClicked"].get(),type="obj")
                tempbs.addBranch(bId=self.windowOptions["bId"],uncertaintyModel=self.windowOptions["uMBox"].get(),uncertaintyWeight=self.windowOptions["uWBox"].get())
                self.outputLogicTree(viewmode=self.view_obj.value.get())
                self.unsavedChanges=True
                self.updateWindowTitle()
                self.windowOptions["top"].destroy()


        addButton = tk.Button(top,text="Add",command=addButtonF,width=9)
        addButton.grid(row=9,column=0,columnspan=4,pady=(5,5))
        top.geometry("") # adds branch

    #Edit Dropdown
    def editBl(self): # creates prompt to edit a branchinglevel
        blIdOptions = self.getBlIdOptions(self.logic_tree)
        if blIdOptions == False: # check if there is even a branchlevel to edit
            self.createPopup(wtitle="No branchLevel exists",wdescription="No branchLevel exists\nCreate one now?",wtype="yn",yfunc=self.addBl)
            return "No branchingLevels"

        self.windowOptions={}
        self.windowOptions["tBlId"] = tk.StringVar()
        self.windowOptions["tBlIdDropdown"] = None
        self.windowOptions["newBlIdBox"] = None
        self.windowOptions["newBlId"] = tk.StringVar()

        #gui
        top = tk.Toplevel(self.master)
        top.title("Edit a branchingLevel")
        self.placeInCenter(300,99,window=top)
        top.resizable(False,False)
        top.iconbitmap(self.icon)
        #frames
        targetFrame = tk.Frame(top)
        targetFrame.pack()
        newBlIdFrame = tk.Frame(top)
        newBlIdFrame.pack()
        #targetFrame items
        tBlIdLabel = tk.Label(targetFrame,text="Select a branchLevel:")
        tBlIdLabel.pack(side=tk.LEFT, pady=3)
        self.windowOptions["tBlId"].set("...")
        self.windowOptions["tBlIdDropdown"] = tk.OptionMenu(targetFrame, self.windowOptions["tBlId"],*blIdOptions,command=lambda id:
            self.windowOptions["newBlId"].set(id)
        )
        self.windowOptions["tBlIdDropdown"].pack(side=tk.LEFT, pady=3)
        #newBlIdFrame items
        newBlIdLabel = tk.Label(newBlIdFrame,text="Edit blId: ")
        newBlIdLabel.pack(side=tk.LEFT, pady=3)
        self.windowOptions["newBlIdBox"] = tk.Entry(newBlIdFrame,textvariable=self.windowOptions["newBlId"])
        self.windowOptions["newBlIdBox"].pack(side=tk.LEFT, pady=3)
        # add button & function
        def addButtonF():
            bl = self.logic_tree.getBranchingLevel(self.windowOptions["tBlId"].get())
            newBlId = self.windowOptions["newBlIdBox"].get()
            try:
                if self.logic_tree.blList[newBlId]:
                    if bl.blId == newBlId:
                        top.destroy()
                        return 'No changes made'
                    else:
                        self.createPopup(wtitle="Error",wdescription="Different branchingLevel already uses that branchingLevelId")
            except:
                bl.blId = newBlId
                self.unsavedChanges=True
                self.updateWindowTitle()
                self.outputLogicTree()
                top.destroy()
        addButton = tk.Button(top,text="Edit",command=addButtonF,width=12)
        addButton.pack(pady=3)
    def editBs(self,file_type=None): # creates prompt to edit a branchSet
        #setup
        if file_type is None:
            file_type = self.file_type
        self.windowOptions={}
        blIdOptions = self.getBlIdOptions(self.logic_tree)
        bsIdOptions = ["Select a branchLevel first"] # list to hold all branchSet ids
        branchSetExists = self.getBlIdOptions(self.logic_tree,checkBsExistence=True)

        if blIdOptions == False: # check if there is even a branchlevel to edit
            self.createPopup(wtitle="No branchLevel exists",wdescription="No branchLevel exists\nCreate one now?",wtype="yn",yfunc=self.addBl)
            return "No branchingLevels"
        if branchSetExists == False:
            self.createPopup(wtitle="No branchSet exists",wdescription="No branchSet exists\nCreate one now?",wtype="yn",yfunc=self.addBs)
            return "No branchSet to edit"

        #gui
        self.windowOptions["top"] = tk.Toplevel(self.master)
        self.windowOptions["top"].title("Edit a branchSet")
        self.windowOptions["top"].resizable(False,False)
        self.windowOptions["top"].iconbitmap(self.icon)
        if file_type == "Source Model Logic Tree":
            self.placeInCenter(300,149,window=self.windowOptions["top"])
        else:
            self.placeInCenter(300,200,window=self.windowOptions["top"])

        # declarations
        self.windowOptions["dropdownFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["dropdownFrame"].pack()
        self.windowOptions["optionFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["optionFrame"].pack()

        self.windowOptions["blIdDropdown"] = None
        self.windowOptions["bsIdDropdown"] = None
        self.windowOptions["bsIdO"] = None
        self.windowOptions["uncertaintyTypeO"] = None
        self.windowOptions["attrO"] = None
        # dropdowns
        def createBsIdDropdown(blId): # bound to blIdDropdown
            if self.windowOptions["bsIdDropdown"] is not None:
                self.windowOptions["bsIdDropdown"].destroy()
            print(blId)
            bl = self.logic_tree.getBranchingLevel(blId)
            bsIdOptions = []
            for i,v in bl.branchSetList.copy().items():
                bsIdOptions.append(v.realBsId)
            self.windowOptions["bsIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=bsIdOptions,defaultval="...",framePackType=tk.LEFT,command=bsIdSelected)
        def bsIdSelected(bsId): # bound to bsIdDropdown
            bl = self.logic_tree.getBranchingLevel(self.windowOptions["blIdDropdown"].get())
            bs = bl.getBranchSet(realBsId=self.windowOptions["bsIdDropdown"].get(),type="obj")
            if self.windowOptions["bsIdO"] is not None:
                self.windowOptions["bsIdO"].set(bs.realBsId)
            if self.windowOptions["uncertaintyTypeO"] is not None:
                self.windowOptions["uncertaintyTypeO"].set(bs.uncertaintyType)
            if self.windowOptions["attrO"] is not None:
                self.windowOptions["attrO"].set(bs.applyToTectonicRegionType)
        self.windowOptions["blIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="blId:",options=blIdOptions,defaultval="...",command=createBsIdDropdown,framePackType=tk.LEFT)
        self.windowOptions["bsIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=bsIdOptions,defaultval="...",framePackType=tk.LEFT)
        # options
        self.windowOptions["bsIdO"] = wim.Entry(self.windowOptions["optionFrame"], label="bsId:")
        self.windowOptions["uncertaintyTypeO"] = wim.Entry(self.windowOptions["optionFrame"], label="uncertaintyType:",type=wim.windowObject.FULL_ENTRY)
        if file_type == "GMPE":
            self.windowOptions["attrO"] = wim.Entry(self.windowOptions["optionFrame"], label="applyToTectonicRegionType:",type=wim.windowObject.FULL_ENTRY)
        def submit():
            bl = self.logic_tree.getBranchingLevel(self.windowOptions["blIdDropdown"].get())
            bs = bl.getBranchSet(realBsId=self.windowOptions["bsIdDropdown"].get(),type="obj")
            bs.realBsId = self.windowOptions["bsIdO"].get()
            bs.uncertaintyType = self.windowOptions["uncertaintyTypeO"].get()
            if file_type == "GMPE":
                bs.applyToTectonicRegionType = self.windowOptions["attrO"].get()
            self.unsavedChanges=True
            self.updateWindowTitle()
            self.outputLogicTree()
            self.windowOptions["top"].destroy()
        addButton = wim.SubmitButton(self.windowOptions["top"],buttontext="Done",command=submit)
        self.windowOptions["top"].geometry("")
    def editBr(self): # creates prompt to edit a branch
        #setup
        self.windowOptions={}
        blIdOptions = self.getBlIdOptions(self.logic_tree) # list to hold all branchinglevel ids
        bsIdOptions = ["Select a branchLevel first"] # list to hold all branchSet ids
        bIdOptions = ["Select a branchSet first"]
        branchSetExists = self.getBlIdOptions(self.logic_tree,checkBsExistence=True) # variable to keep track of if a branchset exits
        branchExists = False # variable to keep track of if a branch exists
        for i,v in self.logic_tree.blList.copy().items(): # loop through the branchlist and add ids as options to blIdOptions
            if len(v.branchSetList) > 0:
                for x,k in v.branchSetList.copy().items():
                    if len(k.branchList) > 0:
                        branchExists = True
        if blIdOptions == False: # check if there is even a branchlevel to edit
            self.createPopup(wtitle="No branchLevel exists",wdescription="No branchLevel exists\nCreate one now?",wtype="yn",yfunc=self.addBl)
            return "No branchingLevels"
        if branchSetExists == False:
            self.createPopup(wtitle="No branchSet exists",wdescription="No branchSet exists\nCreate one now?",wtype="yn",yfunc=self.addBs)
            return "No branchSet to edit"
        if branchExists == False:
            self.createPopup(wtitle="No branch exists",wdescription="No branch exists\nCreate one now?",wtype="yn",yfunc=self.addBr)
            return "No branch to edit"

        #gui
        self.windowOptions["top"] = tk.Toplevel(self.master)
        self.windowOptions["top"].title("Edit a branch")
        self.windowOptions["top"].resizable(False,False)
        self.windowOptions["top"].iconbitmap(self.icon)
        if self.file_type == "Source Model Logic Tree":
            self.placeInCenter(300,171,window=self.windowOptions["top"])
        else:
            self.placeInCenter(300,200,window=self.windowOptions["top"])

        # declarations
        self.windowOptions["dropdownFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["dropdownFrame"].pack()
        self.windowOptions["optionFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["optionFrame"].pack()

        self.windowOptions["blIdDropdown"] = None
        self.windowOptions["bsIdDropdown"] = None
        self.windowOptions["bIdDropdown"] = None

        self.windowOptions["bIdO"] = None
        self.windowOptions["uncertaintyModelO"] = None
        self.windowOptions["gmpeO"] = None
        self.windowOptions["uncertaintyWeightO"] = None

        self.windowOptions["bl"] = None
        self.windowOptions["bs"] = None
        self.windowOptions["b"] = None

        #dropdowns
        def createBsIdDropdown(blId): # bound to blIdDropdown
            if self.windowOptions["bsIdDropdown"] is not None:
                self.windowOptions["bsIdDropdown"].destroy()
            self.windowOptions["bl"] = self.logic_tree.getBranchingLevel(blId)
            bsIdOptions = self.getBsIdOptions(self.windowOptions["bl"])
            self.windowOptions["bsIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=bsIdOptions,defaultval="...",framePackType=tk.LEFT,command=createBIdDropdown)
        def createBIdDropdown(realBsId): # bound to bsIdDropdown
            if self.windowOptions["bl"] is None:
                print('no BranchingLevel')
                return 'no BranchingLevel'
            self.windowOptions["bs"] = self.windowOptions["bl"].getBranchSet(realBsId=realBsId,type="obj")
            if self.windowOptions["bIdDropdown"] is not None:
                self.windowOptions["bIdDropdown"].destroy()
            bIdOptions = self.getBIdOptions(self.windowOptions["bs"])
            self.windowOptions["bIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bId:",options=bIdOptions,defaultval="...",framePackType=tk.RIGHT,command=bIdSelected)
        def bIdSelected(realbId): # bound to bIdDropdown
            self.windowOptions["b"] = self.windowOptions["bs"].getBranch(realBId=realbId,type="obj")
            self.windowOptions["bIdO"].set(realbId)
            if self.file_type == "Source Model Logic Tree":
                self.windowOptions["uncertaintyModelO"].set(self.windowOptions["b"].uncertaintyModel)
            elif self.file_type == "GMPE":
                self.windowOptions["gmpeO"].set(self.windowOptions["b"].GMPETable)
            self.windowOptions["uncertaintyWeightO"].set(self.windowOptions["b"].uncertaintyWeight)
        self.windowOptions["blIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="blId:",options=blIdOptions,defaultval="...",command=createBsIdDropdown,framePackType=tk.LEFT)
        self.windowOptions["bsIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=bsIdOptions,defaultval="...",framePackType=tk.LEFT)
        self.windowOptions["bIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bId:",options=bIdOptions,defaultval="...",framePackType=tk.RIGHT)

        #options
        self.windowOptions["bIdO"] = wim.Entry(self.windowOptions["optionFrame"],label="bId:")
        if self.file_type == "Source Model Logic Tree":
            self.windowOptions["uncertaintyModelO"] = wim.Entry(self.windowOptions["optionFrame"],label="uncertaintyModel:",type=wim.windowObject.FULL_ENTRY,entry_config={"width":"30"})
        elif self.file_type == "GMPE":
            self.windowOptions["gmpeO"] = wim.Entry(self.windowOptions["optionFrame"],label="gmpe_table:",type=wim.windowObject.FULL_ENTRY)
        self.windowOptions["uncertaintyWeightO"] = wim.Entry(self.windowOptions["optionFrame"],label="uncertaintyWeight:",type=wim.windowObject.FULL_ENTRY,entry_config={"width":"30"})

        #submit button
        def submit():
            self.windowOptions["b"].realBId = self.windowOptions["bIdO"].get()
            self.windowOptions["b"].uncertaintyWeight = self.windowOptions["uncertaintyWeightO"].get()
            if self.file_type == "GMPE":
                self.windowOptions["b"].GMPETable = self.windowOptions["gmpeO"].get()
            elif self.file_type == "Source Model Logic Tree":
                self.windowOptions["b"].uncertaintyModel = self.windowOptions["uncertaintyModelO"].get()
            self.outputLogicTree()
            self.unsavedChanges=True
            self.updateWindowTitle()
            self.windowOptions["top"].destroy()
        addButton = wim.SubmitButton(self.windowOptions["top"],buttontext="Save",command=submit)
        self.windowOptions["top"].geometry("")


    #Delete Dropdown
    def deleteBl(self,file_type=None): # creates prompt to delete a branchinglevel
        #setup
        self.windowOptions = {}
        blIdOptions = self.getBlIdOptions(self.logic_tree)
        if blIdOptions == False: # check if there is even a branchlevel to edit
            self.createPopup(wtitle="No branchingLevel",wdescription="No branchingLevel exists")
            return "No branchingLevels"
        #gui
        self.windowOptions["top"] = tk.Toplevel(self.master)
        self.windowOptions["top"].resizable(False,False)
        self.windowOptions["top"].iconbitmap(self.icon)
        self.placeInCenter(150,72,window=self.windowOptions["top"])
        self.windowOptions["top"].title("Delete")
        self.windowOptions["blIdO"] = wim.Dropdown(self.windowOptions["top"],label="blId:",options=blIdOptions,pady=3,defaultval="...")
        #submit
        def submit():
            if self.windowOptions["blIdO"].get() == "...":
                self.createPopup(wtitle="Wrong branchingLevelID",wdescription="Please select a different branchingLevelID")
                return "Invalid bl"
            bl = self.logic_tree.deleteBranchingLevel(self.windowOptions["blIdO"].get())
            self.unsavedChanges = True
            self.updateWindowTitle()
            self.windowOptions["top"].destroy()
            self.outputLogicTree()
        self.windowOptions["submitButton"] = wim.SubmitButton(self.windowOptions["top"],command=submit,button_config={"width":"12"},buttontext="Delete")
    def deleteBs(self,file_type=None): # creates prompt to delete a branchSet
        self.windowOptions = {}
        blIdOptions = self.getBlIdOptions(self.logic_tree)
        self.windowOptions["bsIdOptions"] = ["..."]
        bsExists = self.getBlIdOptions(self.logic_tree,checkBsExistence=True)
        if blIdOptions == False: # check if there is even a branchlevel to edit
            self.createPopup(wtitle="No branchingLevel",wdescription="No branchingLevel exists")
            return "No branchingLevels"
        if bsExists == False:
            self.createPopup(wtitle="No branchSet",wdescription="No branchSet exists")
            return "No branchSet"
        #gui
        self.windowOptions["top"] = tk.Toplevel(self.master)
        self.windowOptions["top"].resizable(False,False)
        self.windowOptions["top"].iconbitmap(self.icon)
        self.placeInCenter(300,72,window=self.windowOptions["top"])
        self.windowOptions["top"].title("Delete")
        self.windowOptions["dropdownFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["dropdownFrame"].pack()
        self.windowOptions["bsIdO"] = None
        def createBsIdDropdown(blId):
            self.windowOptions["bsIdOptions"] = self.getBsIdOptions(self.logic_tree.getBranchingLevel(blId))
            if self.windowOptions["bsIdO"] is not None:
                self.windowOptions["bsIdO"].destroy()
            self.windowOptions["bsIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=self.windowOptions["bsIdOptions"],pady=3,defaultval="...",framePackType=tk.LEFT)
        self.windowOptions["blIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="blId:",options=blIdOptions,pady=3,defaultval="...",command=createBsIdDropdown,framePackType=tk.LEFT)
        self.windowOptions["bsIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=self.windowOptions["bsIdOptions"],pady=3,defaultval="...",framePackType=tk.LEFT)
        #submit button
        def submit():
            if self.windowOptions["blIdO"].get() == "...":
                self.createPopup(wtitle="Wrong branchingLevelID",wdescription="Please select a different branchingLevelID")
                return "Invalid bl"
            if self.windowOptions["bsIdO"].get() == "...":
                self.createPopup(wtitle="Wrong branchSetID",wdescription="Please select a different branchSetID")
                return "Invalid bs"
            bl = self.logic_tree.getBranchingLevel(self.windowOptions["blIdO"].get())
            bl.deleteBranchSet(realBsId=self.windowOptions["bsIdO"].get())
            self.unsavedChanges = True
            self.updateWindowTitle()
            self.outputLogicTree()
            self.windowOptions["top"].destroy()
        self.windowOptions["submitButton"] = wim.SubmitButton(self.windowOptions["top"],command=submit,button_config={"width":"12"},buttontext="Delete")
    def deleteBr(self,file_type=None): # creates prompt to delete a branch
        self.windowOptions = {}
        blIdOptions = self.getBlIdOptions(self.logic_tree)
        self.windowOptions["bsIdOptions"] = ["..."]
        self.windowOptions["bIdOptions"] = ["..."]
        bsExists = self.getBlIdOptions(self.logic_tree,checkBsExistence=True)
        branchExists = False # variable to keep track of if a branch exists
        for i,v in self.logic_tree.blList.copy().items(): # loop through the branchlist and add ids as options to blIdOptions
            if len(v.branchSetList) > 0:
                for x,k in v.branchSetList.copy().items():
                    if len(k.branchList) > 0:
                        branchExists = True
        if blIdOptions == False: # check if there is even a branchlevel to edit
            self.createPopup(wtitle="No branchingLevel",wdescription="No branchingLevel exists")
            return "No branchingLevels"
        if bsExists == False:
            self.createPopup(wtitle="No branchSet",wdescription="No branchSet exists")
            return "No branchSet"
        if branchExists == False:
            self.createPopup(wtitle="No branch",wdescription="No branch exists")
            return "No branch"
        #gui
        self.windowOptions["top"] = tk.Toplevel(self.master)
        self.windowOptions["top"].resizable(False,False)
        self.windowOptions["top"].iconbitmap(self.icon)
        self.placeInCenter(300,72,window=self.windowOptions["top"])
        self.windowOptions["top"].title("Delete")
        self.windowOptions["dropdownFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["dropdownFrame"].pack()
        self.windowOptions["bsIdO"] = None
        self.windowOptions["bIdO"] = None

        self.windowOptions["bl"] = None
        self.windowOptions["bs"] = None
        self.windowOptions["b"] = None

        def createBsIdDropdown(blId):
            self.windowOptions["bl"] = self.logic_tree.getBranchingLevel(blId)
            if self.windowOptions["bl"] == None:
                return 'bad bl'
            self.windowOptions["bsIdOptions"] = self.getBsIdOptions(self.logic_tree.getBranchingLevel(blId))
            if self.windowOptions["bsIdO"] is not None:
                self.windowOptions["bsIdO"].destroy()
            self.windowOptions["bsIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=self.windowOptions["bsIdOptions"],pady=3,defaultval="...",framePackType=tk.LEFT,command=createBIdDropdown)
        def createBIdDropdown(bsId):
            self.windowOptions["bs"] = self.windowOptions["bl"].getBranchSet(realBsId=bsId,type="obj")
            if self.windowOptions["bs"] == None:
                return 'bad bs'
            self.windowOptions["bIdOptions"] = self.getBIdOptions(self.windowOptions["bs"])
            if self.windowOptions["bIdO"] is not None:
                self.windowOptions["bIdO"].destroy()
            self.windowOptions["bIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bId:",options=self.windowOptions["bIdOptions"],pady=3,defaultval="...",framePackType=tk.RIGHT)
        def bIdSelected(bId):
            self.windowOptions["b"] = self.windowOptions["bs"].getBranch(realBId=bId,type="obj")
        self.windowOptions["blIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="blId:",options=blIdOptions,pady=3,defaultval="...",command=createBsIdDropdown,framePackType=tk.LEFT)
        self.windowOptions["bsIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=self.windowOptions["bsIdOptions"],pady=3,defaultval="...",framePackType=tk.LEFT)
        self.windowOptions["bIdO"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bId:",options=self.windowOptions["bIdOptions"],pady=3,defaultval="...",framePackType=tk.RIGHT)
        #submit button
        def submit():
            if self.windowOptions["blIdO"].get() == "...":
                self.createPopup(wtitle="Wrong branchingLevelID",wdescription="Please select a different branchingLevelID")
                return "Invalid bl"
            if self.windowOptions["bsIdO"].get() == "...":
                self.createPopup(wtitle="Wrong branchSetID",wdescription="Please select a different branchSetID")
                return "Invalid bs"
            if self.windowOptions["bIdO"].get() == "...":
                self.createPopup(wtitle="Wrong branchID",wdescription="Please select a different branchID")
                return "Invalid b"
            if self.windowOptions["b"] == None:
                self.windowOptions["b"] = self.windowOptions["bs"].getBranch(realBId=self.windowOptions["bIdO"].get(),type="obj")
            self.windowOptions["bs"].deleteBranch(self.windowOptions["b"].bId)
            self.unsavedChanges = True
            self.updateWindowTitle()
            self.outputLogicTree()
            self.windowOptions["top"].destroy()
        self.windowOptions["submitButton"] = wim.SubmitButton(self.windowOptions["top"],command=submit,button_config={"width":"12"},buttontext="Delete")

    #---smlt/gmpe simplfiied view dropdown---


    #---job bound functions---
    def jNewFile(self):
        def nf():
            del self.jf
            self.jf = job.JobFile()
            for i,v in self.windowOptions.items():
                v.set("")
        self.createPopup(wtype="yn",wtitle="New",wdescription="Are you sure you want to create a new file?\nYou will lose all unsaved data.",yfunc=nf)
    def jOpenFile(self):
        try:
            tempfilepath = filedialog.askopenfilename(initialdir = self.default_path_obj.value,title = "Select file",filetypes = (("ini files","*.ini"),("all files","*.*")))
            if tempfilepath is not "":
                self.file_path = tempfilepath
            else:
                return "User canceled"
        except:
            return "User canceled save"

        self.default_path_obj.value = str(Path(self.file_path).parent) # set default path

        self.jf.open(self.file_path)
        for i,v in self.windowOptions.copy().items():
            v.set(self.jf.settings[i].value)
        self.unsavedChanges=False
        self.updateWindowTitle(unsaved=self.unsavedChanges)
    def jSaveFile(self,newFile=None):
        #checks and ask for file dialog
        openParam = ""
        if self.file_path == None:
            newFile = True
        if newFile == True:
            try:
                tempfilepath = filedialog.asksaveasfilename(initialdir = self.default_path_obj.value,title = "Select file",defaultextension=".ini",filetypes = (("ini file","*.ini"), ("all files","*.*")))
                if tempfilepath == "":
                    return "User canceled save"
                else:
                    self.file_path=tempfilepath
            except FileNotFoundError:
                return "User canceled save"
            openParam = "x"
        else:
            openParam = "w"

        self.default_path_obj.value = str(Path(self.file_path).parent) # set default path

        for i,v in self.windowOptions.copy().items():
            self.jf.set({i:v.get()})
        self.jf.save(file_path=self.file_path)

        self.unsavedChanges=False
        self.updateWindowTitle(unsaved=self.unsavedChanges)

        self.createPopup(wtitle="Successfully saved",wdescription="The file has been saved.")
    def jSaveAsFile(self):
        self.jSaveFile(newFile=True)

    #---main (job)---
    def job_main(self):
        #setup
        self.updateWindowTitle(unsaved=self.unsavedChanges)
        self.jf = jobh.JobFile() # jobfile class
        self.windowOptions={}
        self.master.deiconify() # show window
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.__del__(wclosed=True))
        self.master.bind('<Control-Key-s>',self.jSaveFile)
        self.master.resizable(False,False)
        self.file_path = None
        # window size
        width = 550
        height = 800

        #---menus---
        jMenuBar = tk.Menu(self.master)

        # file drop down
        fileMainMenu = tk.Menu(jMenuBar,tearoff=0) # file drop down
        jMenuBar.add_cascade(label="File",menu=fileMainMenu)
        fileSaveMenu = tk.Menu(jMenuBar,tearoff=0) # save options
        fileExitMenu = tk.Menu(jMenuBar,tearoff=0) # exit Options

        # file commands
        fileMainMenu.add_command(label="New",command=self.jNewFile) # new cascade
        fileMainMenu.add_command(label="Open",command=self.jOpenFile) # new cascade
        fileMainMenu.add_separator()
        fileMainMenu.add_cascade(label="Save",menu=fileSaveMenu) # save cascade
        fileSaveMenu.add_command(label="Save",command=self.jSaveFile) # save option
        fileSaveMenu.add_command(label="Save As",command=self.jSaveAsFile) # save option
        fileMainMenu.add_separator()
        fileMainMenu.add_cascade(label="Exit",menu=fileExitMenu)
        fileExitMenu.add_command(label="Exit to Main Menu",command=self.exitToMainMenuButton)
        fileExitMenu.add_command(label="Exit to Desktop",command=self.exitButton)

        def unsavedBind(key):
            self.unsavedChanges=True
            self.updateWindowTitle(unsaved=self.unsavedChanges)


        def defaultval():
            for i,v in self.windowOptions.copy().items():
                if i in jobh.defaultValues:
                    self.windowOptions[i].set(jobh.defaultValues[i])
        self.createPopup(wtitle="Preset Values",wdescription="Use preset values?",wtype="yn",yfunc=defaultval)

        #---item creation---
        itemframe = tk.Frame(self.master)
        itemframe.grid()
        sections = {}
        rowCount = 0
        for i,v in self.jf.settings.items():
            section = v.section
            try:
                sections[section].configure()
            except:
                sections[section] = tk.Label(itemframe,text=section+":")
                sections[section].configure(font=("Courier", 14))
                sections[section].grid(row=rowCount,column=0,columnspan=2)
                rowCount = rowCount+1
            self.windowOptions[i]=wim.Entry(itemframe,label=i+":",type=wim.windowObject.FULL_ENTRY,noPack=True,entry_config={"justify":tk.LEFT})
            hovertext = ""
            if i in jobh.frequentlyChanged:
                label1 = self.windowOptions[i].Label
                label1.config(fg="red")
                hovertext = "This setting is frequently changed"
            else:
                hovertext = "This setting is rarely changed"
                #print("'{}'".format(i))
            tooltip.CreateToolTip(self.windowOptions[i].Label,hovertext)
            self.windowOptions[i].Label.grid(row=rowCount,column=0)
            self.windowOptions[i].Entry.grid(row=rowCount,column=1)
            self.windowOptions[i].Entry.bind("<Key>", unsavedBind)
            rowCount = rowCount+1

        self.master.config(menu=jMenuBar)
        self.placeInCenter(width,height,window=self.master,place=True)
        self.master.geometry("")
    #---main (smlt/gmpe)---
    def main(self): # main code fo
         #---setup---
        if self.file_type == "Source Model Logic Tree":
            self.logic_tree = ltc.logicTreeC(file_type="SMLT")
        elif self.file_type == "GMPE":
            self.logic_tree = ltc.logicTreeC(file_type="GMPE")
        self.master.deiconify()
        self.master.title("OQInputFiles - "+self.file_type)
        self.master.bind('<Control-Key-s>',self.saveFile)
        self.file_path=None

        # delete self on toplevel window close
        def onDeletion():
            self.updateConfigFile()
            if self.unsavedChanges == True:
                self.createPopup(wtype="yn",wtitle="Unsaved changes",wdescription="Are you sure you want to exit?\nYou have unsaved changes.",nodestroy=True,yfunc=lambda:self.__del__(wclosed=True))
            else:
                self.__del__(wclosed=True)
        self.master.protocol("WM_DELETE_WINDOW", onDeletion)
        # window size
        width = 700
        height = 500
        self.placeInCenter(width,height)

        #---menus---
        # menubar
        menuBar = tk.Menu(self.master) # menu bar

        # file drop down
        fileMainMenu = tk.Menu(menuBar,tearoff=0) # file drop down
        fileSaveMenu = tk.Menu(fileMainMenu,tearoff=0) # save options
        fileExitMenu = tk.Menu(fileMainMenu,tearoff=0) # exit Options
        menuBar.add_cascade(label="File",menu=fileMainMenu) # add cascading list to menubar

        # file commands
        fileMainMenu.add_command(label="New",command=self.newFile) # new cascade
        fileMainMenu.add_command(label="Open",command=self.openFile) # new cascade
        fileMainMenu.add_separator()
        fileMainMenu.add_cascade(label="Save",menu=fileSaveMenu) # save cascade
        fileSaveMenu.add_command(label="Save",command=self.saveFile) # save option
        fileSaveMenu.add_command(label="Save As",command=self.saveAsFile) # save option
        fileMainMenu.add_separator()
        fileMainMenu.add_cascade(label="Exit",menu=fileExitMenu)
        fileExitMenu.add_command(label="Exit to Main Menu",command=self.exitToMainMenuButton)
        fileExitMenu.add_command(label="Exit to Desktop",command=self.exitButton)

        # add drop down
        addMainMenu = tk.Menu(menuBar,tearoff=0) # file drop down
        menuBar.add_cascade(label="Add",menu=addMainMenu) # add cascading list to menubar
        # add commands
        addMainMenu.add_command(label="Add BranchingLevel and BranchSet",command=self.addBlBs) # combo
        addMainMenu.add_separator()
        addMainMenu.add_command(label="Add BranchingLevel",command=self.addBl) # bl
        addMainMenu.add_separator()
        addMainMenu.add_command(label="Add BranchSet",command=self.addBs) # bs
        addMainMenu.add_separator()
        addMainMenu.add_command(label="Add Branch",command=self.addBr) # branch

        # edit drop Dropdown
        editMainMenu = tk.Menu(menuBar,tearoff=0) # edit drop down
        menuBar.add_cascade(label="Edit",menu=editMainMenu) # add cascading list to menubar
        editMainMenu.add_command(label="Edit BranchLevel",command=self.editBl)
        editMainMenu.add_separator()
        editMainMenu.add_command(label="Edit BranchSet",command=self.editBs)
        editMainMenu.add_separator()
        editMainMenu.add_command(label="Edit Branch",command=self.editBr)
        # delete drop Dropdown
        delMainMenu = tk.Menu(menuBar,tearoff=0) # delete drop down
        menuBar.add_cascade(label="Delete",menu=delMainMenu) # add cascading list to menubars
        # delete commands
        delMainMenu.add_command(label="Delete BranchLevel",command=self.deleteBl)
        delMainMenu.add_separator()
        delMainMenu.add_command(label="Delete BranchSet",command=self.deleteBs)
        delMainMenu.add_separator()
        delMainMenu.add_command(label="Delete Branch",command=self.deleteBr)
        # View drop Dropdown
        viewMainMenu = tk.Menu(menuBar,tearoff=0) # view drop down
        viewModeMenu = tk.Menu(menuBar,tearoff=0) # radio menu
        menuBar.add_cascade(label="View",menu=viewMainMenu) # add cascading list to menubars
        viewModeMenu.add_radiobutton(label="XML",value="XML",variable=self.view_obj.value,command=self.outputLogicTree)
        viewModeMenu.add_separator()
        viewModeMenu.add_radiobutton(label="Simplified",value="Simplified",variable=self.view_obj.value,command=self.outputLogicTree)
        viewMainMenu.add_cascade(label="Switch View Mode",menu=viewModeMenu)
        self.view_obj.value.set(self.view_obj.value.get())

        # right-click menu
        self.rightclickable = True
        self.ltviewobject = ViewObject(self.master,ObjectType.LT,self.logic_tree,self.file_type,self)
        self.popmenu = tk.Menu(self.master, tearoff=0)
        self.popmenu.add_command(label="Add BranchingLevel",command=self.ltviewobject.addW)

        def pop(event):
            #self.ltviewobject.xpos = event.x_root
            #self.ltviewobject.ypos = event.y_root
            if not self.rightclickable:
                return False
            try:
                self.popmenu.tk_popup(event.x_root, event.y_root)
            finally:
                self.popmenu.grab_release()

        #self.master.bind("<Button-3>", pop)

        #display
        self.outputArea=None

        #complete
          # add menubar to window
        self.master.config(menu=menuBar)
        self.placeInCenter(width,height)
        self.outputLogicTree()
#---execution---
if __name__ == "__main__":
    ltE = LtEditor(root)
    root.iconbitmap(resource_path("icon.ico"))
    root.mainloop()
    root.quit()
