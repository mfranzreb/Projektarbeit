import importlib.util
import logging
import os.path
import sys
import numpy as np


class AnalyticalSolution:

    def __init__(self, testcase, test_setup, testcase_setup, variables):
        self.testcase = testcase
        self.test_setup = test_setup
        self.testcase_setup = testcase_setup
        self.variables = variables

        print("\n____________________________________________________\nANALYTICAL SOLUTION")

        self._create_analytical_solution(testcase)

    def _create_analytical_solution(self, testcase):
        """Get analytical solution if analytical solution is available and requested."""
        # access all solution scripts from testcase
        self.solution = {}
        for script in self.testcase_setup.parsed_str["solution"]["solutionscript"]:
            testcase_path = self.testcase_setup.testcase_path
            file_path = os.path.join(testcase_path, script)
            analytical_solution_module_name = "HansWurst"
            spec = importlib.util.spec_from_file_location(analytical_solution_module_name, file_path)
            analytical_solution_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(analytical_solution_module)

            # create analytical solution for script
            parameters = self.testcase_setup.parsed_str["parameters"]["parameters"]
            solution_object = analytical_solution_module.AnalyticalSolution(self.variables, parameters)
            self.solution[script] = getattr(solution_object, "solution")
            logging.info(f"Solution created for testcase {testcase} with script {script}.")


class ExperimentalSolution:

    def __init__(self, testcase_path, csv_file):#Difference between gving csv_file to the function and using it as self.?
        self.testcase_path = testcase_path
        self.csv_file = csv_file

        print("\n____________________________________________________\EXPERIMENTAL SOLUTION")
        self._get_data(testcase_path)

    def _get_data(self, testcase_path):
        """Load experimental data if experimental solution is available and requested."""
        prop_run_path = testcase_path / "properties_run.toml"

        self.solution = {}
        sol_data = {}
        sol_data["coordinates"] = self.csv_file.wanted_exp_vars
        self.solution[self.csv_file.filename] = sol_data

        coords = self.csv_file.coords
        replace_coords = np.array(coords).flatten().tolist()
        replace_string = "pp_probeCoordinates = " + str(replace_coords) + "\n"
        with open(prop_run_path, "r+") as f:
          read_data = f.readlines()

        for i in read_data:
            if "probeCoordinates" in i:
                replace_line = read_data.index(i)
                break

        read_data[replace_line] = replace_string

        with open(prop_run_path, 'w') as f:
            f.writelines(read_data)
