import pandas as pd
import os
import glob
from io import StringIO
import re
from collections import defaultdict
from BaselineRemoval import BaselineRemoval

path = 'test_dataset'

def extract(path, correction):
    """
    Extracts data from measure absorbance

    Args
    path: filepath where .txt files are.
    correction: binary value for whether baseline correction is preferred or not

    """

    end_marker = {"[LC Chromatogram(Detector A-Ch1)]": "[LC Chromatogram(Detector A-Ch2)]",
                  "[LC Chromatogram(Detector A-Ch2)]": "[LC Chromatogram(Detector B-Ch1)]",
                  "[LC Chromatogram(Detector B-Ch1)]": "[LC Chromatogram(Detector B-Ch2)]",
                  "[LC Chromatogram(Detector B-Ch2)]": "[LC Chromatogram(Detector B-Ch3)]"}
    # End markers deliniate which lines data is on in the file.


# # Functions to extract metadata:

    def wave(measure):  # Extract the wavelength(s) for each detector measurement, return the wavelength as a string.
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
                        wavelength = "Fluorescence_at_" + "ex_" + lines[excitation_line].split('\t')[
                            1].strip() + "_em_" + lines[emission_line].split('\t')[1].strip()

        return (wavelength)

    def flow_rate(method):
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

    all_files = glob.glob(os.path.join(path, "*.txt"))

    for measure, end_marker in end_marker.keys, end_marker.values:
        for condense in [12, 1]: # Repeat for "condensed" data or raw data.

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

                    if start_index and end_index:
                        reduced_lines = lines[start_index:end_index:condense]
                        dfr = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[0],
                                          names=['Retention Volume (mL)'])
                        df = pd.read_csv(StringIO(''.join(reduced_lines)), sep='\t', engine='python', usecols=[1],
                                         header=None)
                        # Rename the column to the Sample Name
                        df.rename(columns={df.columns[0]: sample_name}, inplace=True)

                    else:
                        print(f"Data not found in file {filename}")

                except pd.errors.ParserError as e:
                    print(f"Error in file {filename}: {e}")


                # Multiply the first column by the Flow rate
                if flow_rate(method_file) and 'Retention Volume (mL)' in dfr:
                    dfr['Retention Volume (mL)'] = dfr['Retention Volume (mL)'] * flow_rate(method_file)
                else:
                    dfr['Retention Volume (mL)'] = dfr['Retention Volume (mL)'] * 1
                    # do something else

                dfs.append([dfr,df]) # A list of dataframes containing the individual file data.

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

        measure_table = combined_df[column_order]
        if correction:
            measure_table = correct_baselines(measure_table)

        # Save the combined DataFrame to a CSV file
        if condense == 12:
            measure_table.to_csv(os.path.join(path, f"{measure.split('(')[1].split(')')[0]}-{wave(measure)}.csv"), index=False)

        return measure_table