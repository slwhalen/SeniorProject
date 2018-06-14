###################################################################
# Original code by GitHub user joskvi
# Additions by Sean Whalen
# Last edit: Jun 13, 2018
###################################################################
from subprocess import call
import os
from tempfile import mkstemp
from shutil import move
import numpy as np

import config


# ----------- Simulation controls ----------- #

def run_simulations(parameter_set=None, numerical_name_start=0):

    # Set appropriate variables according to the argument of parameter_set
    if parameter_set is not None:
        parameter = parameter_set[0]
        parameter_value_list = parameter_set[1]
        use_default_parameters = False
    else:
        use_default_parameters = True

    # Specify file paths
    file_path = config.LTSpice_asc_filename[:-4] # Use .asc file specified in config, but remove file ending
    file_path_generated = file_path + '_generated'
    spice_exe_path = config.LTSpice_executable_path

    # Create a list of the generated files
    output_filenames = []

    if not use_default_parameters:
        # Run a simulation for each parameter value in the parameter set
        for i, parameter_value in enumerate(parameter_value_list):
            # Set specified parameters
            if config.output_data_naming_convention == 'number':
                file_num = str(i + numerical_name_start)
                output_name = '0'*(3-len(file_num)) + file_num
                output_path = config.output_data_path + output_name + '.txt'
                print ("output path = "+output_path)
            else:
                output_path = config.output_data_path + parameter + '=' + str(parameter_value) + '.txt'
            output_filenames.append(output_path)
            print ("setting parameters with: "+ file_path + '.asc' + " " + parameter + " "+parameter_value)
            set_parameters(file_path + '.asc', parameter, parameter_value)
            print('Starting simulation with the specified parameter: ' + parameter + '=' + str(parameter_value))
            # Run simulation
            simulate(spice_exe_path, file_path_generated)

            # Set header and cleanup the file
            output_header = 'SPICE simulation result. Parameters: ' + ', '.join(get_parameters(file_path_generated + '.asc')) + '\n' # Maybe not add the time variables
            rett = clean_raw_file(spice_exe_path, file_path_generated, output_path, output_header)
        biasVoltTwo = float(get_parameters(file_path + '_generated.asc')[1][4:])
        biasVoltage = float (get_parameters(file_path + '_generated.asc')[0][3:])
    else:
        # Run a simulation with the preset values of the file
        output_path = config.output_data_path + 'result.txt'
        simulate(spice_exe_path, file_path)
        print ("past sim")
        # Set header and cleanup the file
        output_header = 'SPICE simulation result. Parameters: ' + ', '.join(get_parameters(file_path + '.asc')) + '\n' # Maybe not add the time variables
        print ("Before difference")
        biasVoltage = float (get_parameters(file_path + '.asc')[0][3:])
        biasVoltTwo = float(get_parameters(file_path + '.asc')[1][4:])
        maximumDiff = 0
        rett = clean_raw_file(spice_exe_path, file_path, output_path, output_header)
    #print ("The maximum difference is " + str(maximumDiff))
    #print ("The bias voltage is "+ str(biasVoltage))
    #print ("The second bias voltage is " + str(biasVoltTwo))

    # Return the max output difference and according difference in input
    return [rett[0], rett[1]] 

def simulate(spice_exe_path, file_path):
    file_name = str(file_path.split('\\')[-1])
    print('Simulation starting: ' + file_name + '.asc')
    call('"' + spice_exe_path + '" -netlist "' + file_path + '.asc"', shell=True)
    #print('"' + spice_exe_path + '" -b -ascii "' + file_path + '.net"')
    call('"' + spice_exe_path + '" -b -ascii "' + file_path + '.net"', shell=True)
    size = os.path.getsize(file_path + '.raw')
    print('Simulation finished: ' + file_name + '.raw created (' + str(size/1000) + ' kB)')

def clean_raw_file(spice_exe_path, file_path, output_path, output_header):
    prev = -55.0
    max = 0
    # Try to open the requested file
    file_name = file_path
    try:
        f = open(file_path + '.raw', 'r')
    except IOError:
        # If the requested raw file is not found, simulations will be run,
        # assuming a that a corresponding LTspice schematic exists
        print('File not found: ' + file_name + '.raw')
        simulate(spice_exe_path, file_path)
        f = open(file_path + '.raw', 'r')

    #print('Cleaning up file: ' + file_name + '.raw')

    max_in = 0
    prev_in = 0
    reading_header = True
    data = []
    data_line = []

    for line_num, line in enumerate(f):

        if reading_header:
            if line_num == 4:
                # Number of Vars = # different measurables on schematic
                number_of_vars = int(line.split(' ')[-1])
                #print (number_of_vars)
            if line_num == 5:
                # Number of Points = # time measurements and data on each measurable
                number_of_points = int(line.split(' ')[-1])
                #print (number_of_points)
            if line[:7] == 'Values:':
                # It reads "Values:" in the RAW file, and data begins after this
                # So line_num and line refer to where data start
                reading_header = False
                header_length = line_num + 1
                continue
        else:
            # This runs after getting the header information
            # Gets the data for each parameter specified in config.py
            # Stores the max value of the file for 
            data_line_num = (line_num - header_length) % number_of_vars
            if data_line_num in config.variable_numbering.values():
                data_line.append(line.split('\t')[-1].split('\n')[0])
            if data_line_num == number_of_vars - 1:
                if (prev != -55.0) and (max < abs(prev - float(data_line[2]))):
                    max = abs(prev - float(data_line[2]))
                    max_in = abs(prev_in - float(data_line[1]))
                # print (max)
                data.append(data_line)
                prev = float(data_line[2])
                prev_in = float(data_line[1])
                data_line = []

    f.close()

    # Rearrange data
    variables = sorted(config.variable_numbering, key=config.variable_numbering.__getitem__)
    #print ("variables = "+variables[0]+" "+variables[1]+" "+variables[2])
    variables = np.array(variables)[config.preffered_sorting].tolist()
    #print ("variables = "+variables[0]+" "+variables[1]+" "+variables[2])
    data = np.array(data)[:, config.preffered_sorting]

    # Write data to file
    try:
        f = open(output_path, 'w+')
    except IOError:
        print('\nThe path specified for saving output data, \'' + config.output_data_path + '\', doesn\'t appear to exist.\nPlease check if the filepath set in \'config.py\' is correct.')
        exit(0)
    f.write(output_header)
    f.write('\t'.join(variables) + '\n')
    #print("Variables are: " + '\t'.join(variables))
    for line in data:
        f.write('\t'.join(line) + '\n')
    f.close()

    size = os.path.getsize(output_path)
    #print('CSV file created: ' + output_path + ' (' + str(size/1000) + ' kB)')
    return [max_in, max]


# ----------- Parameter controls ----------- #

def parse_parameter_file(filename):

    cmd_list = []
    param_file = open(filename, 'r')

    for line in param_file:
        line = line.split()
        if len(line) == 0:
            continue
        try:
            cmd = line[0]
            if cmd[0] == '#':
                continue
            elif cmd.lower() == 'set':
                parameter = line[1]
                value = line[2]
                cmd_list.append(('s', parameter, value))
            elif cmd.lower() == 'run':
                parameter = line[1]
                values = line[2:]
                cmd_list.append(('r', parameter, values))
            else:
                return None # Syntax error
        except IndexError:
            return None # Syntax error

    return cmd_list

def set_parameters(file_path, param, param_val, overwrite=False):
    f, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                line_list = line.split(' ')
                if line_list[0] == 'TEXT':
                    for element_num, element in enumerate(line_list):
                        if element.split('=')[0] == param:
                            # Gets parameter ready to be added (eg. R=5000)
                            line_list[element_num] = param + '=' + str(param_val)
                    if line_list[-1][-1] != '\n':
                        line_list[-1] = line_list[-1] + '\n'
                    new_file.write(' '.join(line_list))
                else:
                    new_file.write(line)
    os.close(f)
    if overwrite:
        os.remove(file_path)
        move(abs_path, file_path)
    else:
        move(abs_path, file_path[:-4] + '_gen.asc')

def get_parameters(file_path):
    output_list = []
    f = open(file_path, 'r')
    for line in f:
        line_list = line.split()
        if line_list[0] == 'TEXT' and '!.param' in line_list:
            output_list.extend(line_list[line_list.index('!.param') + 1:])
    f.close()
    return output_list
