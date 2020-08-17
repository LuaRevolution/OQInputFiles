import configparser
import os

# setup
class configItem:
    def __init__(self,key,section,value=None):
        self.key = key
        self.section = section
        if value == None:
            self.value = ""
        else:
            self.value=value
    def __repr__():
        return "configItem (key:'{}')(section:'{}')(value:'{}')".format(self.key,self.section,self.value)
    def set(self,key,value):
        if key == "section":
            self.section = value
            if self.section == value:
                return True
            else:
                return False
        elif key == "value":
            self.value = value
            if self.value == value:
                return True
            else:
                return False
        elif key == "key":
            self.key = value
            if self.key == value:
                return True
            else:
                return False
class JobFile:
    def __init__(self,settings=None,file_path=None,auto_open=None):
        #--- setup ---
        self.settings = {
            #general
            "description": configItem("description","general"),
            "calculation_mode": configItem("calculation_mode","general"),
            "random_seed": configItem("random_seed","general"),

            #geometry
            "sites_csv": configItem("sites_csv","geometry"),

            #logic_tree
            "number_of_logic_tree_samples": configItem("number_of_logic_tree_samples","logic_tree"),

            #erf
            "rupture_mesh_spacing":configItem("rupture_mesh_spacing","erf"),
            "width_of_mfd_bin": configItem("width_of_mfd_bin","erf"),
            "area_source_discretization": configItem("area_source_discretization","erf"),

            #site_params
            "reference_vs30_type": configItem("reference_vs30_type","site_params"),
            "reference_vs30_value": configItem("reference_vs30_value","site_params"),
            "reference_depth_to_2pt5km_per_sec": configItem("reference_depth_to_2pt5km_per_sec","site_params"),
            "reference_depth_to_1pt0km_per_sec": configItem("reference_depth_to_1pt0km_per_sec","site_params"),

            #calculation
            "source_model_logic_tree_file": configItem("source_model_logic_tree_file","calculation"),
            "gmpe_logic_tree_file": configItem("gmpe_logic_tree_file","calculation"),
            "investigation_time": configItem("investigation_time","calculation"),
            "intensity_measure_types_and_levels": configItem("intensity_measure_types_and_levels","calculation"),
            "truncation_level": configItem("truncation_level","calculation"),
            "maximum_distance": configItem("maximum_distance","calculation"),

            #output
            "export_dir": configItem("export_dir","output"),
            "mean_hazard_curves": configItem("mean_hazard_curves","output"),
            "quantile_hazard_curves": configItem("quantile_hazard_curves","output"),
            "hazard_maps": configItem("hazard_maps","output"),
            "uniform_hazard_spectra": configItem("uniform_hazard_spectra","output"),
            "poes": configItem("poes","output")
        } # default table
        self.parser = configparser.ConfigParser()
        self.file_path = file_path
        self.set(settings)

        #default auto open
        if auto_open is None and file_path is not None:
            auto_open = True
        else:
            auto_open = False

        if self.file_path is not None and auto_open == True:
            self.open(file_path)
        else:
            self.sendToParser()
    def __del__(self):
        del self.parser
        del self
    def set(self,dict,type="value"):
        if dict is not None:
            for i,v in dict.copy().items():
                try:
                    option = self.settings[i]
                    option.set(type,v)
                except:
                    return False
        self.sendToParser()
    def open(self,file_path):
        del self.parser
        self.parser = configparser.ConfigParser()
        try:
            self.parser.read(file_path)
        except:
            print("File '{}' doesn't exist".format(file_path))
            return False
        for section in self.parser.sections():
            items = self.parser.items(section)
            for i,v in items:
                option = self.settings[i]
                option.set("value",v)
                option.set("section",section)
        return True
    def save(self,file_path=None):
        file = None
        if file_path == None:
            file_path = self.file_path
        try:
            file = open(file_path,"w")
        except FileNotFoundError:
            print("File doesn't exist")
            return("File doesn't exist")
        self.parser.write(file)
        file.close()
    def sendToParser(self,settings=None,newSections=True):
        if newSections==True:
            del self.parser
            self.parser = configparser.ConfigParser()
            self.parser.add_section("general") # General
            self.parser.add_section("geometry") # Geometry
            self.parser.add_section("logic_tree") # Logic_Tree
            self.parser.add_section("erf") # Erf
            self.parser.add_section("site_params") # Site_Params
            self.parser.add_section("calculation") # Calculation
            self.parser.add_section("output") #Output
        if settings == None:
            settings = self.settings
        for i,v in settings.items():
            self.parser.set(v.section,v.key,v.value)
if __name__ == "__main__":
    jf = JobFile(file_path="test.ini")
    for i,v in jf.settings.items():
        print(i+": "+v.value)
    jf.set({"poes":"test2"})
    for i,v in jf.settings.items():
        print(i+": "+v.value)
    jf.save()
