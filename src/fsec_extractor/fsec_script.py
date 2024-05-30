from string import ascii_uppercase
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import glob
from io import StringIO
import re
from collections import defaultdict
import tkinter as tk
from tkinter import *


def run():
    def extractor(path, is_detergent_screen, names, measure, end_marker, detergents, condense_factor):
        """Extracts data from measure absorbance"""

        def open_error_window(error):
            error_window = Tk()
            error_window.title("Exception!")
            Label(error_window, anchor="w", text=error).grid(row=0)

        all_files = glob.glob(os.path.join(path, "*.txt"))

        def extract_retention_time():

            def check_flow_rate(method):
                if (method.startswith(
                        'C:\LabSolutions\Data\Project1\Methods\GFP+TRYP\Microtitre plate autosampler\Fast 1.5ml_min')
                        or method.startswith('C:\\LabSolutions\\Data\\Project1\\Methods\\GFP+TRYP\\FAST 1.5 ML_MIN')):
                    flow_rate = 1.5
                elif method.startswith(
                        'C:\LabSolutions\Data\Project1\Methods\GFP+TRYP\Microtitre plate autosampler\Fast 1 ml_min'):
                    flow_rate = 1.0
                else:
                    flow_rate = None
                return flow_rate

            start_index = None
            end_index = None

            try:

                with open(all_files[0], 'r') as file:
                    lines = file.readlines()

                    # Find the start and end markers
                for i, line in enumerate(lines):
                    if 'R.Time (min)\tIntensity' in line:
                        start_index = i + 1
                    elif end_marker in line:
                        end_index = i
                        break

                    elif 'Method File' in line:
                        method_file = line.split('\t')[1].strip()  # Extract method file

                if start_index is not None and end_index is not None:
                    reduced_lines = lines[start_index:end_index:condense_factor]
                    dfr = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[0],
                                      names=['Retention Volume (mL)'])

                # Multiply the first column by the Flow rate
                if check_flow_rate(method_file) and 'Retention Volume (mL)' in dfr:
                    dfr['Retention Volume (mL)'] = dfr['Retention Volume (mL)'] * check_flow_rate(method_file)
                else:
                    dfr['Retention Volume (mL)'] = dfr['Retention Volume (mL)'] * 1

            except IndexError:
                open_error_window("No text files found. Check directory given.")

            except pd.errors.ParserError as e:
                open_error_window(f"Error in file {filename}: {e}")

            return dfr

        def extract_intensities():
            dfs = []
            sample_name = None

            for filename in all_files:
                try:
                    with open(filename, 'r') as file:
                        lines = file.readlines()

                    # Find the indices of the start and end markers
                    for i, line in enumerate(lines):
                        if 'R.Time (min)\tIntensity' in line:
                            start_index = i + 1
                        elif end_marker in line:
                            end_index = i
                            break
                        elif 'Vial#' in line:
                            sample_name = line.split('\t')[1].strip()  # Extract Sample Name

                    if start_index is not None and end_index is not None:
                        # Create a DataFrame from every "condense_factor"nth row between the markers
                        reduced_lines = lines[start_index:end_index:condense_factor]
                        # For subsequent files, create a DataFrame with the second column
                        df = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[1],
                                         header=None)
                        # Rename the column to the Sample Name
                        df.rename(columns={df.columns[0]: sample_name}, inplace=True)


                    else:
                        print(f"Markers not found in file {filename}")

                except pd.errors.ParserError as e:
                    print(f"Error in file {filename}: {e}")

                dfs.append(df)
            return dfs

        def combine_dataframes(dfr, dfs, flow_rate):

            combined_df = pd.concat(dfs, axis=1)
            combined_df = pd.concat([combined_df, dfr], axis=1)

            # Alphanumeric sorting
            def sort_key(column_name):
                # Split the column name into non-digit and digit parts
                parts = re.split(r'(\d+)', column_name)
                return (parts[0], int(parts[1])) if len(parts) > 1 else (parts[0], 0)

            # Rename columns with duplicate labels to make them unique
            column_counts = defaultdict(int)
            new_columns = []
            for column_name in combined_df.columns:
                if column_name in new_columns:
                    column_counts[column_name] += 1
                    new_name = f"{column_name}_{column_counts[column_name]}"
                    new_columns.append(new_name)
                else:
                    new_columns.append(column_name)

            combined_df.columns = new_columns

            # Order columns alphanumerically by sample name
            combined_df = combined_df.reindex(sorted(combined_df.columns, key=sort_key), axis=1)

            # Make Retention Volume the first column
            column_order = ['Retention Volume (mL)'] + [col for col in combined_df.columns if
                                                        col != 'Retention Volume (mL)']
            measure_table = combined_df[column_order]

            # Save the combined DataFrame to a CSV file
            if condense_factor == 12:
                measure_table.to_csv(os.path.join(path, str(measure) + ".csv"), index=False)

            return measure_table

        # Plot graphs

        def check_detergent_names(measure_table):

            def plot_graphs_for_alphanumeric(y_labels, no_label, no_names, letters_dict):

                plt.close('all')
                try:
                    letters_iterator = iter(letters_dict)
                    for i in range(len(letters_dict.items())):
                        key = next(letters_iterator)
                        value = letters_dict[key]

                        if no_label:
                            y_labels = value
                        if no_names:
                            name = key
                        elif not no_names:
                            name = names[i]
                        measure_table.plot(kind='line', title=name + ": Plot of Intensity (mV)",
                                           x="Retention Volume (mL)",
                                           label=y_labels, y=value, xlim=(5, 15),
                                           color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
                                                  '#e377c2',
                                                  '#7f7f7f', '#bcbd22', '#17becf', 'darkblue'])
                        plt.savefig(path + "//" + measure + " - " + name + ".svg")
                        plt.close('all')

                except ValueError:
                    open_error_window("Labels not the same length as y axes. Re-open and check you have inputted detergents correctly.")

            def plot_graphs_for_other(sample_names):

                plt.close('all')

                for sample in sample_names:
                    measure_table.plot(kind='line', title="Plot of Intensity (mV)", x="Retention Volume (mL)",
                                       label=sample, y=sample, xlim=(5, 15), color='blue')

                    plt.savefig(path + "//" + measure + " - " + sample + ".svg")
                    plt.close('all')

            # Check whether alphanumeric columns exist and store in "letters_dict"
            ls = []
            for c in ascii_uppercase[:8]:
                temp = []
                for i in range(12):
                    temp.append(c + str(i + 1))
                ls.append(temp)
            letters = {}
            letter_count = 0
            for c in ascii_uppercase[:8]:
                letters[c] = list(filter(lambda x: x in measure_table.columns, ls[letter_count]))
                letter_count = letter_count + 1
            letters_dict = {k: v for k, v in letters.items() if v}

            if letters_dict:

                no_label = False
                no_names = False
                if is_detergent_screen:
                    y_labels = ['DDM', 'DDM CHS', 'DM', 'DM CHS', 'OG', 'LMNG', 'OGNG CHS', 'LDAO', 'C12E8',
                                'C12E9 CHS', 'CYMAL-5']
                if detergents:
                    y_labels = detergents
                else:
                    # If user left detergent fields blank
                    y_labels = []
                    no_label = True
                if not (list(filter(lambda x: x != "", names))):
                    no_names = True
                plot_graphs_for_alphanumeric(y_labels, no_label, no_names, letters_dict)
            else:
                sample_names = list(measure_table)
                sample_names.pop(0)
                plot_graphs_for_other(sample_names)

        # Call functions to extract data into "dfr" and "dfs".

        combine_dataframes(extract_retention_time(), extract_intensities(), 1.5)
        if condense_factor == 1:
            check_detergent_names(combine_dataframes(extract_retention_time(), extract_intensities(), 1.5))

    def extractor_gui():
        """The GUI for the data extractor."""

        master = Tk()  # The master window.
        master.title('F-SEC data extractor')
        background_color = 'white'
        master.config(bg=background_color)
        master.resizable(False, False)


        is_detergent_screen_tk = tk.BooleanVar()  # Checkbutton for detergent screen
        Checkbutton(master, text='12 detergent screen ', variable=is_detergent_screen_tk, bg=background_color).grid(row=4, column=1,
                                                                                                             sticky=W)

        path_tk = StringVar()  # Entry box for directory
        Label(master, width=30, anchor="e", text='Path to folder containing .txt files:', fg="#ba4a00",
              font=("sans",10,"bold"), bd=5, bg=background_color).grid(row=1)
        Entry(master, textvariable=path_tk, bg='#fe7c7c', width = 30).grid(row=1, column=1)

        a1 = StringVar()
        a2 = StringVar()
        a3 = StringVar()
        a4 = StringVar()
        a5 = StringVar()
        a6 = StringVar()
        a7 = StringVar()
        a8 = StringVar()

        d1 = StringVar()
        d2 = StringVar()
        d3 = StringVar()
        d4 = StringVar()
        d5 = StringVar()
        d6 = StringVar()
        d7 = StringVar()
        d8 = StringVar()
        d9 = StringVar()
        d10 = StringVar()
        d11 = StringVar()
        d12 = StringVar()

        alpha = [a1, a2, a3, a4, a5, a6, a7, a8]  # This creates the entry fields for the proteins

        Label(master, font=("arial",8), width=40, anchor="w", text='(Optional) Names of proteins/constructs ', bd=5, bg=background_color).grid(
            row=6)
        Label(master, font=("arial",8), width=40, anchor="w", text='for each row (A-H):', bd=5, bg=background_color).grid(
            row=7)
        for a, i in zip(alpha, range(len(alpha))):
            Entry(master, width=15, textvariable=a, bg='white').grid(row=9+i, column=0)

        delta = [d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12]  # Entry fields for detergents

        Label(master,font=("arial",8), width=40, anchor="w", text="(Optional) Names of detergents", bg=background_color).grid(row=6,
                                                                                                             column=1)
        Label(master,font=("arial",8), width=40, anchor="w", text=" for each column (1-12):", bg=background_color).grid(row=7,
                                                                                                             column=1)
        for d, i in zip(delta, range(len(delta))):
            Entry(master, width=15, textvariable=d, bg='white').grid(row=9 + i, column=1)

        end_marker = {"UV_absorbance": "[LC Chromatogram(Detector A-Ch2)]",
                      "GFP_fluorescence": "[LC Chromatogram(Detector B-Ch2)]",
                      "Trp_fluorescence": "[LC Chromatogram(Detector B-Ch3)]"}

        def submit():
            """Stores variables after pressing submit button"""
            names = [str(a1.get()), str(a2.get()), str(a3.get()), str(a4.get()),
                     str(a5.get()), str(a6.get()), str(a7.get()), str(a8.get())]
            print(names)
            detergents = list(filter(lambda item: item != "", [str(d1.get()), str(d2.get()), str(d3.get()),
                                                               str(d4.get()), str(d5.get()), str(d6.get()),
                                                               str(d7.get()), str(d8.get()), str(d9.get()),
                                                               str(d10.get()),
                                                               str(d11.get()), str(d12.get())]))
            for e in end_marker:
                for f in [12, 1]:
                    extractor(str(path_tk.get()), int(is_detergent_screen_tk.get()), names, e,
                              end_marker.get(e), detergents, f)
            master.destroy()

        Button(master, text='Submit', command=submit).grid(row=40, column=0)

        mainloop()

    extractor_gui()


run()
