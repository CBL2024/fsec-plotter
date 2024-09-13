from string import ascii_uppercase
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import glob
from io import StringIO
import re
from collections import defaultdict
import tkinter as tk
from tkinter import *
import BaselineRemoval
from BaselineRemoval import BaselineRemoval
import tensorflow as tf
from keras.preprocessing import image
import numpy as np


path = 'D:\\220824'

##  Prediction
def run():
    def graphs(path):
        end_marker = {"[LC Chromatogram(Detector B-Ch2)]": "[LC Chromatogram(Detector B-Ch3)]"}
        files = glob.glob(os.path.join(path, "*.txt"))
        df = pd.DataFrame()
        output_dir = os.path.join(path,'tmp')
        if not os.path.exists(output_dir):
            os.mkdir(os.path.join(path,'tmp'))
        for file in files:
            for e in end_marker:
                try:
                    with open(file) as f:
                        lines = f.readlines()
                        start_index = None
                        end_index = None
                        for i, line in enumerate(lines):
                            if 'R.Time (min)\tIntensity' in line:
                                start_index = i + 1
                            elif 'Method File' in line:
                                method_file = line.split('\t')[1].strip()
                            elif 'Sample Name' in line:
                                sample_name = line.split('\t')[1].strip()  # Extract Sample Name
                            elif end_marker.get(e) in line:
                                end_index = i
                                break

                        if start_index is not None and end_index is not None:
                            
                            def flow_rate(method_file):
                                if "1.5 ML_MIN" in method_file:
                                    flow_rate = 1.5
                                elif "1.5ml_min" in method_file:
                                    flow_rate = 1.5
                                elif "1-5ml flow" in method_file:
                                    flow_rate = 1.5
                                elif '1ML_MIN' in method_file:
                                    flow_rate = 1
                                elif '1 ml_min' in method_file:
                                    flow_rate = 1
                                else:
                                    flow_rate = 0.5
                                return flow_rate

                            section = lines[start_index:end_index]
                            df = pd.read_csv(StringIO(''.join(section)), sep='\t', engine='python', header=None)
                            plt.close('all')
                            x = df[0] * flow_rate(method_file)
                            y = df[1]
                            
                            fig, ax = plt.subplots()
                            ax.plot(x,y)                        
                            ax.autoscale()
                            ax.axis("off")                        
                            ax.set_xticks([])
                            ax.set_yticks([])
                            ax.fill_between(x, y, where=[v > 10000 for v in y], color='r', interpolate=True) # Make high signal red. Anything below <10000 is unusable.
                            ax.fill_between(x, y, where=[12 > z > 10.5 for z in x], color='green', interpolate=True) # At this volume free GFP elutes as a sharp peak.
                            ax.fill_between(x, y, where=[z < 6.7 for z in x], color='yellow', interpolate=True) # 6-6.7 should colour the void peak.
                            ax.fill_between(x, y, where=[z < 6 for z in x], color='gray', interpolate=True) # 6 is the void volume so anything before is not the sample.                                ax.fill_between(x, y, where=[v < 10000 for v in y], color='b', interpolate=True) # Make plot blue if signal is low.
                            filename = os.path.basename(file)
                            plot_path = os.path.join(f"{output_dir}", f"{sample_name}.png")
                            plt.savefig(plot_path)

                except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as ex:
                    print(f"Error in {file}...Skipping... Error: {ex}")
                    files.remove(file)
                    break

    def classify(path):

        model = tf.keras.models.load_model("C:\\Users\\qdj48121\\Documents\\fsec_script\\src\\fsec_extractor\\test.keras")

        model.compile(loss='categorical_crossentropy',
                    optimizer='rmsprop',
                    metrics=['accuracy'])

        # predicting images

        imglist = os.listdir(os.path.join(path, 'tmp'))

        tmp_dict = {}
        for pic in imglist:
            img = image.load_img(os.path.join(path, 'tmp', pic), target_size=(150, 150))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            images = np.vstack([x])
            c = model.predict(images)
            ls = c.ravel()
            for i in range(len(ls)): 
                if ls[i] > 0:  tmp_dict[pic]=i+1 # Makes b a list of all classes

        def sort_key(tmp_dict):
            # Split the column name into non-digit and digit parts
            parts = re.split(r'(\d+)', tmp_dict)
            return (parts[0], int(parts[1])) if len(parts) > 1 else (parts[0], 0)

        reordered_list = sorted(tmp_dict, key=sort_key)
        reordered_dict = {k: tmp_dict[k] for k in reordered_list}

        return(reordered_dict)

    def output(results, path):

        empty_ls = [0,0,0,0,0,0,0,0]
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
        def row_position(results, let): # This arranges the results into a plate format
            row = [0,0,0,0,0,0,0,0,0,0,0,0]
            for k, v in results.items():
                if let in k:
                    parts = re.split(r'(\d+)', k)
                    for i in range(12):                   
                        if int(parts[1]) == i + 1:
                            row[i] = (v)
            return(row)
        
        for n,l in enumerate(letters):
            empty_ls[n] = row_position(results, l)

        print(empty_ls)

        plt.close()
        x = np.arange(0, 13, 1) 
        y = np.arange(0, 9, 1)  

        fig, ax = plt.subplots()
        ax.pcolormesh(x, y, empty_ls[::-1])

        plt.show()
        plt.savefig(os.path.join(path,'output.jpg'))

    graphs(path)
    output(classify(path), path)

run()