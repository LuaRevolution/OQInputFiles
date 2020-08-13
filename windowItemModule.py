import tkinter as tk
import enum
#classes
class windowObject(enum.Enum):
    ENTRY = 1
    FULL_ENTRY = 2
    DROPDOWN = 3
    AUTO_ENTRY = 4
    AUTO_FULL_ENTRY = 5
    AUTO_DROPDOWN = 6
class Entry:
    def __init__(self,master,type=None,label="Default",stringvar=None,defaultval=None):
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
        self.Frame = tk.Frame(self.master)
        if self.type == windowObject.ENTRY:
            self.Label = tk.Label(self.Frame,text=self.label)
            self.Label.pack(side=tk.LEFT)
            self.Entry = tk.Entry(self.Frame,variable=stringvar)
            self.Entry.pack(side=tk.LEFT)
        elif self.type == windowObject.FULL_ENTRY:
            self.Label = tk.Label(self.Frame,text=self.label)
            self.Label.pack()
            self.Entry = tk.Entry(self.Frame,variable=stringvar)
            self.Entry.pack(fill=tk.BOTH,expand=True)
        self.Frame.pack()
    def __repr__(self):
        return self.get()
    def destroy(self):
        for k,i in self.Frame.children.copy().items():
            if i is not None:
                i.destroy()
        self.Frame.destroy()
    def get(self):
        return self.Entry.get()
class Dropdown:
    def __init__(self,master,label="Default",stringvar=None,defaultval=None,options=None,noLabel=False,packType=None,command=None):
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
        self.master = master
        self.label = label
        self.Frame = None
        if noLabel == True:
            self.Frame = self.master
            self.OptionMenu = tk.OptionMenu(self.Frame,self.stringvar,*self.options,command=command)
        else:
            self.Frame = tk.Frame(self.master)
            self.Label = tk.Label(self.Frame,text=self.label)
            self.Label.pack(side=tk.LEFT)
            self.OptionMenu = tk.OptionMenu(self.Frame,self.stringvar,*self.options,command=command)
        self.OptionMenu.pack(side=packType)
        self.Frame.pack()
    def __repr__(self):
        return self.get()
    def destroy(self):
        if noLabel == False:
            for k,i in self.Frame.children.copy().items():
                if i is not None:
                    i.destroy()
            self.Frame.destroy()
        elif noLabel == True:
            self.OptionMenu.destroy()
    def get(self):
        return self.OptionMenu.get()
class Automize:
    def __init__(self,master,label="Default",type=None,stringvar=None,defaultval=None,checkButtonText=None,checkButtonCommand=None,checkButtonVar=None):
        if master == None:
            return 'No window'
        if checkButtonText == None:
            self.checkButtonText = ("Automatically assign '{}'".format(label.replace(":","")))
            print(self.checkButtonText)
        else:
            self.checkButtonText = checkButtonText
        if checkButtonVar == None:
            self.checkButtonVar = tk.IntVar()
        else:
            self.checkButtonVar = checkButtonVar
        self.type = windowObject.AUTO_ENTRY
        self.master = master
        self.entryObject = None
        self.label = label
        self.Frame = tk.Frame(self.master)

        def checkButtonF():
            if self.checkButtonVar.get() == 0:
                # uncheck
                if self.entryObject is not None:
                    self.entryObject.destroy()
                if checkButtonCommand is not None:
                    checkButtonCommand(checked=False)
                self.checkButtonVar.set(1)
            elif self.checkButtonVar.get() == 1:
                # check
                self.entryObject = Entry(self.Frame,label=self.label,type=windowObject.ENTRY,stringvar=stringvar,defaultval=defaultval)
                if checkButtonCommand is not None:
                    checkButtonCommand(checked=True)
                self.checkButtonVar.set(0)
        self.checkButton = tk.Checkbutton(self.Frame,text=self.checkButtonText,command=checkButtonF)
        self.checkButton.pack()
        self.checkButton.deselect()
        self.checkButton.invoke()

        self.Frame.pack()
    def __repr__(self):
        return self.get()
    def destroy(self):
        for k,i in self.Frame.children.copy().items():
            if i is not None:
                i.destroy()
        self.Frame.destroy()
    def get(self):
        if self.entryObject is not None:
            return self.Ent.get()
        else:
            return None

if __name__ == "__main__":
    root = tk.Tk()
    test = AutoEntry(root,label="test")
    root.mainloop()
