import tkinter as tk
import enum
#classes
class windowObject(enum.Enum):
    ENTRY = "ENTRY OBJECT"
    FULL_ENTRY = "FULL_ENTRY OBJECT"
    DROPDOWN = "DROPDOWN OBJECT"
    FULL_DROPDOWN = "FULL_DROPDOWN OBJECT"
    AUTO_OBJECT = "AUTOMATIC OBJECT"
    SUBMIT_BUTTON = "SUBMIT_BUTTON OBJECT"
class Entry:
    # vital arguments:
    # - master (container)
    # - label (text of the label)
    # semi-vital arguments:
    # - type (specify whether the entry should be next to the label or on the next line and cover the window) -> windowObject.ENTRY or windowObject.FULL_ENTRY
    # - stringvar (variable that the entry uses to hold it's value)
    # - defaultval (default text of the entry)
    # methods:
    # - destroy() -> deletes label and entry, and self
    # - get() -> returns the value of the entry
    # - set(str) -> sets the value of the entry to str
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
    def set(self,str):
        self.Entry.set(str)
class Dropdown:
    # vital arguments:
    # - master (container)
    # - label (label text)
    # - options (options for the dropdown menu)
    # semi-vital arguments:
    # - type (whether the object is a FULL_DROPDOWN or DROPDOWN)
    # - command (function called when dropdown option is selected)
    # - stringvar (variable that the dropdown changes)
    # - defaultval (default value for the dropdown)
    # - noLabel (specify whether or not to have no label, just dropdown)
    # unimportant arguments:
    # - packType (pack "side" argument for the label and dropdown)
    # - framePackType (pack "side" argument for the frame holding the label and dropdown)
    # - pady (y padding for the label and dropdown)
    # methods:
    # - destroy() -> deletes label and dropdown, and self
    # - get() -> returns the value of the entry
    def __init__(self,master,label="Default",stringvar=None,defaultval=None,options=None,noLabel=None,packType=None,command=None,pady=3,framePackType=None,type=windowObject.DROPDOWN):
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
        else:
            self.packType = packType
        if options == None:
            self.options = ["Default"]
            if self.stringvar is not None and defaultval is None:
                self.stringvar.set(self.options[0])
        else:
            self.options = options
        if noLabel == None:
            noLabel = False
            self.noLabel = noLabel
        else:
            self.noLabel = noLabel
        self.master = master
        self.label = label
        self.Label = None
        self.type = windowObject.DROPDOWN

        #gui
        self.Frame = tk.Frame(self.master)
        if framePackType == None:
            self.Frame.pack()
        else:
            self.Frame.pack(side=framePackType)
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
class AutoObject:
    # notes: any other arguments are passed directly to the desired object (ex "label" argument will be passed to the Entry object)
    # vital arguments:
    # - master (container)
    # - objectType (type of the object you want to automate)
    # semi-vital arguments:
    # - _checkbuttoncommand (function that will be called when the checkbutton is clicked) -> this function will get passed a boolean argument "checked" that specifies whether the box is checked
    # - _checkbuttontext (text of the checkbutton)
    # methods:
    # - destroy() -> deletes the tkinter widgets and self
    # - get() -> returns the actual object (example: an Entry object)
    def __init__(self,master,objectType,_checkbuttoncommand=None,_checkbuttontext=None,**kwargs):
        if master == None:
            return 'No window'
        if _checkbuttontext == None:
            try:
                _checkbuttontext = ("Automatically assign '{}'".format(kwargs["label"].replace(":","")))
            except:
                _checkbuttontext = "No text"

        self.type = windowObject.AUTO_OBJECT
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
        self.Frame.destroy()
        del self
    def get(self):
        return self.object
class SubmitButton:
    def __init__(self,master,buttontext="Submit",command=None,pady=3,packType=None):
        self.Button = tk.Button(master,text=buttontext,width=(len(buttontext)*3))
        if packType == None:
            self.Button.pack(side=packType,pady=pady)
        else:
            self.Button.pack(pady=pady)
        self.command=command
        self.Button.configure(command=self.submit)
        self.type = windowObject.SUBMIT_BUTTON
    def destroy(self):
        self.Button.destroy()
        del self
    def submit(self):
        if self.command is not None:
            self.command()
        top = None
        while True:
            object = self.Button.master
            if isinstance(object, tk.Toplevel) or isinstance(object,tk.Tk):
                top = object
                break
        top.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    test = AutoObject(root,windowObject.DROPDOWN,label="Test:")
    test2 = Dropdown(root,noLabel=True)
    root.mainloop()
