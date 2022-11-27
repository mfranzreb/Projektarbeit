import toml


class TestConfig:
    def __init__(self, setuptoml_path):
        self.test_setup_path = setuptoml_path
        with setuptoml_path.open() as setup_toml:
            self.parsed_test_setup = toml.load(setup_toml)
