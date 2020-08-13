# notes:
# the program flow goes as follows: __main__ -> ltEditor.__init__ -> ltEditor.startMenu() -> ltEditor.main(), the last being the actual main


#---imports---
import tkinter as tk
#import configparser
from tkinter import filedialog
from PIL import ImageTk, Image
import enum
import os
#own imports
import ltc
import windowItemModule as wim
#---core variables---
root = tk.Tk()
#config = configparser.ConfigParser()
#---core functions---
def switchFileTypes(ltEditorObj):
    ltEditorObj.__del__(wclosed=False)
    newLte = LtEditor(root)
#---classes / gui---
class LtEditor:
    #---event methods---
    def __init__(self, master, *args, **kwargs):
        # init is not actually where the main portion of the gui inits, main_init is
        self.tk = master # actual tkinter instance
        self.tk.withdraw() # hide the legitmate tkinter instance
        self.master = tk.Toplevel() # create our actual window
        self.master.withdraw() # hide the window temporarily
        self.file_type = None # default file type
        self.logic_tree = None # logic tree
        self.view_mode = tk.StringVar() # viewmode (mode to display logictree object in): xml, Simplified
        self.file_path = None # saved/opened file path
        self.unsavedChanges = False # keep track of unsaved changes
        #self.master.resizable(False,False)

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
        top.title("ltEditor - Select a file type")
        width = 325
        height = 300
        x = (top.winfo_screenwidth() // 2) - (width //2)
        y = (top.winfo_screenheight() // 2) - (height //2)
        top.geometry("{}x{}+{}+{}".format(width,height,x,y))

        # delete self on toplevel window close
        top.protocol("WM_DELETE_WINDOW", top.quit)
        #logo
        logoFile=ImageTk.PhotoImage(file="logo.png")
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
    def placeInCenter(self, width,height,window=None,place=True): #fixes x,y placement of window
        if window is None:
            window=self.master
        x = (window.winfo_screenwidth() // 2) - (width //2)
        y = (window.winfo_screenheight() // 2) - (height //2)
        if place==True:
            window.geometry("{}x{}+{}+{}".format(width,height,x,y))
        else:
            window.geometry("{}x{}".format(width,height))
    def pToOutput(self,text): # print to output
        self.outputArea.configure(state=tk.NORMAL)
        self.outputArea.delete(1.0, "end")
        self.outputArea.insert("end", text)
        self.outputArea.configure(state=tk.DISABLED)
    def outputLogicTree(self,ltobj=None,file_type=None,viewmode=None): # displays the logic tree in either the xml or simplfiied format
        if ltobj==None:
            ltobj=self.logic_tree
        if file_type==None:
            file_type=self.file_type
        str = ""
        if viewmode == None:
            viewmode = self.view_mode.get()
        if viewmode == "Simplified":
            if file_type=="Source Model Logic Tree":
                isFirst=True
                for a,b in ltobj.blList.copy().items():
                    if isFirst == True:
                        str = str+("BranchingLevel (branchingLevelId: %s)"%b.blId)
                        isFirst=False
                    else:
                        str = str+("\n\nBranchingLevel (branchingLevelId: %s)"%b.blId)
                    for k,l in b.branchSetList.copy().items():
                        str = str+("\n  BranchSet (branchSetId: {})(uncertaintyType: {})".format(l.realBsId, l.uncertaintyType))
                        for x,z in l.branchList.copy().items():
                            str = str+("\n    Branch (branchId: {})(uncertaintyModel: {})(uncertaintyWeight: {})".format(z.realBId, z.uncertaintyModel,z.uncertaintyWeight))
            elif file_type == "GMPE":
                isFirst=True
                for a,b in ltobj.blList.copy().items():
                    if isFirst == True:
                        str = str+("BranchingLevel (branchingLevelId: %s)"%b.blId)
                        isFirst=False
                    else:
                        str = str+("\n\nBranchingLevel (branchingLevelId: %s)"%b.blId)
                    for k,l in b.branchSetList.copy().items():
                        str = str+("\n  BranchSet (branchSetId: {})(uncertaintyType: {})(applyToTectonicRegionType: {})".format(l.realBsId, l.uncertaintyType,l.applyToTectonicRegionType))
                        for x,z in l.branchList.copy().items():
                            str = str+("\n    Branch (branchId: {})(gmpeTable: {})(uncertaintyWeight: {})".format(z.realBId, z.GMPETable,z.uncertaintyWeight))
        elif viewmode == "XML":
            str = ltc.createXML(ltobj)
        self.pToOutput(str)
    def createPopup(self,wtype="message",wtitle="Popup",wdescription="Description",okfunc=None,yfunc=None,nfunc=None,oktext="Ok",ytext="Yes",ntext="No"): # creates a popup
        #two types: message and yn
        top = tk.Toplevel(self.master)
        top.resizable(False,False)
        top.title(wtitle)
        self.placeInCenter(300,85,window=top)
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
                    top.destroy()
                ybutton.configure(command=yfunc)
            else:
                def yfunc2():
                    yfunc()
                    top.destroy()
                ybutton.configure(command=yfunc2)
            if nfunc is None:
                def nfunc():
                    top.destroy()
                nbutton.configure(command=nfunc)
            else:
                def nfunc2():
                    nfunc()
                    top.destroy()
                nbutton.configure(command=nfunc2)
        else:
            button = tk.Button(frame,text=oktext,width=(len(oktext)*3))
            button.pack()
            if okfunc is None:
                def okfunc():
                    top.destroy()
                button.configure(command=okfunc)
            else:
                def okfunc2():
                    okfunc()
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
        self.outputLogicTree(viewmode=self.view_mode.get())
        return self.logic_tree
    def updateWindowTitle(self,unsaved=True): # updates the window title
        if unsaved==True:
            if self.file_path == None:
                self.master.title("ltEditor - "+self.file_type+" - *")
            else:
                self.master.title("ltEditor - "+self.file_type+" - "+self.file_path+"*")
        else:
            self.master.title("ltEditor - "+self.file_type+" - "+self.file_path)
    def readConfig(self,key): # fetches the config value for the key given
        pass
    def updateConfig(self, dict): # loops through given dict, updating the config fike
        pass

    #---bound functions---
    # file dropdown
    def newFile(self,file_type=None): # creates a new file
        self.createPopup(wtype="yn",wtitle="New",wdescription="Are you sure you want to create a new file?\nYou will lose all unsaved data.",yfunc=self.newLt)
    def openFile(self,file_type=None): # opens file prompt then imports file
        try:
            self.file_path=filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("XML files","*.xml"),("all files","*.*")))
        except:
            return "User canceled save"

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
                self.file_path = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",defaultextension=".xml",filetypes = (("XML file","*.xml"), ("all files","*.*")))
            except FileNotFoundError:
                return "User canceled save"
            openParam = "x"
        else:
            openParam = "w"
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
            self.outputLogicTree(viewmode=self.view_mode.get())
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
        width=400
        height=200
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
            self.outputLogicTree(viewmode=self.view_mode.get())
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
                self.outputLogicTree(viewmode=self.view_mode.get())
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
                self.outputLogicTree(viewmode=self.view_mode.get())
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
                self.outputLogicTree(viewmode=self.view_mode.get())
                self.unsavedChanges=True
                self.updateWindowTitle()
                self.windowOptions["top"].destroy()


        addButton = tk.Button(top,text="Add",command=addButtonF,width=9)
        addButton.grid(row=9,column=0,columnspan=4,pady=(5,5))
        top.geometry("") # adds branch

    #Edit Dropdown
    def editBl(self): # creates prompt to edit a branchinglevel
        blIdOptions = [] # list to hold all branchinglevel ids
        for i,v in self.logic_tree.blList.copy().items(): # loop through the branchlist and add ids as options to blIdOptions
            blIdOptions.append(v.blId)
        if len(blIdOptions) == 0: # check if there is even a branchlevel to edit
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
                self.outputLogicTree()
                top.destroy()
        addButton = tk.Button(top,text="Edit",command=addButtonF,width=12)
        addButton.pack(pady=3)
    def editBs(self,file_type=None): # creates prompt to edit a branchSet
        #setup
        if file_type is None:
            file_type = self.file_type
        self.windowOptions={}
        blIdOptions = [] # list to hold all branchinglevel ids
        bsIdOptions = ["Select a branchLevel first"] # list to hold all branchSet ids
        branchSetExists = False # variable to keep track of if a branchset exits
        for i,v in self.logic_tree.blList.copy().items(): # loop through the branchlist and add ids as options to blIdOptions
            if len(v.branchSetList) > 0:
                branchSetExists = True # also check for a branch set
            blIdOptions.append(i)
        if len(blIdOptions) == 0: # check if there is even a branchlevel to edit
            self.createPopup(wtitle="No branchLevel exists",wdescription="No branchLevel exists\nCreate one now?",wtype="yn",yfunc=self.addBl)
            return "No branchingLevels"
        if branchSetExists == False:
            self.createPopup(wtitle="No branchSet exists",wdescription="No branchSet exists\nCreate one now?",wtype="yn",yfunc=self.addBs)
            return "No branchSet to edit"

        #gui
        self.windowOptions["top"] = tk.Toplevel(self.master)
        self.windowOptions["top"].title("Edit a branchSet")
        if file_type == "Source Model Logic Tree":
            self.placeInCenter(300,149,window=self.windowOptions["top"])
        else:
            self.placeInCenter(300,200,window=self.windowOptions["top"])


        # frames
        self.windowOptions["dropdownFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["dropdownFrame"].pack()
        self.windowOptions["optionFrame"] = tk.Frame(self.windowOptions["top"])
        self.windowOptions["optionFrame"].pack()
        #dropdowns
        self.windowOptions["bsIdDropdown"] = None
        # blid dropdown
        def createBsIdDropdown(blId):
            if self.windowOptions["bsIdDropdown"] is not None:
                self.windowOptions["bsIdDropdown"].destroy()
            bl = self.logic_tree.getBranchingLevel(blId)
            bsIdOptions = []
            for i,v in bl.branchSetList.copy().items():
                bsIdOptions.append(i)
            self.windowOptions["bsIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=bsIdOptions,defaultval="...",framePackType=tk.LEFT)
        self.windowOptions["blIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="blId:",options=blIdOptions,defaultval="...",command=createBsIdDropdown,framePackType=tk.LEFT)
        # bsid dropdown
        def bsIdSelected(bsId):
            pass
        self.windowOptions["bsIdDropdown"] = wim.Dropdown(self.windowOptions["dropdownFrame"],label="bsId:",options=bsIdOptions,defaultval="...",framePackType=tk.LEFT)
        # options
        self.windowOptions["bsIdO"] = wim.Entry(self.windowOptions["optionFrame"], label="bsId:")
        self.windowOptions["uncertaintyTypeO"] = wim.Entry(self.windowOptions["optionFrame"], label="uncertaintyType:",type=wim.windowObject.FULL_ENTRY)
        self.windowOptions["attrO"] = None
        if file_type == "GMPE":
            self.windowOptions["attrO"] = wim.Entry(self.windowOptions["optionFrame"], label="applyToTectonicRegionType:",type=wim.windowObject.FULL_ENTRY)
        def submit():
            bl = self.logic_tree.getBranchingLevel(self.windowOptions["blIdDropdown"].get())
            bs = bl.getBranchSet(bsId=self.windowOptions["bsIdDropdown"].get(),type="obj")
            bs.realBsId = self.windowOptions["bsIdO"].get()
            bs.uncertaintyType = self.windowOptions["uncertaintyTypeO"].get()
            if file_type == "GMPE":
                bs.applyToTectonicRegionType = self.windowOptions["attrO"].get()
            self.outputLogicTree()
        addButton = wim.SubmitButton(self.windowOptions["top"],buttontext="Done",command=submit)


    def editBr(self,file_type=None): # creates prompt to edit a branch
        pass

    #Delete Dropdown
    def deleteBl(self,file_type=None): # creates prompt to delete a branchinglevel
        pass
    def deleteBs(self,file_type=None): # creates prompt to delete a branchSet
         pass
    def deleteBr(self,file_type=None): # creates prompt to delete a branch
        pass


    #---main (job)---
    def job_main(self):
        pass

    #---main (smlt/gmpe)---
    def main(self): # main code for
        #---setup---
        if self.file_type == "Source Model Logic Tree":
            self.logic_tree = ltc.logicTreeC(file_type="SMLT")
        elif self.file_type == "GMPE":
            self.logic_tree = ltc.logicTreeC(file_type="GMPE")
        self.master.deiconify()
        self.master.title("ltEditor - "+self.file_type)

        # delete self on toplevel window close
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.__del__(wclosed=True))
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
        addBlBsMenu = tk.Menu(addMainMenu,tearoff=0)
        menuBar.add_cascade(label="Add",menu=addMainMenu) # add cascading list to menubar
        # add commands
        addMainMenu.add_cascade(label="Add BranchingLevel/BranchSet",menu=addBlBsMenu) # bl/bs options
        addMainMenu.add_separator()
        addBlBsMenu.add_command(label="Add BranchingLevel and BranchSet",command=self.addBlBs) # combo
        addBlBsMenu.add_separator()
        addBlBsMenu.add_command(label="Add BranchingLevel",command=self.addBl) # bl
        addBlBsMenu.add_separator()
        addBlBsMenu.add_command(label="Add BranchSet",command=self.addBs) # bs
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
        viewModeMenu.add_radiobutton(label="XML",value="XML",variable=self.view_mode,command=self.outputLogicTree)
        viewModeMenu.add_separator()
        viewModeMenu.add_radiobutton(label="Simplified",value="Simplified",variable=self.view_mode,command=self.outputLogicTree)
        self.view_mode.set("XML")
        viewMainMenu.add_cascade(label="Switch View Mode",menu=viewModeMenu)

        #display
        self.outputArea = tk.Text(
            self.master,
            bg="#e6e6e6",
            state=tk.DISABLED
        )
        self.outputScroll = tk.Scrollbar(self.master, command=self.outputArea.yview)
        self.outputArea.configure(yscrollcommand=self.outputScroll.set)
        self.outputArea.pack(side=tk.LEFT, fill=tk.BOTH,expand=True)
        self.outputScroll.pack(side=tk.RIGHT,fill=tk.Y)

        #complete
        self.master.config(menu=menuBar) # add menubar to window
        self.placeInCenter(width,height)
#---execution---
if __name__ == "__main__":
    ltE = LtEditor(root)
    root.mainloop()
