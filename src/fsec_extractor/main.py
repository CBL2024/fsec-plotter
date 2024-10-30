# # Main for fsec-plotter # #
from gui import extractor_gui
from extractor import extract
import graph
import os

def main():
    """
    Main function runs GUI first
    """
    # Run the GUI which calls functions from graph and extractor modules
    # Extract data into dataframe
    params = extractor_gui()

    print(params)
    metadata = graph.excel_check(params['path'])  # Check for excel file.

    # End markers delineate which lines data is on in the file.
    end_marker = {"[LC Chromatogram(Detector A-Ch1)]": "[LC Chromatogram(Detector A-Ch2)]",
                  "[LC Chromatogram(Detector A-Ch2)]": "[LC Chromatogram(Detector B-Ch1)]",
                  "[LC Chromatogram(Detector B-Ch1)]": "[LC Chromatogram(Detector B-Ch2)]",
                  "[LC Chromatogram(Detector B-Ch2)]": "[LC Chromatogram(Detector B-Ch3)]"}

    for start, end in end_marker.items():
        for n in [12,1]:
            measure_dict = extract(inputs=params, start=start, end=end, condense=n) # Store dataframe in dict
            for key, data in measure_dict.items():
                if n == 12: # Save condensed raw data.
                   data.to_csv(os.path.join(params['path'], f"{start.split('(')[1].split(')')[0]}-{key}.csv"), index=False)
                if n == 1: # Graph uncondensed data.
                    if metadata:
                        graph.from_excel_plot(metadata=metadata, out_path=params['path'], measure=key, measure_table=data)
                    elif params['detergents']:
                        letters_dict = graph.check_alphabet(data) # Create dictionary of all letters contained in table
                        graph.alphanum_plot(path=params['path'], letters_dict=letters_dict,
                                            measure_table=data, measure=key,
                                            detergents=params['detergents'],
                                            names=params['names']) # Plot same letter together



    print("Extraction complete.")
    # Plot graphs

if __name__ == "__main__":
    main()