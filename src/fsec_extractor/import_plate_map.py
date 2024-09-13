import pandas as pd
import os

path = 'C:\\Users\\qdj48121\\Documents\\Test fsec'
all_files = [f for f in os.listdir(path) if f.endswith('.xlsx')]
#if len(all_files) > 1:
    #oepn_error_window("More than one excel file found.")

print(all_files)
if len(all_files) == 1:
    file = all_files[0]
    df = pd.read_excel(os.path.join(path, file),'Plate map')
    print(df)

    for index, row in df.iterrows():
        data = {row[0].replace('0',''):(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])}
        print(data)