# Plot graphs

import os
from string import ascii_uppercase
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import mpld3

def make_output_dir(name, path):
    """
    Args:
        name: name of folder
        path: path to store data
    """
    filepath = os.path.join(path, name)
    if not os.path.exists(filepath):
       os.mkdir(filepath)
    return filepath

# Check whether there is a metadata excel file.
def excel_check(path):
    """
    Args:
        path - path to check for excel file.
    """
    # Checks for files ending with .xlsx
    # Stores data in dictionary with key of first row in df.
    files = [f for f in os.listdir(path) if f.endswith('.xlsx')]
    if len(files) == 1:
        file = files[0]
        df = pd.read_excel(os.path.join(path, file), 'Plate map')
        metadata = {}
        for index, row in df.iterrows():
            metadata[row[0].replace('0', '')] = list(row[1:])
        return metadata
    else:
        print("No Excel files found.")
        return None

def check_alphabet(measure_table):
    # Check whether alphanumeric columns exist
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
    new_letters = {k: v for k, v in letters.items() if v}
    return new_letters

def alphanum_plot(path, letters_dict, measure_table, measure):
    plt.close('all')
    try:
        letters_iterator = iter(letters_dict)
        for i in range(len(letters_dict.items())):
            key = next(letters_iterator)
            value = letters_dict[key]
            measure_table.plot(kind='line', x="Retention Volume (mL)", ylabel='Intensity (mV)',
                               label=detergents, y=value)
            plt.savefig(f"{make_output_dir(measure, path)}//{value}.svg")
    except ValueError as e:
        print(e)

def from_excel_plot(metadata, out_path, measure_table, measure):
    grouped = {}
    vals_in_data = {}
    for key, values in metadata.items():
        for value in values:
            if value not in grouped:
                grouped[value] = []
            # Append the original key to the list for this value
            grouped[value].append(key)

    for key, values in grouped.items():
        # Create list of only metadata values that correspond to columns in measure_table
        vals_in_data[key] = list(set(values).intersection(list(measure_table)))
    same_vals_filtered = {k: v for k, v in vals_in_data.items() if v} # Remove keys with empty strings.

    for k,v in same_vals_filtered.items():

        plt.close('all')
        cm = plt.get_cmap('inferno')
        colors = [cm(i / len(v)) for i in range(len(v))] # Number of colors depends on length of plotted list

        measure_table.plot(kind='line', title=f"{k}_{measure}", x="Retention Volume (mL)",
                               ylabel='Intensity (mV)', y=v, color=colors)
        mpld3.save_html(plt.gcf(), f"{make_output_dir(name=measure,path=out_path)}//{k}.html")
        plt.savefig(f"{make_output_dir(name=measure,path=out_path)}//{k}.svg")



