The script takes a path inputted by the user and reads all the .txt files within the directory, 
extracting the lines containing the relevant data. 
These are then joined into Pandas dataframes which are saved as .csvs for each abs/fluorescnece measurement and used to create graphs in matplotlib. 

/// Protein and detergent (or any condition) names. ///
The GUI provides entry fields for entering protein names.
You do not have to enter anything here. If you don't, the graphs will be plotted based on vial number. 
It's important to enter the protein names or detergents in the correct order, as run on the Shimadzu machine. 
e.g., if you were to only run samples in A1-A12 and G1-G12, only fill in the names in the first entry field and 7th entry field.

/// Flow rate. ///
If you are using the "standard" method that we use for Trp/GFP then this isn't a problem. 
However, the flow rate information is only obtainable from the name of the method file that was used.
The script will assume that the flow rate is 1.0 if the method file name differs from a standard method.
This will make the Retention Volume = Retention Time and if your flow rate was different from 1.0, it is incorrect.



