
######### IMPORTS
import configparser
import sys
import json
import pyperclip
import xml.dom.minidom

#ElementTree
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
parser = configparser.ConfigParser()

######### VARIABLES / SETUP
smltCVars = { # SMLT Core Variables -> Core variables, largely unmodified
    "xmlns:gml": "http://www.opengis.net/gml",
    "xmlns": "http://openquake.org/xmlns/nrml/0.4"
}

######### CLASSES
# note: realbid/realbsid is the id that appears in the generated xml, whereas just bid/bsid is the id that appears in backend code
class branchC:
    def changeBranchingLevel(self,newBranchSet,newBId=0): #method to change branch's branching level
        if newSId == 0:
            newBId = self.bId
        self.branchSet.deleteBranch(self.bId, totalDeletion=False) # delete from old list of entities
        newBranchSet.addBranch(bId=newBId,uncertaintyModel=self.uncertaintyModel,uncertaintyWeight=self.uncertaintyWeight,new=False,branch=self) #add to it's list of entities
        self.branchSet = newBranchingSet # change our variable
    def __init__(self,branchSet,bId,uncertaintyModel,uncertaintyWeight, GMPETable=None, realBId=None,file_type="auto"):
        if file_type == "auto":
            self.file_type=branchSet.branchLevel.logicTree.file_type
        else:
            self.file_type=file_type
        if realBId == None:
            realBId = bId
        if self.file_type == "GMPE": #gmpe has a different bId system than SMLT, so this code is to change smlt bid into gmpe bid
            temp_bl = branchSet.branchLevel.blId
            bl_num = temp_bl[2:len(temp_bl)]
            temp_bid = "b"+bl_num+bId[1:len(bId)]
            if realBId != temp_bid:
                realBId=temp_bid
        self.branchSet = branchSet
        self.bId = bId
        self.realBId = realBId

        self.uncertaintyModel = uncertaintyModel
        self.uncertaintyWeight = uncertaintyWeight
        self.GMPETable = GMPETable
        self.Class = "branchC" #  on creation
    def __del__(self):
        pass # on deletion
    def __repr__(self):
        return "<branchC bId:%s blId:%s uncertaintyModel:%s uncertaintyWeight:%s>" % (self.bId,self.branchSet.branchLevel.blId,self.uncertaintyModel,self.uncertaintyWeight) # return
class branchSetC:
    def __init__(self, branchLevel, bsId, uncertaintyType="default", branchList={},file_type="auto",applyToTectonicRegionType="default",realBsId=None):
        if file_type == "auto":
            self.file_type=branchLevel.logicTree.file_type
        else:
            self.file_type=file_type
        if uncertaintyType=="default":
            if self.file_type=="SMLT":
                uncertaintyType="sourceModel"
            elif self.file_type=="GMPE":
                uncertaintyType="gmpeModel"
        if realBsId == None:
            self.realBsId = bsId
        if self.file_type == "GMPE":
            self.applyToTectonicRegionType=applyToTectonicRegionType
            #bsid stuff
            temp_bl = branchLevel.blId
            bl_num = temp_bl[2:len(temp_bl)]
            temp_bsid = "bs"+bl_num
            realBsId=temp_bsid
        self.branchLevel=branchLevel # parent object
        self.bsId=bsId # branch set id
        self.uncertaintyType=uncertaintyType # uncertaintyType
        self.branchList={} # list of children objects
        self.Class = "branchSetC" # class name, for identification
    def __del__(self):
        for k,v in self.branchList.copy():
            self.deleteBranch(k) #delete branch
    def __repr__(self):
        return "<branchSetC bsId:%s blId:%s treeId:%s>" % (self.bsId,self.branchLevel,self.branchLevel.logicTree.ltId)
    def addBranch(self,bId="def",uncertaintyModel="default",uncertaintyWeight="default", new=True, branch=None, GMPETable=None, realBId=None, file_type="auto"): # method to add branching level. This can be used to add a branch to a different branchinglevel as well as to create a whole different one
        if bId in self.branchList: # Check if branch id is already in use
            return "Error: branch ID already in use"
        elif bId=="def":
            bId = "b"+str(len(self.branchList)+1) #generate bid
        if new == True:
            newBranch = branchC(self, bId,uncertaintyModel,uncertaintyWeight,GMPETable=GMPETable,realBId=realBId,file_type=file_type) # create new branch
            self.branchList[bId] = newBranch # add to the list of branch entities
            return newBranch
        elif new == False:
            if branch is None: # check if branch exists
                return "Error: Branch is non existent"
            else:
                self.branchList[branch.bId] = branch # add branch to branchList
                return self.branchList[branch.bId]
    def deleteBranch(self,bId,totalDeletion=True): # method to delete branching level, check if you need to remove it from its list of children or completely obliterate it
        if bId in self.branchList:
            branchInQuestion = self.branchList[bId]
            self.branchList.pop(bId)
            if totalDeletion == True:
                del branchInQuestion
    def getBranch(self,realBId="def",bId="def",type="id"):
        if realBId == "def" and bId == "def":
            return 'Error: No Criteria Given'
        elif realBId != "def":
            for k,v in self.branchList.copy().items():
                if realBId == v.realBId:
                    if type == "id":
                        return v.bId
                    elif type == "obj":
                        return self.branchList[k]
        elif bId != "def":
            try:
                self.branchList[bId]
            except KeyError:
                return "Error: Object with key '%s' does not exist." % bId
            else:
                if type == "id":
                    return self.branchList[bId].realBId
                elif type == "obj":
                    return self.branchList[bId]
class branchingLevelC:
    def addBranchSet(self,bsId="def",uncertaintyType="default", new=True,branchSet=None, file_type="auto", applyToTectonicRegionType="default"): # method to add branching level. This can be used to add a branch to a different branchinglevel as well as to create a whole different one
        if bsId in self.branchSetList: # Check if branch id is already in use
            return "Error: branchSet ID already in use"
        elif bsId=="def":
            bsId = "bs"+str(len(self.branchSetList)+1) #generate bsid
        if new == True:
            newBranchSet = branchSetC(self,bsId,uncertaintyType=uncertaintyType,file_type=file_type,applyToTectonicRegionType=applyToTectonicRegionType) # create new branch
            self.branchSetList[bsId] = newBranchSet # add to the list of branch entities
            return newBranchSet
        elif new == False:
            if branchSet is None: # check if branchSet exists
                return "Error: BranchSet is non existent"
            else:
                self.branchSetList[branchSet.bsId] = branchSet # add branch to branchList
                return self.branchSetList[branchSet.bsId]
    def deleteBranchSet(self,bsId,totalDeletion=True,deletingAll=False): # method to delete branchset, check if you need to remove it from its list of children or completely obliterate it
        if bsId in self.branchSetList.copy():
            branchSetInQuestion = self.branchSetList[bsId]
            if totalDeletion == True:
                del branchSetInQuestion
            if deletingAll == True:
                self.branchSetList.pop(bsId)
    def getBranchSet(self,realBsId="def",bsId="def",type="id"): # can be used to get branchset id, real branchset id, or object itself from all of the above.
        if realBsId == "def" and bsId == "def":
            return 'Error: No Criteria Given'
        elif realBsId != "def":
            for k,v in self.branchSetList.copy().items():
                if realBsId == v.realBsId:
                    if type == "id":
                        return v.bsId
                    elif type == "obj":
                        return self.branchSetList[k]
        elif bsId != "def":
            try:
                self.branchSetList[bsId]
            except KeyError:
                return "Error: Object with key '%s' does not exist." % bsId
            else:
                if type == "id":
                    return self.branchSetList[bsId].realBsId
                elif type == "obj":
                    return self.branchSetList[bsId]
    def __init__(self, tree, blId, branchSetList={},file_type="auto"): # tree is the logic tree it is in, branchList is the list for existing branches
        self.logicTree = tree
        self.blId = blId
        self.branchSetList = branchSetList
        self.Class = "branchingLevelC"
        if file_type == "auto":
            self.file_type=self.logicTree.file_type
        else:
            self.file_type=file_type
    def __del__(self):
        for k,v in self.branchSetList.items():
            self.deleteBranchSet(k) #delete branch
    def __repr__(self):
        return "<branchingLevelC blId:%s treeId:%s>" % (self.blId,self.logicTree.ltId)
class logicTreeC:
    def __init__(self, ltId="lt1", blList={}, file_type="SMLT"): # get ltid, and check for existing branching levels.
        self.ltId = ltId # Get our ltId
        self.blList = blList
        self.itself = self
        self.file_type=file_type
        self.Class = "logicTreeC"
    def addBranchingLevel(self,blId="def", branchSetList={}, new=True, branchingLevel=None, file_type="auto"): # method to add branching level
        if blId == "def": #check if auto blid
            blId = "bl"+str(len(self.blList)+1) #generate blid
        if file_type == "auto":
            file_type == self.file_type
        if new == False: #check if new
            if branchingLevel == None: #see if branching level exists
                return "Error: Branching Level does not exist"
            self.blList[branchingLevel.blId] = branchingLevel # add to our list
            return newBranchingLevel
        else:
            newBranchingLevel = branchingLevelC(self,blId,file_type=file_type)
            self.blList[newBranchingLevel.blId] = newBranchingLevel
            return newBranchingLevel
    def deleteBranchingLevel(self,blId,deletingAll=False): # method to delete branching level
        if blId in self.blList.copy():
            branchingLevelInQuestion = self.blList[blId]
            del branchingLevelInQuestion
            if deletingAll==False:
                self.blList.pop(blId)
    def debugPrint(self):
        print("LogicTree ID: "+str(self.ltId))
        for a,b in self.blList.items():
            print("-->BranchingLevel ID: "+str(b.blId))
            for i,v in b.branchSetList.items():
                print("---->BranchSet ID: "+v.bsId+", uncertaintyType: "+v.uncertaintyType)
                for x,k in v.branchList.items():
                    print("------>Branch ID: "+k.realBId+" (list_bid: %s)" % k.bId)
                    print("-------->uncertaintyModel: "+k.uncertaintyModel)
                    print("-------->uncertaintyWeight: "+k.uncertaintyWeight)
                    if k.GMPETable is not None:
                        print("-------->gmpe_table: "+k.GMPETable)
    def __del__(self):
        for k,v in self.blList.items():
            self.deleteBranchingLevel(k,deletingAll=True)
        self.blList.clear()
    def __repr__(self):
        return "<logicTreeC ltId:%s>" % (self.ltId)


######### FUNCTIONS
def getopts(argv): #code to get arguments
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts
def createXML(logicTreeObj, prettyPrint=True):
    # make sure the object is correct
    try:
        logicTreeObj.Class
    except AttributeError:
        err = "Error: No LTC class given"
        print(err)
        return "Error: No LTC class given"
    if not logicTreeObj.Class == "logicTreeC":
        err = "Error: Object is not class 'logicTreeC'"
        print(err)
        return "Error: Object is not class 'logicTreeC'"

    # root stuff
    root = Element("nrml")
    root.set("xmlns:gml", smltCVars["xmlns:gml"])
    root.set("xmlns", smltCVars["xmlns"])

    # logic tree
    lt = ET.SubElement(root, "logicTree", {"logicTreeID": logicTreeObj.ltId})

    # branchLevels
    for k,v in logicTreeObj.blList.items():
        curBl = ET.SubElement(lt, "logicTreeBranchingLevel", {"branchingLevelID": v.blId}) # curBl -> current branch level.

        if logicTreeObj.file_type == "SMLT":
            for a,b in v.branchSetList.items():
                curBs = ET.SubElement(curBl, "logicTreeBranchSet", {"uncertaintyType": b.uncertaintyType,"branchSetID": b.bsId}) # curBs -> current branchset.
                for x,z in b.branchList.items():
                    curBr = ET.SubElement(curBs, "logicTreeBranch", {"branchID": z.realBId}) # curBr -> current branch
                    cUncMod = ET.SubElement(curBr, "uncertaintyModel", {}) # cUncMod -> current uncertaintyModel
                    cUncMod.text = z.uncertaintyModel

                    cUncWei = ET.SubElement(curBr, "uncertaintyWeight", {}) # cUncWeight -> current uncertaintyWeight
                    cUncWei.text=z.uncertaintyWeight
        elif logicTreeObj.file_type == "GMPE":
            for a,b in v.branchSetList.items():
                curBs = ET.SubElement(curBl, "logicTreeBranchSet", {"uncertaintyType": b.uncertaintyType,"branchSetID": b.realBsId,"applyToTectonicRegionType":b.applyToTectonicRegionType}) # curBs -> current branchset.
                for x,z in b.branchList.items():
                    curBr = ET.SubElement(curBs, "logicTreeBranch", {"branchID": z.realBId}) # curBr -> current branch
                    cUncMod = ET.SubElement(curBr, "uncertaintyModel", {"gmpe_table":z.GMPETable}) # cUncMod -> current uncertaintyModel
                    cUncMod.text = "GMPETable"
                    cUncWei = ET.SubElement(curBr, "uncertaintyWeight", {}) # cUncWeight -> current uncertaintyWeight
                    cUncWei.text=z.uncertaintyWeight
    product = ET.tostring(root)
    product=str(product)
    product = product[2:len(product)-1]
    xml1 = xml.dom.minidom.parseString(product)
    finished_product = xml1.toprettyxml(indent='  ')
    return finished_product

######### EXECUTION
if __name__ == "__main__":
    args = getopts(sys.argv) #get possible arguments
    if len(args) == 0: #check if there are arguments
        #use preset
        preset="gmpe" #smlt or gmpe
        if preset=="smlt":
            lt = logicTreeC
            bl = lt.addBranchingLevel()
            bs = bl.addBranchSet()
            b1 = bs.addBranch(realBId="b1",uncertaintyModel="../../../sources/collapsed/eastern_arctic/EasternActic_H_Model_collapsed_rates.xml",uncertaintyWeight="0.6")
            b2 = bs.addBranch(uncertaintyModel="../../../sources/collapsed/eastern_arctic/EasternActic_R_Model_collapsed_rates.xml",uncertaintyWeight="0.4")
        elif preset=="gmpe":
            lt = logicTreeC(file_type="GMPE")
            bl1 = lt.addBranchingLevel()
            bs1 = bl1.addBranchSet(applyToTectonicRegionType="Active Shallow Fault")
            b1 = bs1.addBranch(GMPETable="../gm_tables/WcrustFRjb_low_clC.hdf5",uncertaintyWeight="0.2")
            b2 = bs1.addBranch(GMPETable="../gm_tables/WcrustFRjb_med_clC.hdf5",uncertaintyWeight="0.5")
            b3 = bs1.addBranch(GMPETable="../gm_tables/WcrustFRjb_high_clC.hdf5",uncertaintyWeight="0.3")


        lt.debugPrint()
        result=str(createXML(lt,prettyPrint=True))
        pyperclip.copy(result)
        print("\nCoppied to clipboard :)\n")
        print(result)
    else: #if no arguments, then
        ltData1 = json.loads(args['-ltd'])
        print(ltData1)
