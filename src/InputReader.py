import csv
import os
import numpy as np
from copy import deepcopy
import toml


class inputReader:

    def __init__(self, testcase_path, filename, wanted_vars):
        self.testcase_path = testcase_path
        self.filename = filename
        self.filepath = testcase_path / filename
        self.wanted_vars = wanted_vars
        with open(self.filepath, newline = '') as f:
            self.csv_file = csv.reader(f, delimiter=',')
            
            self.vars = self._get_vars(self.csv_file)
            self.coords = self._get_coords(self.vars)
            f.seek(0)
            self.var_names = self._get_var_names(self.csv_file)
            f.seek(0)
            self.wanted_exp_vars = self._get_wanted_exp_vars(self.csv_file, f, self.wanted_vars)


    def _get_vars(self, csv_file):#maybe not needed
        exp_vars = []
        next(csv_file)
        for row in csv_file:
            exp_vars.append(row)
        #vars = [np.float_(i) for i in exp_vars]
        vars = [list(map(float, i)) for i in exp_vars]
        return vars

    def _get_coords(self, vars):#TODO: also for 2d coords
        prop_run_path = self.testcase_path / "properties_run.toml"
        with prop_run_path.open() as f:
            nDim = toml.load(f)["nDim"]
        coords = []
        for var in vars:
            coords.append(var[:nDim])

        #np_coords = np.array(coords)
        return coords

    def _get_wanted_exp_vars(self, csv_file, f, wanted_vars):
        exp_vars = deepcopy(self.coords)
        var_names = self.var_names

        for var in wanted_vars: #Assumed that variable names are the same in csv file and toml file
            i = 0       
            f.seek(0)
            for v in var_names:

                if var == v:
                    i = var_names.index(v)
                    break

            if i == 0:#Is this check necessary? Will always all variables be compared?
                print("Variable " + var + " is not in the experimental solution" + "\n")
                return None

            next(csv_file)

            for coord in exp_vars:
                coord.append(float(next(csv_file)[i]))
            
        return exp_vars



    def _get_var_names(self, csv_file):
        var_names = next(csv_file)
        return var_names