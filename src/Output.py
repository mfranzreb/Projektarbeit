class Output:

    def __init__(self, output_dict, test_setup, testcase_setup):
        self.output_dict = output_dict
        self.test_setup = test_setup
        self.testcase_setup = testcase_setup

        print("\n____________________________________________________\nOUTPUT")
                            
        for testcase in output_dict:
            parameters = testcase_setup[testcase].parsed_str["parameters"]["parameters"]
            for script in output_dict[testcase]:
                for key in output_dict[testcase][script]:
                    print(f"\nOutput for testcase {testcase}, script {script} and key {key}:")
                    for result in output_dict[testcase][script][key]:

                        # Output max diff
                        if test_setup["output"]["max_diff"] and result[0] == "max":
                            i = 0
                            for parameter in parameters:
                                print(f"Max diff for {parameter} is {result[1][i]}")
                                i += 1

                        # Output min diff
                        if test_setup["output"]["min_diff"] and result[0] == "min":
                            i = 0
                            for parameter in parameters:
                                print(f"Min diff for {parameter} is {result[1][i]}")
                                i += 1

                        # Output average diff
                        if test_setup["output"]["average_diff"] and result[0] == "average":
                            i = 0
                            for parameter in parameters:
                                print(f"Average diff for {parameter} is {result[1][i]}")
                                i += 1
