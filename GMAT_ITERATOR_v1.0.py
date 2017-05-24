#!/usr/bin/env python
'''
    GMAT_ITERATOR_v1.1
    Authors: Michael Rinehart
             Neil Eelman
    Date last revised : 23 May 2017

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
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory


# Tkinter application class that handles the GUI and the majority of the script functions
class App(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        self.pack()
        self.setup()

    # Set up all script inputs in the Tkinter GUI
    def setup(self):
        #self.parent.geometry("400x250")
        self.parent.title("GMAT Iterator")
        self.columnconfigure(1, minsize=250)

        tk.Button(self, text="Select script", command=self.set_file
                 ).grid(row=0, column=0, pady=2, sticky="W")
        self.script_label = tk.Label(self, text="No script selected")
        self.script_label.grid(row=0, column=1, padx=2, pady=2, sticky="E")

        tk.Button(self, text="Select directory", command=self.set_cwd
                 ).grid(row=1, column=0, pady=2, sticky="W")
        self.directory_label = tk.Label(self, text="No directory selected")
        self.directory_label.grid(row=1, column=1, padx=2, pady=2, sticky="E")

        script_variables= ['Earth.ConstantThrust','ExampleVar']
        self.script_variable = tk.StringVar()
        self.script_variable.set(script_variables[0])
        tk.OptionMenu(self, self.script_variable, *script_variables
                     ).grid(row=2, column=0, columnspan=2, pady=2, sticky="W")

        # The %P parameter passes the value of text if the modification is allowed
        # and the %S parameter passes the text being added or deleted
        vcmd = (self.parent.register(self.validate),'%P','%S')

        self.start_variable = tk.DoubleVar()
        tk.Label(self, text="Start:").grid(row=3, column=0, padx=2, pady=2, sticky="W")
        tk.Entry(self, textvariable=self.start_variable, validate="key",
                validatecommand=vcmd, width=15).grid(row=3, column=1, padx=2, pady=2, sticky="W")

        self.step_variable = tk.DoubleVar()
        tk.Label(self, text="Step:").grid(row=4, column=0, padx=2, pady=2, sticky="W")
        tk.Entry(self, textvariable=self.step_variable, validate="key",
                validatecommand=vcmd, width=15).grid(row=4, column=1, padx=2, pady=2, sticky="W")

        self.end_variable = tk.DoubleVar()
        tk.Label(self, text="End:").grid(row=5, column=0, padx=2, pady=2, sticky="W")
        tk.Entry(self, textvariable=self.end_variable, validate="key",
                validatecommand=vcmd, width=15).grid(row=5, column=1, padx=2, pady=2, sticky="W")

        tk.Button(self, text="Run", command=self.run).grid(row=6, column=0, pady=2, sticky="W")
        tk.Button(self, text="Exit", command=self.quit).grid(row=6, column=1, pady=2, sticky="W")

    # Function used to validate text entry in the the GUI for start, end, and step values
    def validate(self, value_if_allowed, text):
        if text in '0123456789.-+':
            if value_if_allowed == '':
                return True
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        return False

    def set_file(self):
        self.script_file_name = askopenfilename()
        self.script_label["text"] = self.script_file_name
        self.cwd = "/".join(self.script_file_name.split("/")[:-1])
        self.directory_label["text"] = self.cwd

    def set_cwd(self):
        self.cwd = askdirectory()
        self.directory_label["text"] = self.cwd

    # Main function of the script that handles file modification and GMAT iteration
    def run(self):
        # Ensure that all variables are set before continuing
        if not hasattr(self, 'script_file_name'):
            print("Please select a script file.")
            return
        start = self.start_variable.get()
        end = self.end_variable.get()
        step = self.step_variable.get()
        script_param = self.script_variable.get()
        if not start and not end:
            print("Please enter a non-zero start or stop value.")
            return
        if not step:
            print("Please enter a step value.")
            return
        if not hasattr(self, 'cwd'):
            self.cwd = os.getcwd()

        # OS-aware code to get path of GMAT and relevant files required to run GMAT
        user_platform = platform.system()
        if (user_platform == "Windows"):
            current_user = os.getlogin()
            self.gmat_location = "C:/Users/" + current_user + "/AppData/Local/GMAT/R2016a/bin/GMAT.exe"
        else: # GMAT is required to be in the user's PATH if not on Windows
            self.gmat_location = "gmat"
        self.temp_script_file_name = self.cwd + "/temp.script"

        # GMAT data goes in subfolder escape_data, should folder not exist we'll create it
        output_file = self.cwd + "/escape_data/"
        if not os.path.isdir(output_file):
            os.makedirs(output_file)
        output_file += "escape_data"
        print("GMAT Iterator Script")
        filecounter = 1
        filenameparam = "EarthData.Filename"

        with open(self.script_file_name) as template_script_io:
            script_text = template_script_io.read()
        output_summary_io = open(output_file + ".csv", "w")

        for loopcounter in list(numpy.arange(start, end + step, step)):
            script_text = update_parameters(script_text, script_param, loopcounter)
            script_text = update_parameters(script_text, filenameparam,
                                            "'" + output_file + str(filecounter) + ".txt'")

            with open(self.temp_script_file_name, "w") as running_script_io:
                running_script_io.write(script_text)

            run_gmat(self.temp_script_file_name, self.gmat_location, loopcounter)
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
        os.remove(self.temp_script_file_name)
        print("Iterations complete.")
        return


# Looks in string <content> for <param>, and updates it's value to <param_value>
# Returns modified string
def update_parameters(content, param, param_value):
    pos = content.find(param)
    if (pos <= 0):
        print("Error: unable to find given parameter")
        return
    pos2 = content.find(";", pos)
    if (pos <= 0):
        print("Error: GMAT script line not terminated with ;")
        return
    return (content[:pos] + param + " = " + str(param_value) + content[pos2:])


# Runs GMAT with the script location and the iteration name
# Prints status to terminal.
def run_gmat(file_name, GMAT, iteration):
    print("Running GMAT with iteration #" + str(iteration) + " " + file_name)
    subprocess.call(GMAT + " --run --exit --minimize " + file_name)


def main():
    root = tk.Tk()
    app = App(root)
    app.mainloop()


if __name__ == "__main__":
    main()
