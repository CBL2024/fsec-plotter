########## fsec-plotter #########

Function:
The function of this script is to extract the intensity vs retention time data from ASCII Shimadzu HPLC output files.
The script concatenates the intensities from every run into a single dataframe, rearranging the columns in a helpful format.

Useage:
It is expected that the user:

1. Organises all the txt to be concatenated and analysed into the same folder and (OPTIONAL) includes a metadata Excel file in this folder as well.
2. Provides the file path to this folder.
3. Specifies values for the output, such as x and y limits for graphing.

The script includes a tkinter-built GUI which enables ease of use for inputting preferences and specifying the filepath.
