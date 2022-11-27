import math
import numpy as np
import sys
import toml


class AnalyticalSolutionScript:

    def __init__(self, variables, parameters, testcase_path = None):
        self.solution ={}
        F1BCS = 1.73205080756887729352
        prop_run_path = testcase_path / "properties_run.toml"
        with prop_run_path.open() as f:
            Ma = toml.load(f)["Ma"]
        # iterate over each point in line array
        for key, value in variables.items():
            point_solution = []
            for point in value:
                # Order: "x", "y", "z"
                self.x = point[0]
                self.y = point[1]
                self.z = point[2]

                # calc solution for point
                self.R1 = float(1)
                self.R2 = float(2)
                self.Omega1 = float(0)
                self.Omega2 = float(Ma/(self.R2*F1BCS))

                self.r = math.sqrt(self.x ** 2 + self.y ** 2)
                if self.x == 0.0:
                    self.eta = np.sign(self.y)*math.pi/2
                else:
                    self.eta = np.arctan2(self.y, self.x)
                self.v_eta = (self.Omega2 * self.R2 ** 2) / (self.R2 ** 2 - self.R1 ** 2) * self.r - (
                            self.Omega2 * self.R1 ** 2 * self.R2 ** 2) / ((self.R2 ** 2 - self.R1 ** 2) * self.r)
                self.u = -math.sin(self.eta) * self.v_eta
                self.v = math.cos(self.eta) * self.v_eta
                self.w = 0

                # create array with solution of point
                coords = point[:3]
                parameter_check = []
                parameter_check_bool = False
                for parameter in parameters:
                    try:
                        coords.append(getattr(self, parameter))
                        parameter_check.append(parameter)
                    except AttributeError as e:
                        parameter_check_bool = True
                        print(f"Parameter {parameter} is not available in the analytical Solutionscript!")
                if parameter_check_bool is True:
                    sys.exit("Analytical Solution failed.")
                else:
                    point_solution.append(coords)
                
            # add solution of point to solution array
            self.solution["points_{}".format(key[-1])] = point_solution  # SOL key is the same as SIM key.
            
