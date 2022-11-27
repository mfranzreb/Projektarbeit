import logging
from pathlib import Path

from simulator import simulator
from Solution import AnalyticalSolution
from Solution import ExperimentalSolution
from TestRoot import TestRoot
from Comparer import Comparer
from Output import Output
from InputReader import inputReader


TEST_PATH = Path("/home/marcof/scratch/PA")


class TestExecutor:

    def __init__(self, console_testcase=None):
        # members
        self.test_root = None
        self.solution = None
        self.sim = None
        self.comparison = None
        self.output = None

        # variables
        self.output_dict = {}

        # setup test
        self._create_testroot(console_testcase)
        self.test_setup = self.test_root.test_config.parsed_test_setup
        

        # iterate over all testcases individually for simulation, solution and comparison
        for testcase in self.test_root.testcase_configs:
            self.testcase_setup = self.test_root.testcase_configs[testcase]

            #check if solution is ANALYTICAL: simulate first, create solution later
            if self.get_test_analytical_bool() and self.get_testcase_analytical_bool():
                logging.info(f"Testsetup requests analytical solution and testcase {testcase} has analytical solution.")
                logging.info(f"Running simulation for {testcase}.")
                if self._run_simulation(testcase) is True:
                    continue
                logging.info(f"Creating analytical solution for {testcase}.")
                self._run_analytical_solution(testcase)
            elif not self.get_test_analytical_bool():
                logging.info("Testsetup does not request analytical solution.")

            # TODO: Problem if testcase has analytical and experimental solution... Testcase is simulated twice.!!!!!!
            # check if solution is EXPERIMENTAL: get solution data first, simulate later
            if self.get_test_experimental_bool() and self.get_testcase_experimental_bool():
                logging.info(f"Testsetup requests experimental solution and testcase {testcase} has experimental solution.")
                logging.info(f"Getting experimental data for testcase {testcase}.")
                self.csv_file = self._read_CSV_file(testcase)
                if self.csv_file.wanted_exp_vars is None:
                    continue
                self._run_experimental_solution(testcase)#Make testaces_path once and give it to the functions?
                logging.info(f"Running simulation for {testcase}.")
                if self._run_simulation(testcase) is True:#SHould continue with other loops or stop the whole code?
                    continue
            elif not self.get_test_experimental_bool():
                logging.info("Testsetup does not requests experimental solution.")

            self.output_dict[testcase] = self._run_comparison(testcase)
        # create final output for user
        self._create_output()


    def _create_testroot(self, console_testcase):
        """Setup general test config and all testcases."""
        self.test_root = TestRoot(TEST_PATH, console_testcase)

    def get_test_analytical_bool(self):
        """Check test_setup.toml if analytical solution type is requested."""
        test_analytical = self.test_setup["solutionType"]["analytical"]
        return test_analytical

    def get_test_experimental_bool(self):
        """Check test_setup.toml if experimental solution type is requested."""
        test_experimental = self.test_setup["solutionType"]["experimental"]
        return test_experimental

    def get_testcase_analytical_bool(self):
        """Check if analytical solution is available for given testcase."""
        testcase_analytical = self.testcase_setup.parsed_str["solution"]["analytical"]
        return testcase_analytical

    def get_testcase_experimental_bool(self):
        """Check if analytical solution is available for given testcase."""
        testcase_experimental = self.testcase_setup.parsed_str["solution"]["experimental"]
        return testcase_experimental

    def _read_CSV_file(self, testcase):
        config = self.test_root.testcase_configs[testcase]
        csv_filename = config.parsed_str["solution"]["solutionscript"]
        wanted_vars = config.parsed_str["parameters"]["parameters"]
        testcase_path = Path(self.test_root.testcase_configs[testcase].testcase_path)
        csv_file = inputReader(testcase_path, csv_filename, wanted_vars)
        return csv_file

    def _run_simulation(self, testcase):
        """Runs m-AIA with current testcase."""
        sim_path = Path(self.test_root.testcase_configs[testcase].testcase_path)
        config = self.test_root.testcase_configs[testcase]
        try:
            self.csv_file

        except AttributeError:
            self.sim = simulator(sim_path, config)
            if self.sim.points is None:
                print("error")
                return True

        else:
            self.sim = simulator(sim_path, config, self.csv_file)
            if self.sim.points is None:
                print("error")
                return True

    def _run_analytical_solution(self, testcase):
        variables = self.sim.points
        self.analyticalsolution = AnalyticalSolution(testcase, self.test_setup, self.testcase_setup, variables)

    def _run_experimental_solution(self, testcase):
        #config = self.test_root.testcase_configs[testcase]
        testcase_path = Path(self.test_root.testcase_configs[testcase].testcase_path)
        csv_file = self.csv_file
        self.experimentalsolution = ExperimentalSolution(testcase_path, csv_file)

    # TODO: change sol data for ex or an solution. If loop? problem: both exp and ana
    # default None value in Comparer(...=None) not working.
    def _run_comparison(self, testcase):
        """Compares simulation and solution data for each testcase."""
        sim_data = self.sim.points
        analytical_sol_data = None  # temporary fix
        experimental_sol_data = None
        if self.get_testcase_analytical_bool():
            analytical_sol_data = self.analyticalsolution.solution 
        elif self.get_testcase_experimental_bool():
            experimental_sol_data = self.experimentalsolution.solution  # Attribute not yet existing
        parameters = self.test_root.testcase_configs[testcase].parsed_str["parameters"]["parameters"]
        self.comparison = Comparer(testcase, sim_data, parameters, analytical_sol_data, experimental_sol_data)
        return self.comparison.output_dict_script

    def _create_output(self):
        """Creates final output for user"""
        test_setup = self.test_root.test_config.parsed_test_setup
        testcase_setup = self.test_root.testcase_configs
        self.output = Output(self.output_dict, test_setup, testcase_setup)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_executor = TestExecutor()
