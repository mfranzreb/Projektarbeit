import os
import subprocess
import re
import numpy as np
import netCDF4 as nc
import toml
import logging
import traceback


class Simulator:

    def __init__(self, path_to_testcase, config, csv_file = None):
        self.path_to_testcase = path_to_testcase
        self.points = None
        self.csv_file = csv_file

        print("\n____________________________________________________\nSIMULATOR")

        error = None#self.grid(path_to_testcase)
        if error is None:
            error = None#self.sim(path_to_testcase)
        if error is None:
            self.points = self.getDP(path_to_testcase, config)

    def grid(self, path_to_testcase):

        os.chdir(path_to_testcase)

        cmd1 = subprocess.Popen("mpirun -np 12 ./maia properties_grid.toml", shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, encoding="utf-8")
        retval = cmd1.wait()
        stdout, stderr = cmd1.communicate()

        # To show output in terminal
        #    for line in cmd1.stdout.readlines():
        #       print(line)
        if cmd1.returncode != 0:
            print("grid of " + str(path_to_testcase).split("/")[-1] + " has failed:" + "\n" + stderr)
            return True

    def sim(self, path_to_testcase):
        os.chdir(path_to_testcase)

        cmd2 = subprocess.Popen("mpirun -np 12 ./maia properties_run.toml", shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, encoding="utf-8")
        
        retval = cmd2.wait()
        stdout, stderr = cmd2.communicate()
        if cmd2.returncode != 0:
            print("sim of " + str(path_to_testcase).split("/")[-1] + " has failed:" + "\n" + stderr)
            return True

    def getDP(self, path_to_testcase, config):

        self.path_to_testcase = path_to_testcase
        prop_run_path = path_to_testcase / "properties_run.toml"

        probe_file = None
        if config.parsed_str["solution"]["analytical"]:
            probe_file = config.parsed_str["parameters"]["probeFile"]

        wanted_vars = config.parsed_str["parameters"]["parameters"]

        os.chdir(path_to_testcase)
        try:
            with prop_run_path.open() as f:
                pp_filePath = toml.load(f)["pp_fileName"]

            pp_file = pp_filePath.split("/")[-1]
            pp_path = path_to_testcase / "/".join(pp_filePath.split("/")[:-1])

        except KeyError:
            pp_file = config.parsed_str["parameters"]["simFile"]
            pp_path = out = path_to_testcase / "out"

        simu = nc.Dataset(pp_path / pp_file).variables
        sim_vars = {}
        var_number_to_name = {}
        i = 0
        for key in simu.keys():
            if "name" not in simu[key].ncattrs():
                continue
            if "variable" in key:
                for attr in simu[key].ncattrs():
                    sim_vars[key] = simu[key].getncattr(attr)

            elif key in wanted_vars:
                for attr in simu[key].ncattrs():
                    sim_vars["variables{}".format(i)] = simu[key].getncattr(attr)
            i +=1

        already_printed = []
        for var in wanted_vars:
            for key in sim_vars:
                if var == sim_vars[key]:
                    var_number_to_name[key] = sim_vars[key]
                    break
                elif var not in list(sim_vars.values()) and var not in already_printed:
                    print("ERROR: Variable: " + var + " has not been simulated, please remove it from the testcase_parameters.toml file")
                    already_printed.append(var)
                    return None

        print('Selected variables:', ', '.join(var_number_to_name[key] for key in var_number_to_name))

        if config.parsed_str["solution"]["analytical"]:
            if "Line" in probe_file:
                points = self._get_line_DP(prop_run_path, path_to_testcase, var_number_to_name, probe_file)
                return points

        if config.parsed_str["solution"]["experimental"]:
            points = self._get_points_DP(prop_run_path, path_to_testcase, var_number_to_name, self.csv_file)
            return points

    def _get_line_DP(self, prop_run_path, path_to_testcase, var_number_to_name, probe_file):

        with prop_run_path.open() as f:
            lines = toml.load(f)["pp_probeLineDirection"]
        with prop_run_path.open() as f:
            lines_coords = toml.load(f)["pp_probeLineCoordinates"]
        with prop_run_path.open() as f:
            nDim = toml.load(f)["nDim"]

        out = path_to_testcase / "out"
        os.chdir(out)
    
        path_to_probe = out / probe_file
        data = nc.Dataset(path_to_probe)

        points = {}
        line_ids = [i[0] for i in enumerate(lines)]
        for key in var_number_to_name:
            for k in data.variables.keys():
                if k.endswith("coordinates"):
                    for line in lines:
                        for lineId in line_ids:
                            if lines[int(lineId)] == line and str(lineId) in k and nDim == 3:
                                if line == 0:
                                    x_coords = data.variables[k][:]
                                    y_coords = lines_coords[2 * int(lineId)]
                                    z_coords = lines_coords[2 * int(lineId) + 1]
                                    points["points_{}".format(lineId)] = [[coord, y_coords, z_coords] for coord in x_coords]
                                elif line == 1:
                                    x_coords = lines_coords[2 * int(lineId)]
                                    y_coords = data.variables[k][:]
                                    z_coords = lines_coords[2 * int(lineId) + 1]
                                    points["points_{}".format(lineId)] = [[x_coords, coord, z_coords] for coord in y_coords]
                                elif line == 2:
                                    x_coords = lines_coords[2 * int(lineId)]
                                    y_coords = lines_coords[2 * int(lineId) + 1]
                                    z_coords = data.variables[k][:]
                                    points["points_{}".format(lineId)] = [[x_coords, y_coords, coord] for coord in z_coords]

                            elif lines[int(lineId)] == line and str(lineId) in k and nDim == 2:
                                if line == 0:
                                    x_coords = data.variables[k][:]
                                    y_coords = lines_coords[int(lineId)]
                                    points["points_{}".format(lineId)] = [[coord, y_coords] for coord in x_coords]
                                elif line == 1:
                                    x_coords = lines_coords[int(lineId)]
                                    y_coords = data.variables[k][:]
                                    points["points_{}".format(lineId)] = [[x_coords, coord] for coord in y_coords]

        for key in var_number_to_name:
            for k in data.variables.keys():
                if key.endswith(str(k)[-1]):
                    var = data.variables[k][:]
                    for i in enumerate(var):
                        points["points_{}".format(data.variables[k].getncattr("lineId"))][i[0]].append(var[i[0]])
        return points

    def _get_points_DP(self, prop_run_path, path_to_testcase, var_number_to_name, csv_file):
        try:
            with prop_run_path.open() as f:
                probe_path = toml.load(f)["pp_probePath"]

            with prop_run_path.open() as f:
                nDim = toml.load(f)["nDim"]
            with prop_run_path.open() as f:
                num_files = int(len(toml.load(f)["pp_probeCoordinates"])/nDim)

            os.chdir(path_to_testcase)
            os.chdir(probe_path)

            probe_file_numbers = []
            probe_files = []

            for dirpath, dirnames, filenames in os.walk(path_to_testcase / probe_path):
                for file in filenames:
                    m = re.match("probe_([0-9]+).dat", file)
                    if m:
                        probe_files.append(file)
                        probe_file_numbers.append(int(m.group(1)))


            if not probe_file_numbers:
                print("ERROR: No point/s have been processed, please fix or remove the point/s")
                for name in probe_files:
                    os.remove(name) 
                return None
            if len(probe_file_numbers) != num_files:
                for num in range(num_files):
                    for file in probe_file_numbers:
                        if file == num:
                            break
                    else:
                        print("ERROR: Point " + str(num) + " has not been processed, please fix or remove the point")

                for name in probe_files:
                    os.remove(name)
                return None

            sorted_probe_files = []
            for i in range(num_files):
                for file in probe_files:
                    if file == "probe_{}.dat".format(i):
                        sorted_probe_files.append(file)
                        break

            points = {}
            points["coordinates"] = []
            coords = np.array(csv_file.coords)
            for coord, file in zip(coords, sorted_probe_files):
                sim_coords = []
                with open(file, "r") as f:
                    probe_file = f.read()
                    probe_file_lines = probe_file.split("\n")
                for index, elem in reversed(list(enumerate(probe_file_lines))):
                    if not elem:
                        probe_file_lines.pop(index)
                    else:
                        break
                for line in probe_file_lines:
                    single_coord = []
                    if "%" in line:
                        for word in line.split(" "):
                            x = re.search(r"\(([0-9.-]+)\)", word)
                            if x != None:
                                single_coord.append(float(x.group(1)))
                        if single_coord:
                            sim_coords.append(np.array(single_coord))
                dist = []
                for c in sim_coords:
                    dist.append(np.sum((c-coord)**2, axis=0))
                    
                chosen_coord_index = dist.index(min(dist))
                chosen_coord = list(map(float, sim_coords[chosen_coord_index]))

                sim_vars = probe_file_lines[-len(dist)+chosen_coord_index].split(" ")[2:]
                
                for index, elem in reversed(list(enumerate(sim_vars))):    
                    try:
                        float(elem)
                        sim_vars = list(map(float, sim_vars[:index+1]))
                        break
                    except ValueError:
                        continue

                for i, e in reversed(list(enumerate(sim_vars))):
                    for key, value in var_number_to_name.items():
                        if key.endswith(str(i)):
                            break
                    else:                  
                        sim_vars.pop(i)
                print(str(sim_vars))
                points["coordinates"].append(chosen_coord+sim_vars)

            for file in probe_files:
                os.remove(file)
            return points

        except Exception:
            os.chdir(path_to_testcase)
            os.chdir(probe_path)

            for dirpath, dirnames, filenames in os.walk(path_to_testcase / probe_path):
                for file in filenames:
                    if "probe_" in file and ".dat" in file:
                        os.remove(file)
            logging.error(traceback.format_exc())
