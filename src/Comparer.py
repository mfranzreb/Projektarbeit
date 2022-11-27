import numpy as np


class Comparer:

    def __init__(self, testcase, sim_data, parameters, analytical_sol_data, experimental_sol_data):
        self.testcase = testcase
        self.sim_data = sim_data
        self.parameters = parameters
        self.analytical_sol_data = analytical_sol_data
        self.experimental_sol_data = experimental_sol_data

        self.sol_data = None

        # for now! needs replacement when both analytical and experimental data
        # check if analytical or experimental data is None!
        if analytical_sol_data is None:
            print("analytical_sol_data is None")
        elif analytical_sol_data is not None:
            self.sol_data = analytical_sol_data

        if experimental_sol_data is None:
            print("experimental_sol_data is None")
        elif experimental_sol_data is not None:
            self.sol_data = experimental_sol_data


        print("\n____________________________________________________\nCOMPARISON")
        
        self.output_dict_script = {}
        output_dict_key = {}
        abs_diff_dict = {}

        # calculate difference and add to dict:
        for script in self.sol_data:  # Level: Script
            for key, value in self.sol_data[script].items():  # Level: different probeLines
                # create NumPy arrays from data
                np_sol_points = np.asarray(value)
                np_sim_points = np.asarray(self.sim_data[key])
                # jump zero-size arrays
                if not np.any(np_sol_points):
                    print(f"Array for script {script} and key {key} has not enough indices for array! Array is skipped.")
                    continue
                else:
                    # calc difference
                    abs_diff_dict[key] = self.calc_abs_difference(np_sol_points, np_sim_points)
                    # calc custom functions for the user output
                    max_diff_array = self.max_diff(abs_diff_dict[key])
                    min_diff_array = self.min_diff(abs_diff_dict[key])
                    average_diff_array = self.average_diff(abs_diff_dict[key])
                    # add all results for the script to a dict with key
                    output_dict_key[key] = max_diff_array, min_diff_array, average_diff_array
            # add all results for the script to a dict with script
            self.output_dict_script[script] = output_dict_key

    def calc_abs_difference(self, sol_points, sim_points):
        # calc diff for all parameters (slice coords on column 0,1,2)
        abs_diff_array = np.absolute(sol_points[:, 3:] - sim_points[:, 3:])
        return abs_diff_array

    def max_diff(self, diff_array):
        key = "max"
        max_diff = diff_array.max(axis=0)
        return key, max_diff

    def min_diff(self, diff_array):
        key = "min"
        min_diff = diff_array.min(axis=0)
        return key, min_diff

    def average_diff(self, diff_array):
        key = "average"
        average_diff = diff_array.sum(axis=0) / len(diff_array)
        return key, average_diff

    # TODO: more custom functions can be added
