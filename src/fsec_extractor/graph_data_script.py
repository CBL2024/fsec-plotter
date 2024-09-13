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
import BaselineRemoval
from BaselineRemoval import BaselineRemoval


def run():
    def extractor(path, is_detergent_screen, names, measure, end_marker, detergents, condense_factor, correction, xlims):
        """Extracts data from measure absorbance"""

        all_files = glob.glob(os.path.join(path, "*.txt"))

        def open_error_window(error):
            error_window = Tk()
            error_window.title("Error!")
            Label(error_window, anchor="w", text=error).grid(row=0)

        def wave(measure): # Extract the wavelength(s) for each detector measurement, return the wavelength as a string.
            with open(all_files[0], 'r') as file:
                lines = file.readlines()
                for n, line in enumerate(lines):
                    if measure in line:
                        if 'Detector A' in measure:
                            wavelength_line = n + 7
                            wavelength = "Absorbance_" + lines[wavelength_line].split('\t')[1].strip()
                        elif 'Detector B' in measure:
                            excitation_line = n + 7
                            emission_line = n + 8
                            wavelength = "Fluorescence_at_" + "ex_" + lines[excitation_line].split('\t')[1].strip()+"_em_"+lines[emission_line].split('\t')[1].strip()

            return(wavelength)

        def extract_retention_time():

            def check_flow_rate(method):
                ''' Extract the flow rate from method file and return it. '''
                if "1.5 ML_MIN" in method:
                    flow_rate = 1.5
                elif "1.5ml_min" in method:
                    flow_rate = 1.5
                elif "1-5ml flow" in method:
                    flow_rate = 1.5
                elif '1ML_MIN' in method:
                    flow_rate = 1
                elif '1 ml_min' in method:
                    flow_rate = 1
                else:
                    flow_rate = 0.5
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
                    if start_index and end_index:
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
                        elif 'Sample Name' in line:
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
                        print(f"Data not found in file {filename}")

                except pd.errors.ParserError as e:
                    print(f"Error in file {filename}: {e}")

                dfs.append(df)
            return dfs

        def combine_dataframes(dfr, dfs):

            def correct_baselines(measure_table):
                '''Uses BaselineRemoval package Zhangfit method to correct baselines.'''
                for col in measure_table.columns:
                    try:
                        if col != 'Retention Volume (mL)':
                            baseObj = BaselineRemoval(measure_table[col])
                            Zhangfit_output = baseObj.ZhangFit()
                            measure_table[col] = Zhangfit_output
                    except ValueError or IndexError:
                        open_error_window("Baseline correction failed.")

                return measure_table

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
                
            corrected_table = correct_baselines(measure_table)

            # Save the combined DataFrame to a CSV file
            if condense_factor == 12:
                if correction:
                    corrected_table.to_csv(os.path.join(path, f"{measure.split('(')[1].split(')')[0]}-{wave(measure)}.csv"), index=False)
                else:
                    measure_table.to_csv(os.path.join(path, f"{measure.split('(')[1].split(')')[0]}-{wave(measure)}.csv"), index=False)

            return corrected_table if correction else measure_table

        # Plot graphs

        def create_directory(measure, output):
            filepath = os.path.join(output, wave(measure))
            for m in measure:
                if not os.path.exists(filepath):
                    os.mkdir(filepath)
            return(filepath)
                


        def check_detergent_names(measure_table, xlims):
            ''' Check whether detergents have been added. '''

            meta_dict = None

            if len(xlims[1]) > 0: # xlims is a str not int. Check it contains then sets x limits.
                xlims_in = [int(xlims[0]),int(xlims[1])]
                
            else:
                xlims_in = [5,18]
            print(xlims_in)

            #if file_check: # checks whether the plate map is present. If present, create dict with metadata.
                #meta_dict = extract_metadata(path)

            def plot_graphs_for_alphanumeric(y_labels, no_label, no_names, letters_dict, out_path, xlims, meta_dict):
                plt.close('all')
                try:
                    letters_iterator = iter(letters_dict)
                    for i in range(len(letters_dict.items())):
                        key = next(letters_iterator)
                        value = letters_dict[key]
                        if no_names:
                            name = names[i]
                        if no_label:
                            y_labels = value
                        #elif file_check:
                            #name = meta_dict[i] 
                        elif no_names:
                            name = key

                        measure_table.plot(kind='line', title=name, x="Retention Volume (mL)", ylabel='Intensity (mV)',
                                           label=y_labels, y=value, xlim=xlims,
                                           color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
                                                  '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', 'darkblue'])
                        plt.savefig(f"{create_directory(measure, out_path)}//{wave(measure)}-{name}.svg")
                        plt.close('all')
                except ValueError:
                    open_error_window("Labels not the same length as y axes. Re-open and check you have inputted detergents correctly.")

            def plot_graphs_for_other(sample_names, out_path, xlims):
                plt.close('all')
                for sample in sample_names:
                    measure_table.plot(kind='line', title=sample, x="Retention Volume (mL)", ylabel ='Intensity (mV)',
                                       label=sample, xlim=xlims, y=sample, color='blue')
                    plt.savefig(f"{create_directory(measure, out_path)}//{wave(measure)}-{sample}.svg")
                    plt.close('all')

            def plot_graphs_for_meta(metadata, out_path, xlims):
                plt.close('all')      
                print(metadata.items())          
                for key in metadata:
                    for i in range(9):
                        grouping = [k for k, v in metadata.items if v[i] == 'Joana']
                        print(grouping)
                        measure_table.plot(kind='line', title=f'{key}-{metadata[key][i]}', x="Retention Volume (mL)", ylabel ='Intensity (mV)',
                                            label=grouping, xlim=xlims, y=grouping, color='blue')
                        plt.savefig(f"{create_directory(measure, out_path)}//{wave(measure)}-{key}-{metadata[key][i]}.svg")
                        plt.close('all')


            # Check whether there is a metadata excel file.

            def excel_check(path):
                '''submit button for metadata question.'''     
                files = [f for f in os.listdir(path) if f.endswith('.xlsx')]
                if len(files) == 1:
                    file = files[0]
                    df = pd.read_excel(os.path.join(path, file),'Plate map')
                    metadata = {}
                    for index, row in df.iterrows():
                        metadata[row[0].replace('0','')]=[row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]]
                    print(metadata)
                else: 
                    open_error_window("Too many or no Excel files found.")
                return(metadata)

            if excel_check(path):
                output_path_2 = os.path.join(path,'Plots for metadata') # output path
                if not os.path.exists(output_path_2):
                    os.mkdir(output_path_2)
                plot_graphs_for_meta(excel_check(path), output_path_2, xlims_in)
        
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
                
                output_path1 = os.path.join(path, 'Rows plotted together')
                if not os.path.exists(output_path1):
                    os.mkdir(output_path1) 

                plot_graphs_for_alphanumeric(y_labels, no_label, no_names, letters_dict, output_path1, xlims_in, meta_dict)

                output_path = os.path.join(path,'Individual plots') # output path
                if not os.path.exists(output_path):
                    os.mkdir(output_path)
                    
                sample_names = list(measure_table)
                sample_names.pop(0)
                plot_graphs_for_other(sample_names, output_path, xlims_in)
            else:
                output_path = os.path.join(path,'Individual plots') # output path
                if not os.path.exists(output_path):
                    os.mkdir(output_path)
                sample_names = list(measure_table)
                sample_names.pop(0)
                plot_graphs_for_other(sample_names, output_path, xlims_in)

        # Call functions to extract data into "dfr" and "dfs".

        combine_dataframes(extract_retention_time(), extract_intensities())
        if condense_factor == 1:
            check_detergent_names(combine_dataframes(extract_retention_time(), extract_intensities()), xlims)
           
    def extractor_gui():
        
            #if len(files) > 1:
            #open_error_window("More than one excel file found.")

        """The GUI for the data extractor."""

        end_marker = {"[LC Chromatogram(Detector A-Ch1)]": "[LC Chromatogram(Detector A-Ch2)]",
                      "[LC Chromatogram(Detector A-Ch2)]": "[LC Chromatogram(Detector B-Ch1)]",
                      "[LC Chromatogram(Detector B-Ch1)]": "[LC Chromatogram(Detector B-Ch2)]",
                      "[LC Chromatogram(Detector B-Ch2)]": "[LC Chromatogram(Detector B-Ch3)]"}

        master = Tk()
        master.title('F-SEC data extractor')
        background_color = 'white'
        master.config(bg=background_color)
        master.resizable(False, False)

        is_detergent_screen_tk = tk.BooleanVar()  # Checkbutton for detergent screen
        Checkbutton(master, text='12 detergent screen ', variable=is_detergent_screen_tk, bg=background_color).grid(
            row=4, column=0, padx=10,
            sticky=W)

        correction_tk = tk.BooleanVar()  # Checkbutton 
        Checkbutton(master, text='Correct baselines? ', variable=correction_tk, bg=background_color).grid(
            row=4, column=1, padx=10,
            sticky=W)
        
        xlim1_tk = tk.StringVar() # Enter x limits for graphs
        xlim2_tk = tk.StringVar()
        Label(master, width=10, anchor="e", text='X limits:',bg=background_color).grid(row=4, column=3, padx=(10, 20))
        Entry(master, textvariable=xlim1_tk, bg='#f2f2f2', width=2).grid(row=4, column=4, padx=(0, 10))
        Entry(master, textvariable=xlim2_tk, bg='#f2f2f2', width=2).grid(row=4, column=5, padx=(0, 10))

        path_tk = StringVar()  # Entry box for directory
        Label(master, width=30, anchor="e", text='Path to folder containing .txt files:', fg="red",
              font=("sans", 8, "bold"), bd=5, bg=background_color).grid(row=1, padx=(10, 20))
        Entry(master, textvariable=path_tk, bg='#fff7ec', width=20).grid(row=1, column=1, padx=(0, 10))

        alpha = []
        for i in range(8):
            alpha.append(StringVar())

        delta = []
        for i in range(12):
            delta.append(StringVar())

        Label(master, font=("arial", 8), width=20, anchor="w", text='(Optional) Names of constructs ', bd=5,
              bg=background_color).grid(
            row=6, padx=(10, 110))
        Label(master, font=("arial", 8), width=20, anchor="w", text='for each row (A-H):', bd=5,
              bg=background_color).grid(
            row=7, padx=(10, 100))
        for a, i in zip(alpha, range(len(alpha))):
            Entry(master, borderwidth=2, relief="sunken", width=20, textvariable=a, bg='white').grid(row=9 + i,
                                                                                                     column=0,
                                                                                                     padx=(10, 100))

        Label(master, font=("arial", 8), width=30, anchor="w", text="(Optional) Names of detergents",
              bg=background_color).grid(row=6,
                                        column=1, padx=(10, 10))
        Label(master, font=("arial", 8), width=30, anchor="w", text=" for each column (1-12):",
              bg=background_color).grid(row=7,
                                        column=1, padx=(10, 10))
        for d, i in zip(delta, range(len(delta))):
            Entry(master, borderwidth=2, relief="sunken", width=20, textvariable=d, bg='white').grid(row=9 + i,
                                                                                                     column=1,
                                                                                                     padx=(0, 10))
        def submit():
            """Stores variables after pressing submit button"""

            names = []
            for a in range(len(alpha)):
                names.append(str(alpha[a].get()))
            detergents_ls = []
            for d in range(len(delta)):
                detergents_ls.append(str(delta[d].get()))
            detergents = (list(filter(lambda item: item != "", detergents_ls)))
            for e in end_marker:
                for f in [12, 1]:
                    extractor(str(path_tk.get()), int(is_detergent_screen_tk.get()), names, e,
                              end_marker.get(e), detergents, f, int(correction_tk.get()), [xlim1_tk.get(),xlim2_tk.get()], )
            master.destroy()

        def plate_button():
            master.destroy()
            plate_gui()

        Button(master, text='Submit', font=("arial", 10, "bold"), command=submit, width=10,
               borderwidth=1).grid(row=40, column=0, pady=10, padx=(100, 0))

        Button(master, text='Select from plate layout', font=("arial", 10, "bold"), command=plate_button, width=25,
               borderwidth=1).grid(row=40, column=1, pady=10)

        mainloop()

    extractor_gui()

run()