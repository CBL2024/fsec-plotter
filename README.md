//What does it do///
The script takes a path inputted by the user and reads all the .txt files within the directory, 
extracting the lines containing the relevant data (i.e., retention time + intensity for each wavelength). 
These are then joined into Pandas dataframes which are saved as .csvs for each measurement 
Graphs are made in matplotlib assuming all columns in each row on the microtitre plate are plotted together. 

/// Protein and detergent (or any condition) names. ///
The GUI provides entry fields for entering protein names.
You do not have to enter anything here. If you don't, the graphs will be plotted based on vial number. 
If you want the graph labels for sample/condition, it's important to enter the protein names or detergents in the correct order, as run on the Shimadzu machine. 
e.g., if you were to only run samples in A1-A12 and G1-G12, only fill in the names in the first entry field and 7th entry field.



