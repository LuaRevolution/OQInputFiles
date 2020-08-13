import tkinter as tk
import enum
#classes
class windowObject(enum.Enum):
    ENTRY = "ENTRY OBJECT"
    FULL_ENTRY = "FULL_ENTRY OBJECT"
    DROPDOWN = "DROPDOWN OBJECT"
    FULL_DROPDOWN = "FULL_DROPDOWN OBJECT"
    AUTOMATION = "AUTOMATION OBJECT"
class Entry:
    def __init__(self,master,type=None,label="Default",stringvar=None,defaultval=None,pady=3):
        # declarations
        if master == None:
            return 'No window'
        if type == None:
            self.type = windowObject.ENTRY
        else:
            self.type = type
        if stringvar == None:
            self.stringvar = tk.StringVar()
        else:
            self.stringvar = stringvar
        self.master = master
        self.label = label
        # Gui
        self.Frame = tk.Frame(self.master)
        if self.type == windowObject.ENTRY:
            self.Label = tk.Label(self.Frame,text=self.label)
            self.Label.pack(side=tk.LEFT,pady=pady)
            self.Entry = tk.Entry(self.Frame,variable=stringvar)
            self.Entry.pack(side=tk.LEFT,pady=pady)
        elif self.type == windowObject.FULL_ENTRY:
            self.Label = tk.Label(self.Frame,text=self.label)
            self.Label.pack(pady=pady)
            self.Entry = tk.Entry(self.Frame,variable=stringvar)
            self.Entry.pack(fill=tk.BOTH,expand=True,pady=pady)
        self.Frame.pack()
    def __repr__(self):
        return self.get()
    def destroy(self):
        for k,i in self.Frame.children.copy().items():
            if i is not None:
                i.destroy()
        self.Frame.destroy()
        del self
    def get(self):
        return self.Entry.get()
class Dropdown:
    def __init__(self,master,label="Default",stringvar=None,defaultval=None,options=None,noLabel=None,packType=None,command=None,pady=3,type=windowObject.DROPDOWN):
        # declarations
        if master == None:
            return 'No window'
        if stringvar == None:
            self.stringvar = tk.StringVar()
        else:
            self.stringvar = stringvar
        if defaultval is not None:
            self.stringvar.set(defaultval)
        if packType == None:
            self.packType = tk.LEFT
        if options == None:
            self.options = ["Default"]
            if self.stringvar is not None and defaultval is None:
                self.stringvar.set(self.options[0])
        if noLabel == None:
            noLabel = False
            self.noLabel = noLabel
        else:
            self.noLabel = noLabel
        self.master = master
        self.label = label
        self.Label = None

        #gui
        self.Frame = tk.Frame(self.master)
        self.Frame.pack()
        self.OptionMenu = tk.OptionMenu(self.Frame,self.stringvar,*self.options,command=command)
        if self.noLabel == False:
            self.Label = tk.Label(self.Frame,text=self.label)
            if type == windowObject.DROPDOWN:
                self.Label.pack(side=self.packType,pady=pady)
            elif type == windowObject.FULL_DROPDOWN:
                self.Label.pack(pady=pady)
            self.OptionMenu.pack(side=self.packType,pady=pady)
        else:
            self.OptionMenu.pack(side=self.packType,pady=pady)
    def __repr__(self):
        return self.get()
    def destroy(self):
        if self.noLabel == False:
            for k,i in self.Frame.children.copy().items():
                if i is not None:
                    i.destroy()
            self.Frame.destroy()

        elif self.noLabel == True:
            self.OptionMenu.destroy()
        del self
    def get(self):
        return self.OptionMenu.get()
class Automation:
    def __init__(self,master,objectType,_checkbuttoncommand=None,_checkbuttontext=None,**kwargs):
        if master == None:
            return 'No window'
        if _checkbuttontext == None:
            try:
                _checkbuttontext = ("Automatically assign '{}'".format(kwargs["label"].replace(":","")))
            except:
                _checkbuttontext = "No text"

        self.type = windowObject.AUTOMATION
        self.master = master
        self.checkButtonVar = tk.IntVar()
        self.Frame = tk.Frame(self.master)
        self.Frame.pack()
        self.object = None

        def checkButtonF():
            if self.checkButtonVar.get() == 0:
                # uncheck
                if self.object is not None:
                    self.object.destroy()
                if _checkbuttoncommand is not None:
                    _checkbuttoncommand(checked=False)
                self.checkButtonVar.set(1)
            elif self.checkButtonVar.get() == 1:
                # check
                if objectType == windowObject.ENTRY:
                    self.object = Entry(self.Frame,**kwargs)
                elif objectType == windowObject.DROPDOWN:
                    self.object = Dropdown(self.Frame,**kwargs)
                if _checkbuttoncommand is not None:
                    _checkbuttoncommand(checked=True)
                self.checkButtonVar.set(0)
        self.checkButton = tk.Checkbutton(self.Frame,text=_checkbuttontext,command=checkButtonF)
        self.checkButton.pack()
        self.checkButton.deselect()
        self.checkButton.invoke()
    def __repr__(self):
        return self.type
    def destroy(self):
        self.object.destroy()
        del self
    def get(self):
        return self.object

if __name__ == "__main__":
    root = tk.Tk()
    test = Automation(root,windowObject.DROPDOWN,label="Test:")
    test2 = Dropdown(root,noLabel=True)
    root.mainloop()
