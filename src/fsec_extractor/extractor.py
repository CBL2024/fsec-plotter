import pandas as pd
import os
import glob
from io import StringIO
import re
from collections import defaultdict
from BaselineRemoval import BaselineRemoval

def extract(inputs, start, end, condense):
    """
    Extracts data from measure absorbance

    --Args--
    path: filepath where .txt files are
    start: file start marker
    end: file end marker

    """

    def flow_rate(method):
        """ Extract the flow rate from method file and return it. """
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

    def correct_baselines(measure_table):
        '''Uses BaselineRemoval package Zhangfit method to correct baselines.'''
        for col in measure_table.columns:
            try:
                if col != 'Retention Volume (mL)':
                    baseObj = BaselineRemoval(measure_table[col])
                    Zhangfit_output = baseObj.ZhangFit()
                    measure_table[col] = Zhangfit_output
            except ValueError or IndexError:
                print("Baseline correction failed.")
        return measure_table

#######################################

    all_files = glob.glob(os.path.join(inputs['path'], "*.txt"))
    dfs = []
    start_index = None
    end_index = None
    file_metadata = {}  # Store wavelength, method, and name for each file

    for filename in all_files:

        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if 'R.Time (min)\tIntensity' in line:
                    start_index = i + 1 # Find index of start marker
                elif end in line:
                    end_index = i # Find index of end marker
                    break
                elif 'Sample Name' in line:
                    file_metadata['name'] = line.split('\t')[1].strip()  # Extract sample name
                elif 'Method File' in line:
                    file_metadata['method'] = line.split('\t')[1].strip()  # Extract method file

                # Extract wavelength
                elif start in line:
                    if 'Detector A' in start:
                        wavelength_line = i + 7
                        file_metadata['wavelength'] = "absorbance-"+lines[wavelength_line].split('\t')[1].strip()
                    elif 'Detector B' in start:
                        excitation_line = i + 7
                        emission_line = i + 8
                        file_metadata['wavelength'] = (
                        "excitation-"+lines[excitation_line].split('\t')[1].strip()+"nm"+
                        "-emission-"+lines[emission_line].split('\t')[1].strip())+"nm"

            if start_index and end_index:
                reduced_lines = lines[start_index:end_index:condense]
                dfr = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[0],
                                      names=['Retention Volume (mL)'])
                df = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[1],
                                 header=None)
                # Rename the column to the Sample Name
                df.rename(columns={df.columns[0]: file_metadata['name']}, inplace=True)

            else:
                print(f"Data not found in file {filename}")

        except pd.errors.ParserError as e:
            print(f"Error in file {filename}: {e}")


        # Multiply the first column by the Flow rate
        flow = flow_rate(file_metadata['method'])
        if flow_rate(file_metadata['method']) and 'Retention Volume (mL)' in dfr:
            dfr['Retention Volume (mL)'] = dfr['Retention Volume (mL)'] * flow
        else:
            dfr['Retention Volume (mL)'] = dfr['Retention Volume (mL)'] * 1
            # do something else

        dfs.append(df)       # A list of dataframes containing the individual file data.

    dfs.append(dfr)

    combined_df = pd.concat(dfs, axis=1) # Combine the dfs list into a single dataframe on axis=1

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
    def sort_key(column_name):
        # Split the column name into non-digit and digit parts
        parts = re.split(r'(\d+)', column_name)
        return (parts[0], int(parts[1])) if len(parts) > 1 else (parts[0], 0)
    combined_df = combined_df.reindex(sorted(combined_df.columns, key=sort_key), axis=1)

    # Make Retention Volume the first column
    column_order = ['Retention Volume (mL)'] + [col for col in combined_df.columns if col != 'Retention Volume (mL)']

    measure_table = correct_baselines(combined_df[column_order])

    # Save the combined DataFrame to a CSV file

    measure_dict = {file_metadata['wavelength']: measure_table}

    return measure_dict

