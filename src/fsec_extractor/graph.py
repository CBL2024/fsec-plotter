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

def metadata_plot(metadata, out_path, measure_table, measure, xlims, ylims):
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
        # v = list of dataframe columns to plot (e.g., ['A1', 'B2'])
        # k = metadata key for the data to be plotted together, e.g., '8His tag'

        labs=[] # Initialise label variable

        plt.close('all') # Close all plots to free memory

        cm = plt.get_cmap('inferno') # Choose colormap 'inferno'
        colors = [cm(i / len(v)) for i in range(len(v))] # Number of colors depends on len list to plot

        for en in enumerate(v): # Extract elements from "v"
            labs.append(" ".join(metadata[en[1]]))
            # Returns all metadata info about each element in "v"
            # then joins it with " " separator.
            # Appends each label to list "labs"
            # This is used as the labels for the graph.
        fig = measure_table.plot(kind='line', title=f"{k}_{measure}", x="Retention Volume (mL)",
                           label=labs, ylabel='Intensity (mV)', y=v, color=colors)

        print(xlims)
        if xlims != ('',''):
            fig.set_xlim(xlims)
        if ylims != ('',''):
            fig.set_ylim(ylims)

        mpld3.save_html(plt.gcf(), f"{make_output_dir(name=measure,path=out_path)}//{k}.html")
        # This saves the graphs in an interactive html format.
        plt.savefig(f"{make_output_dir(name=measure,path=out_path)}//{k}.svg")
        # This saves the graphs as vector graphics.




