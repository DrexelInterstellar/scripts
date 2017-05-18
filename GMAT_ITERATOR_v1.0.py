#!/usr/bin/env python
'''
    GMAT_ITERATOR_v1.1
    Author: Michael Rinehart
    Date last revised : 18 May 2017
    Platform Created: Windows 7 SP1
    
    Purpose: Reads a GMAT script from the same directory, and
    iteratively runs GMAT using temp scripts with modified
    variables.

    NOTE: For now, filepath cannot include a space
    
    Effects: Outputs summary data in a .csv file.

'''
import sys
import subprocess
import numpy
import os
import platform


def run():
    #OS-aware code to get path of GMAT and relevant files required to run GMAT.
    user_platform = platform.system()
    cwd = os.getcwd()
    userhome = os.path.expanduser('~')
    CURRENT_USER = os.path.split(userhome)[-1]
    if (user_platform == "Windows"):
        GMAT_LOCATION = "C:\\Users\\" + CURRENT_USER + "\\AppData\\Local\GMAT\\R2016a\\bin\\GMAT.exe"
        TEMP_SCRIPT_FILE_NAME = cwd + "\\temp.script"
        SCRIPT_FILE_NAME = cwd + "\\"
    else: #NOTE: GMAT is required to be in the user's PATH if not on Windows
        GMAT_LOCATION = "gmat"
        TEMP_SCRIPT_FILE_NAME = cwd + "/temp.script"
        SCRIPT_FILE_NAME = cwd
    
    SCRIPT_FILE_NAME += input("Please Enter a File Name: ")
    filenameparam = input("Please enter the name of the file parameter you want to modify: ")
    thrustparam = input("Please enter the thrust parameter you want to modify: ")
    start_variable = float(input("Please enter start value: "))
    end_variable = float(input("Please enter end value: "))
    step = float(input("Please enter step value: "))
    

    #GMAT data goes in subfolder escape_data, should folder not exist we'll create it
    OUTPUT_FILE = cwd + "\\escape_data\\"
    if not os.path.isdir(OUTPUT_FILE):
       os.makedirs(OUTPUT_FILE)
    OUTPUT_FILE = OUTPUT_FILE + "escape_data"
    print("GMAT Runner Script v 1.1")
    filecounter = 0
    
    template_script_io = open(SCRIPT_FILE_NAME)
    output_summary_io = open(OUTPUT_FILE + ".csv", "w")
    script_text = template_script_io.read()

    for loopcounter in list(numpy.arange(start_variable, end_variable + step, step)):
        filecounter += 1
        
        script_text = UpdateParameters(script_text, thrustparam,
                                        loopcounter)
        script_text = UpdateParameters(script_text, filenameparam,
                                                 "'" + OUTPUT_FILE + str(filecounter) + ".txt'")

        running_script_io = open(TEMP_SCRIPT_FILE_NAME, "w")
        running_script_io.write(script_text)
        running_script_io.close()
        
        runGMAT(TEMP_SCRIPT_FILE_NAME, GMAT_LOCATION, loopcounter)

    for file in range(1,filecounter):
        with open(OUTPUT_FILE + str(file) + ".txt", 'r') as fh:
            for line in fh:
                pass
            last = line
            data = line.split()
            output_summary_io.write(','.join(map(str, data)))
            output_summary_io.write("\n")
    
def main():
    run()
    

#Looks in string <content> for <param>, and updates it's value to <param_value>
#Returns modified string
def UpdateParameters(content, param, param_value):
    semicolon = ";"
    pos = content.find(param)
    if (pos <= 0):
        print("ERROR: Invalid GMAT script file: unable to find parameter")
    pos2 = content.find(";", pos)
    if (pos <= 0):
        print("Error: Invalid GMAT script file: line not terminated with ;")
    return (content[:pos] + param + " = " + str(param_value) + content[pos2:])

#Runs GMAT with the script location and the iteration name
#Prints status to terminal.
def runGMAT(file_name, GMAT, iteration):
    print("Running GMAT with iteration #" + str(iteration) + file_name)
    subprocess.call(GMAT + " --run --exit --minimize " + file_name)

if __name__ == "__main__":
    main()

