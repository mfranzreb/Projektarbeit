from os.path import join
#from typing import Final

import toml


class TestcaseConfig:
    CONFIG_FILENAME= "testcase_parameters.toml"#: Final = 'testcase_parameters.toml'

    def __init__(self, testcase_path, testcase_name):
        self.testcase_path = testcase_path
        parameters_path = join(testcase_path, self.CONFIG_FILENAME)
        with open(parameters_path) as f:
            self.parsed_str = toml.load(f)
            self.name = testcase_name
