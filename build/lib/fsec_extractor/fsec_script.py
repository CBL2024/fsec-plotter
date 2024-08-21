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
import tensorflow as tf
from keras.preprocessing import image
import numpy as np


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
                if "1.5 ML_MIN" in method_file:
                    flow_rate = 1.5
                elif "1.5ml_min" in method_file:
                    flow_rate = 1.5
                elif "1-5ml flow" in method_file:
                    flow_rate = 1.5
                elif '1ML_MIN' in method_file:
                    flow_rate = 1
                elif '1 ml_min' in method_file:
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

            # Save the combined DataFrame to a CSV file
            if condense_factor == 12:
                correct_baselines(measure_table).to_csv(os.path.join(path, str(measure) + ".csv"), index=False)

            return correct_baselines(measure_table)


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

    
##  M A C H I N E L E A R N I N G
    def graphs_ml(path):
        end_marker = {"GFP_fluorescence": "[LC Chromatogram(Detector B-Ch2)]"}
        files = glob.glob(os.path.join(path, "*.txt"))
        df = pd.DataFrame()
        output_dir = os.path.join(path,'tmp')
        if not os.path.exists(output_dir):
            os.mkdir(os.path.join(path,'tmp'))
        for file in files:
            for e in end_marker:
                try:
                    with open(file) as f:
                        lines = f.readlines()
                        start_index = None
                        end_index = None
                        for i, line in enumerate(lines):
                            if 'R.Time (min)\tIntensity' in line:
                                start_index = i + 1
                            elif 'Method File' in line:
                                method_file = line.split('\t')[1].strip()
                            elif end_marker.get(e) in line:
                                end_index = i
                                break

                        if start_index is not None and end_index is not None:
                            
                            def flow_rate(method_file):
                                if "1.5 ML_MIN" in method_file:
                                    flow_rate = 1.5
                                elif "1.5ml_min" in method_file:
                                    flow_rate = 1.5
                                elif "1-5ml flow" in method_file:
                                    flow_rate = 1.5
                                elif '1ML_MIN' in method_file:
                                    flow_rate = 1
                                elif '1 ml_min' in method_file:
                                    flow_rate = 1
                                else:
                                    flow_rate = 0.5
                                return flow_rate

                            section = lines[start_index:end_index]
                            df = pd.read_csv(StringIO(''.join(section)), sep='\t', engine='python', header=None)
                            plt.close('all')
                            x = df[0] * flow_rate(method_file)
                            y = df[1]
                            
                            fig, ax = plt.subplots()
                            ax.plot(x,y)                        
                            ax.autoscale()
                            ax.axis("off")                        
                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.fill_between(x, y, where=[v > 10000 for v in y], color='r', interpolate=True) # Make high signal red. Anything below <10000 is unusable.
                            ax.fill_between(x, y, where=[12 > z > 10.5 for z in x], color='green', interpolate=True) # At this volume free GFP elutes as a sharp peak.
                            ax.fill_between(x, y, where=[z < 6.7 for z in x], color='yellow', interpolate=True) # 6-6.7 should colour the void peak.
                            ax.fill_between(x, y, where=[z < 6 for z in x], color='gray', interpolate=True) # 6 is the void volume so anything before is not the sample.                                ax.fill_between(x, y, where=[v < 10000 for v in y], color='b', interpolate=True) # Make plot blue if signal is low.
                            filename = os.path.basename(file)
                            plot_path = os.path.join(f"{output_dir}", f"{filename}.png")
                            plt.savefig(plot_path)

                except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as ex:
                    print(f"Error in {file}...Skipping... Error: {ex}")
                    files.remove(file)
                    break

    def classify(path):

        model = tf.keras.models.load_model("C:\\Users\\qdj48121\\Documents\\fsec_script\\src\\fsec_extractor\\model.keras")

        model.compile(loss='categorical_crossentropy',
                    optimizer='rmsprop',
                    metrics=['accuracy'])

        # predicting images
        image_file_dir = os.path.join(path, 'tmp')
        all_images = os.listdir(image_file_dir)
        for i in all_images:
            img = image.load_img(os.path.join(image_file_dir,i), target_size=(150, 150))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)

            images = np.vstack([x])
            classes = model.predict(images)
            print(classes)
            #os.rmtree(image_file_dir)

    def extractor_gui():
        """The GUI for the data extractor."""

        master = Tk()
        master.title('F-SEC data extractor')
        background_color = 'white'
        master.config(bg=background_color)
        master.resizable(False, False)

        is_detergent_screen_tk = tk.BooleanVar()  # Checkbutton for detergent screen
        Checkbutton(master, text='12 detergent screen ', variable=is_detergent_screen_tk, bg=background_color).grid(
            row=4, column=1, padx=10,
            sticky=W)
        path_tk = StringVar()  # Entry box for directory
        Label(master, width=30, anchor="e", text='Path to folder containing .txt files:', fg="red",
              font=("sans", 8, "bold"), bd=5, bg=background_color).grid(row=1, padx=(10, 20))
        Entry(master, textvariable=path_tk, bg='grey', width=20).grid(row=1, column=1, padx=(0, 10))

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

        end_marker = {"UV_absorbance": "[LC Chromatogram(Detector A-Ch2)]",
                      "GFP_fluorescence": "[LC Chromatogram(Detector B-Ch2)]",
                      "Trp_fluorescence": "[LC Chromatogram(Detector B-Ch3)]"}

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
                              end_marker.get(e), detergents, f)
                    
            graphs_ml(str(path_tk.get()))
            classify(str(path_tk.get()))
            master.destroy()

        def plate_button():
            master.destroy()
            plate_gui()

        Button(master, text='Submit', font=("arial", 10, "bold"), command=submit, width=10,
               borderwidth=1).grid(row=40, column=0, pady=10, padx=(100, 0))

        Button(master, text='Select from plate layout', font=("arial", 10, "bold"), command=plate_button, width=25,
               borderwidth=1).grid(row=40, column=1, pady=10)

        mainloop()

    def plate_gui():
        slave = Tk()

        platelist = []
        for i in range(96):
            platelist.append(BooleanVar())

        for p, i in zip(platelist, range(len(platelist))):
            if i < 12:
                Label(slave, font=("arial", 8), width=0, anchor="w", text=i + 1).grid(row=0, column=i + 1)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="A").grid(row=1, column=0)
                Checkbutton(slave, variable=p).grid(row=1, column=i + 1, padx=0, sticky=W)
            elif i < 24:
                Checkbutton(slave, variable=p).grid(row=2, column=i - 11, padx=0, sticky=W)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="B").grid(row=2, column=0)
            elif i < 36:
                Checkbutton(slave, variable=p).grid(row=3, column=i - 23, padx=0, sticky=W)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="C").grid(row=3, column=0)
            elif i < 48:
                Checkbutton(slave, variable=p).grid(row=4, column=i - 35, padx=0, sticky=W)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="D").grid(row=4, column=0)
            elif i < 60:
                Checkbutton(slave, variable=p).grid(row=5, column=i - 47, padx=0, sticky=W)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="E").grid(row=5, column=0)
            elif i < 72:
                Checkbutton(slave, variable=p).grid(row=6, column=i - 59, padx=0, sticky=W)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="F").grid(row=6, column=0)
            elif i < 84:
                Checkbutton(slave, variable=p).grid(row=7, column=i - 71, padx=0, sticky=W)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="G").grid(row=7, column=0)
            elif i < 96:
                Checkbutton(slave, variable=p).grid(row=8, column=i - 83, padx=0, sticky=W)
                Label(slave, font=("arial", 8), width=0, anchor="w", text="H").grid(row=8, column=0)

        def Submit():
            slave.destroy()

        Button(slave, text='Submit', font=("arial", 10, "bold"), command=Submit, width=5,
               borderwidth=1).grid(row=9, column=13, pady=10, padx=10)

        mainloop()

    extractor_gui()

run()