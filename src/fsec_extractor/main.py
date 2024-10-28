# # Main for fsec-plotter # #
from gui import extractor_gui
import extractor

def main():
    """
    Main function runs GUI first
    """
    extractor_gui() # Run the GUI which calls functions from graph and extractor modules

    # Extract data into dataframe
    combine_dataframes(extract_retention_time(), extract_intensities())

    # Plot graphs
    if condense_factor == 1:
        check_detergent_names(combine_dataframes(extract_retention_time(), extract_intensities()), xlims)


main()