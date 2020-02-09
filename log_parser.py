"""Log to CSV Parser

This script allows to parse .log and .txt files into the CSV format.
Please read the README.md file for a quick usage tutorial or simply compile this script.

You can add more predefined parsing cases inside the parser() function.
Also, you can save your:
---> RegEx expressions inside the saved-regex_patterns.txt file.
---> CSV columns inside the saved-csv_columns.txt file
"""

# Import of required standard Python libraries. The main components are: 
# --> "csv" to read/save data into the CSV format
# --> "re" to use regular expression operations
# --> "tkinter" to create GUI interface
import os
import sys
import csv
import re
import tkinter as tk
from tkinter import filedialog, Text, Tk, Frame, ttk, StringVar
from tkinter.filedialog import askopenfilenames
from tkinter.font import Font

# Read saved regex patterns from saved-regex_patterns.txt file
with open(os.path.join(sys.path[0], "saved-regex_patterns.txt"), "r") as f:
    saved_regex_patterns = []
    file_lines = f.read().splitlines()
    for line in file_lines:
        saved_regex_patterns.append(line)

# Read saved csv columns from saved-csv_columns.txt file
with open(os.path.join(sys.path[0], "saved-csv_columns.txt"), "r") as f:
    saved_csv_columns = []
    file_lines = f.read().splitlines()
    for line in file_lines:
        saved_csv_columns.append(line)

# Define the main application
class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Define app fonts
        text = tk.Text(self)
        global my_font_button
        global my_font_path
        my_font_button = Font(family='Consolas', size=14)
        my_font_path = Font(family='Courier New', size=9)
        
        text.configure(font=my_font_button)

        self.pack(padx=30, pady=30)
        self.create_widgets()

    # Widgets are the particular buttons/labels/text objects inside the GUI screen
    def create_widgets(self):
        # INPUT
        self.input_file_button = tk.Button(self, fg="white", bg="blue", font=my_font_button)
        self.input_file_button["text"] = "Select 1 (or more)\n.log or .txt files"
        self.input_file_button["command"] = self.select_file
        self.input_file_button.pack(side="top")

        self.input_path_label = tk.Label(self, wraplength=900, font=my_font_path, fg="#3a3a3a")
        self.input_path_label.pack(side="top")

        # OUTPUT
        self.output_folder_button = tk.Button(self, fg="white", bg="#004ffc", font=my_font_button)
        self.output_folder_button["text"] = "Choose the\noutput folder"
        self.output_folder_button["command"] = self.select_output_path
        self.output_folder_button.pack(side="top", pady=(10,0))

        self.output_path_label = tk.Label(self, wraplength=900, text=os.path.dirname(os.path.abspath(__file__)), font=my_font_path, fg="#3a3a3a")
        self.output_path_label.pack(side="top")

        # REGEX
        self.regex_input_info = tk.Label(self, text="Specify RegEx:", font=my_font_button)
        self.regex_input_info.pack(side="top", pady=(20,0))

        self.regex_input_field = ttk.Combobox(self, width = 60, values=saved_regex_patterns)
        self.regex_input_field.insert(tk.END, saved_regex_patterns[0])
        self.regex_input_field.pack()
        
        self.regex_input_info = tk.Label(self, fg="#515151", text="[INFO] Save more Python flavor RegEx patterns in saved-regex_patterns.txt\n[TIP] You can test your Python flavor expressions at regex101.com")
        self.regex_input_info.pack()

        # CSV COLUMNS
        self.csv_input_info = tk.Label(self, text="Specify CSV Columns:", font=my_font_button)
        self.csv_input_info.pack(side="top", pady=(20,0))

        self.csv_input_field = ttk.Combobox(self, width = 60, values=saved_csv_columns)
        self.csv_input_field.insert(tk.END, saved_csv_columns[0])
        self.csv_input_field.pack()
        
        self.csv_input_info = tk.Label(self, fg="#515151", text="[INFO 1] Save more csv columns (separated by ,) in saved-csv_columns.txt\n[INFO 2] This step is optional (you can leave the field blank).")
        self.csv_input_info.pack()

        # CONVERT
        self.convert_button = tk.Button(self, text="Convert to CSV", fg="white", bg="green", font=my_font_button, command=self.parser)
        self.convert_button.pack(pady=(30,0))

        self.parsing_finished_label = tk.Label(self, wraplength=900)
        self.parsing_finished_label.pack(side="top")

        # QUIT
        self.quit_button = tk.Button(self, text="QUIT", fg="white", bg="#E81123", font=my_font_button, command=self.master.destroy)
        self.quit_button.pack(side="bottom", pady=(30,0))

    def select_file(self):
        global input_path
        input_path = askopenfilenames(initialdir=os.getcwd(), title="Select the log file(s)", filetypes=[(
       "text files", ".log .txt"),("all files","*.*")])

       # Display input files in the app
        if input_path:
            if len(input_path) <= 5:
                list_of_files = "+ "+"\n+ ".join(input_path)
                self.input_path_label.config(text=list_of_files, fg="#3a3a3a")
            else:
                # Limit the display of input files to 5 elements, as otherwise it takes too much space on the main frame
                list_of_files = "+ "+"\n+ ".join(input_path[0:5])
                self.input_path_label.config(text=list_of_files+"\n+ ......", fg="#3a3a3a")
        else:
            self.input_path_label.config(text="No file chosen! Try again.", fg="#E81123")

    def select_output_path(self):
        global out_folder
        out_folder = os.path.dirname(os.path.abspath(__file__)) #if the user didn't select output folder, use the script folder
        out_folder = filedialog.askdirectory(initialdir=os.getcwd(), title="Select the output folder")

        # Display output folder path in the app
        if out_folder:
            self.output_path_label.config(text=out_folder)
        else:
            self.output_path_label.config(text=os.path.dirname(os.path.abspath(__file__)))
        
    def parser(self):
        try:
            # Define output file name
            csv_file_output_name = "PARSED__"+os.path.basename(input_path[0])+".csv"

            # Define output file path
            out_file_path = os.path.join(out_folder,csv_file_output_name)
        
            # Get the RegEx expression
            regex_pattern = re.compile(self.regex_input_field.get())

            # Get the CSV columns
            csv_columns = self.csv_input_field.get()
            csv_columns = csv_columns.split(",")

            # Define a loop for a later comparison
            list_of_previously_parsed = []

            #  Define match and row count for the total number of matches and rows
            match_total_number = 0
            row_total_number = 0

            # Open log file and start saving variables to the csv file
            for input_file in input_path:
                with open(input_file, 'r') as f_log, open(out_file_path, 'a', newline='') as f_csv:
                    lines = f_log.readlines()
                    try:
                        csv_writer = csv.writer(f_csv, dialect="excel")
                        # Write the CSV column headers only once (at the top of the .csv file)
                        if input_path.index(input_file) == 0:
                            csv_writer.writerow(csv_columns)
                    except IOError:
                        print("I/O error")
                    
#################### CUSTOM PARSER FOR A SPECIFIC REGEX STRING (predefined parsing for the 5 variables defined below) ####################
                    # If you want to add specific parsing such as the one below, you will have to recreate a similar block of code below
                    if self.regex_input_field.get() == r"(\b\d{1,2}/\d{1,2}/\d{1,4}\b)  (\b\d{1,2} : \d{1,2} : \d{1,4}\b . \d{1,3}\b)|((?<=vehicle\s{7}Id : ).*)\b|((?<=speed\s{29}= ).*)\b|((?<=\s{22}street_id\s{36}= str_).*)\b":
                        # Initialise variables
                        date = ""
                        time = ""
                        vehicle_id = ""
                        speed = ""
                        street_id = ""
                        # Parse log file line by line
                        for line in lines:
                            match = re.search(regex_pattern, line)
                            if match:
                                match_total_number += 1
                                # date & time (both are on the same line)
                                if match.group(1):
                                    date = match.group(1)
                                    time = match.group(2).replace(" ","") #replace() method removes whitespaces in the "time" string
                                # vehicle_id
                                if match.group(3):
                                    vehicle_id = match.group(3)
                                # speed
                                if match.group(4):
                                    speed = match.group(4)
                                    list_of_parsed = [date, time, vehicle_id, speed, street_id]
                                    # Use the "if" block to prevent writing lines of duplicated information
                                    if list_of_parsed != list_of_previously_parsed:
                                        csv_writer.writerow(list_of_parsed)
                                        row_total_number +=1
                                    list_of_previously_parsed = list_of_parsed
                                # street_id
                                if match.group(5):
                                    street_id = match.group(5)
                                    list_of_parsed = [date, time, vehicle_id, speed, street_id]
                                    # Use the "if" block to prevent writing lines of duplicated information
                                    if list_of_parsed != list_of_previously_parsed:
                                        csv_writer.writerow(list_of_parsed)
                                        row_total_number +=1
                                    list_of_previously_parsed = list_of_parsed
                            else:
                                pass

#################### ---> HERE YOU CAN ENTER YOUR INDIVIDUAL PARSING ALGORITHM. YOU CAN MAKE A SIMILAR BLOCK OF CODE AS THE "CUSTOM LOG PARSING" ABOVE (start the code with the "else if:" statement) <--- ####################

#################### GENERAL PARSER for any other type of RegEx pattern. It only prints out results when all the RegEx matching groups are found (you can check the full algorithm workflow in the "general_parsing_workflow.png" file) ####################
                    else:
                        #Count number of RegEx capturing groups
                        def num_groups_function(regex):
                            return re.compile(regex).groups
                        num_groups = num_groups_function(regex_pattern)
                        # Define a list for the general RegEx parser. "None" values are used as a placeholder to be replaced by the matched values
                        general_parser_list = [None]*num_groups
                        for line in lines:
                            match = re.search(regex_pattern, line)
                            if match:
                                match_total_number += 1
                                for i in range(1,num_groups+1):
                                    if match.group(i):
                                        # Match only if [i-1] element is different from the previously saved one (such as "None").
                                        # I am using "i-1" instead of "i", as Python list starts indexing from "0", but our range function starts from "1" (since we've to deal with the match.group() function)
                                        if match.group(i) is not general_parser_list[i-1]: 
                                            general_parser_list[i-1] = match.group(i)
                                        # Save the CSV row only if all RegEx matching groups are found (if all the None values in general_parser_list were replaced)
                                        if None not in general_parser_list:
                                            # Use the "if" block to prevent writing lines of duplicated information
                                            if general_parser_list != list_of_previously_parsed:
                                                csv_writer.writerow(general_parser_list)
                                                row_total_number +=1
                                            list_of_previously_parsed = general_parser_list
                                            # Clean the general_parser_list list
                                            general_parser_list = [None]*num_groups
                            else:
                                pass
            # Display green success message and output folder path
            self.parsing_finished_label.config(text="Done! "+str(row_total_number)+" row(s) of "+str(match_total_number)+" match(es) saved in the filename:\n"+csv_file_output_name, fg='#007235')
        except:
            self.parsing_finished_label.config(text="You did not select any input file yet!", fg='#E81123')


def main():
    root = tk.Tk()
    root.title("LOG to CSV parser")

    # Add app logo in the top of the GUI screen
    logo_image = tk.PhotoImage(file="graphics/app_header_image.png")
    tk.Label(root, image=logo_image).pack(side="top", pady=(10,0))

    # Create the main GUI window
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.eval('tk::PlaceWindow . center') # Display the window on the center of the screen
    root.mainloop() # Display the GUI application until the user clicks "QUIT" button

if __name__ == "__main__":
    main()