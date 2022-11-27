import os
from os.path import basename
from pathlib import Path
from TestConfig import TestConfig
from TestcaseConfig import TestcaseConfig


class TestRoot:

    def __init__(self, path, console_testcase):  # init TestConfig object and Testcases
        self.console_testcase = console_testcase
        self.path = path
        self._load_test_config()
        self._find_cases(console_testcase)

    def _load_test_config(self):
        """Read test setup toml and create TestConfig."""
        setup_toml_path = self.path / "test_setup.toml"
        self.test_config = TestConfig(setup_toml_path)

    def _find_cases(self, console_testcase):
        """Searches subdirectories for eligible testcases or uses testcase from console."""
        self.testcase_configs = {}
        if console_testcase is None:
            all_testcases = self.test_config.parsed_test_setup["general"]["all_testcases"]
            testcases = self.test_config.parsed_test_setup["general"]["testcases"]
            for dirpath, dirnames, filenames in os.walk(self.path):
                testname = basename(dirpath)
                if TestcaseConfig.CONFIG_FILENAME in filenames and (all_testcases or testname in testcases):
                    print(f'Adding testcase "{testname}" at {dirpath}')
                    self.testcase_configs[testname] = TestcaseConfig(Path(dirpath), testname)
            if not self.testcase_configs:
                print("No testcases in test_setup.toml found. testcase_configs is empty.")
        else:
            for dirpath, dirnames, filenames in os.walk(self.path):
                testname = basename(dirpath)
                if TestcaseConfig.CONFIG_FILENAME in filenames and (testname == console_testcase):
                    print(f'Adding testcase "{testname}" at {dirpath}')
                    self.testcase_configs[testname] = TestcaseConfig(Path(dirpath), testname)
            if not self.testcase_configs:
                print(f'{console_testcase} not found. testcase_configs is empty.')
