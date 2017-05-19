#!/usr/bin/env python
'''
    GMAT_ITERATOR_v1.1
    Authors: Michael Rinehart
             Neil Eelman
    Date last revised : 19 May 2017

    Purpose: Reads a GMAT script from the same directory, and
    iteratively runs GMAT using temp scripts with modified
    variables.

    NOTE: For now, filepath cannot include a space

    Effects: Outputs summary data in a .csv file.
'''

import subprocess
import numpy
import os
import platform


def run():
    # OS-aware code to get path of GMAT and relevant files required to run GMAT.
    user_platform = platform.system()
    cwd = os.getcwd()
    current_user = os.getlogin()
    if (user_platform == "Windows"):
        gmat_location = "C:\\Users\\" + current_user + "\\AppData\\Local\GMAT\\R2016a\\bin\\GMAT.exe"
        temp_script_file_name = cwd + "\\temp.script"
        script_file_name = cwd + "\\"
    else: # GMAT is required to be in the user's PATH if not on Windows
        gmat_location = "gmat"
        temp_script_file_name = cwd + "/temp.script"
        script_file_name = cwd

    script_file_name += input("Please enter a file name: ")
    filenameparam = input("Please enter the name of the file parameter you want to modify: ") # EarthData.Filename
    thrustparam = input("Please enter the thrust parameter you want to modify: ") # EngineEarth.ConstantThrust
    start_variable = float(input("Please enter start value: "))
    end_variable = float(input("Please enter end value: "))
    step = float(input("Please enter step value: "))

    # GMAT data goes in subfolder escape_data, should folder not exist we'll create it
    output_file = cwd + "\\escape_data\\"
    if not os.path.isdir(output_file):
        os.makedirs(output_file)
    output_file += "escape_data"
    print("GMAT Runner Script v 1.1")
    filecounter = 1

    with open(script_file_name) as template_script_io:
        script_text = template_script_io.read()
    output_summary_io = open(output_file + ".csv", "w")

    for loopcounter in list(numpy.arange(start_variable, end_variable + step, step)):
        script_text = update_parameters(script_text, thrustparam, loopcounter)
        script_text = update_parameters(script_text, filenameparam, "'" + output_file + str(filecounter) + ".txt'")

        with open(temp_script_file_name, "w") as running_script_io:
            running_script_io.write(script_text)

        run_gmat(temp_script_file_name, gmat_location, loopcounter)
        filecounter += 1

    for file in range(1, filecounter):
        with open(output_file + str(file) + ".txt", 'r') as fh:
            if file == 1:
                first = fh.readline()
                data = ','.join(first.split()) + '\n'
                output_summary_io.write(data)

            for last in fh:
                pass
            data = ','.join(last.split()) + '\n'
            output_summary_io.write(data)

    output_summary_io.close()
    os.remove(temp_script_file_name)


def main():
    run()


# Looks in string <content> for <param>, and updates it's value to <param_value>
# Returns modified string
def update_parameters(content, param, param_value):
    pos = content.find(param)
    if (pos <= 0):
        print("ERROR: Invalid GMAT script file: unable to find parameter")
    pos2 = content.find(";", pos)
    if (pos <= 0):
        print("Error: Invalid GMAT script file: line not terminated with ;")
    return (content[:pos] + param + " = " + str(param_value) + content[pos2:])


# Runs GMAT with the script location and the iteration name
# Prints status to terminal.
def run_gmat(file_name, GMAT, iteration):
    print("Running GMAT with iteration #" + str(iteration) + file_name)
    subprocess.call(GMAT + " --run --exit --minimize " + file_name)

if __name__ == "__main__":
    main()
