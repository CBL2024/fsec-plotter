from string import ascii_uppercase
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import glob
from io import StringIO
import re
from collections import defaultdict


def extractor(path, is_detergent_screen, names, measure, end_marker, detergents, condense_factor):
    '''Extracts data from measure absorbance'''

    all_files = glob.glob(os.path.join(path, "*.txt"))
    start_index = None
    end_index = None
    first_file = True

    for filename in all_files:
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            # Find the start and end markers
            for i, line in enumerate(lines):
                if 'R.Time (min)\tIntensity' in line:
                    start_index = i + 1
                elif end_marker in line:
                    end_index = i
                    break

            if start_index is not None and end_index is not None:
                # Create a DataFrame from every "condense_factor"nth row between the markers. Uses uncondensed data
                # to plot graphs, but outputs condensed data into csv.
                reduced_lines = lines[start_index:end_index:condense_factor]
                if first_file:
                    # For the first file, create a DataFrame with the first column
                    dfr = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[0],
                                      names=['Retention Volume (mL)'])
                    first_file = False

            else:
                print(f"Markers not found in file {filename}")

        except pd.errors.ParserError as e:
            print(f"Error in file {filename}: {e}")

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
                elif 'Method File' in line:
                    method_file = line.split('\t')[1].strip()  # Extract method file
                    if method_file.startswith(
                            "C:\LabSolutions\Data\Project1\Methods\GFP+TRYP\Microtitre plate autosampler\Fast 1.5ml_min"):
                        flow_rate = 1.5
                    else:
                        flow_rate = input("What is the flow rate of this experiment?")

            if start_index is not None and end_index is not None:
                # Create a DataFrame from every "condense_factor"nth row between the markers
                reduced_lines = lines[start_index:end_index:condense_factor]
                if first_file:
                    # For the first file, create a DataFrame with the first column
                    df = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[0],
                                     names=['Retention Volume (mL)'])
                    first_file = False

                else:
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

    # Combine DataFrames into a single DataFrame with columns for each file
    combined_df = pd.concat(dfs, axis=1)
    combined_df = pd.concat([combined_df, dfr], axis=1)

    # Multiply the first column by the Flow rate
    if 'Retention Volume (mL)' in combined_df:
        combined_df['Retention Volume (mL)'] = combined_df['Retention Volume (mL)'] * flow_rate

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
    column_order = ['Retention Volume (mL)'] + [col for col in combined_df.columns if col != 'Retention Volume (mL)']
    measure_table = combined_df[column_order]

    # Save the combined DataFrame to a CSV file
    measure_table.to_csv(os.path.join(path, str(measure) + ".csv"), index=False)

    # Plot graphs

    def plot_graphs_for_alphanumeric(y_labels, no_label, no_names, letters_dict):
        no_of_rows = len(letters_dict.keys())
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
                else:
                    name = names[i]
                measure_table.plot(kind='line', title=name + ": Plot of Intensity (mV)", x="Retention Volume (mL)",
                                   label=y_labels, y=value, xlim=(5, 15),
                                   color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
                                          '#7f7f7f', '#bcbd22', '#17becf', 'darkblue'])
                plt.savefig(path + "//" + measure + " - " + name + ".svg")
                plt.close('all')
        except ValueError:
            print("ValueError. Label not the same length as y. Check you have inputted the detergents correctly.")

    def plot_graphs_for_other(sample_names):
        no_of_rows = len(letters.keys())
        plt.close('all')

        for sample in sample_names:

            measure_table.plot(kind='line', title="Plot of Intensity (mV)", x="Retention Volume (mL)",
                                       label=sample, y=sample, xlim=(5, 15), color='blue')

            plt.savefig(path + "//" + measure + " - " + sample + ".svg")
            plt.close('all')


    # Only check names if plotting graphs

    if condense_factor == 1:

        def check_detergent_names():
                        
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

        check_detergent_names()
               
