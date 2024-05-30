from F_SEC_data_extractor import data_extractor
import tkinter as tk
from tkinter import *


def extractor_gui():
    '''The GUI for the data extractor.'''

    master = Tk()
    is_detergent_screen_tk = tk.BooleanVar()
    is_test_expression_tk = tk.BooleanVar()
    path_tk = StringVar()

    master.title('F-SEC data extractor')

    Checkbutton(master, text='12 detergent screen ', variable=is_detergent_screen_tk).grid(row=2, sticky=W)
    Checkbutton(master, text='Test expression with DDM and FC-12)', variable=is_test_expression_tk).grid(row=3,
                                                                                                         sticky=W)
    Label(master, text='Directory containing .txt data files:').grid(row=4)
    Entry(master, textvariable=path_tk).grid(row=4, column=1)
    Label(master, text='(For graphs only) Names of proteins/constructs:').grid(row=6)

    a1 = StringVar()
    a2 = StringVar()
    a3 = StringVar()
    a4 = StringVar()
    a5 = StringVar()
    a6 = StringVar()
    a7 = StringVar()
    a8 = StringVar()

    d1 = StringVar()
    d2 = StringVar()
    d3 = StringVar()
    d4 = StringVar()
    d5 = StringVar()
    d6 = StringVar()
    d7 = StringVar()
    d8 = StringVar()
    d9 = StringVar()
    d10 = StringVar()
    d11 = StringVar()
    d12 = StringVar()

    end_marker = {"UV_absorbance": "[LC Chromatogram(Detector A-Ch2)]",
                  "GFP_fluorescence": "[LC Chromatogram(Detector B-Ch2)]",
                  "Trp_fluorescence": "[LC Chromatogram(Detector B-Ch3)]"}

    # This creates the entry fields for the proteins to be inputted.
    for i in range(8):
        Entry(master, textvariable=a1).grid(row=8, column=0)
        Entry(master, textvariable=a2).grid(row=9, column=0)
        Entry(master, textvariable=a3).grid(row=10, column=0)
        Entry(master, textvariable=a4).grid(row=11, column=0)
        Entry(master, textvariable=a5).grid(row=12, column=0)
        Entry(master, textvariable=a6).grid(row=13, column=0)
        Entry(master, textvariable=a7).grid(row=14, column=0)
        Entry(master, textvariable=a8).grid(row=15, column=0)

    for i in range(12):
        Label(master, text="(optional) Names of detergents if non-standard:").grid(row=16)
        Entry(master, textvariable=d1).grid(row=17, column=0)
        Entry(master, textvariable=d2).grid(row=18, column=0)
        Entry(master, textvariable=d3).grid(row=19, column=0)
        Entry(master, textvariable=d4).grid(row=20, column=0)
        Entry(master, textvariable=d5).grid(row=21, column=0)
        Entry(master, textvariable=d6).grid(row=22, column=0)
        Entry(master, textvariable=d7).grid(row=23, column=0)
        Entry(master, textvariable=d8).grid(row=24, column=0)
        Entry(master, textvariable=d9).grid(row=25, column=0)
        Entry(master, textvariable=d10).grid(row=26, column=0)
        Entry(master, textvariable=d11).grid(row=27, column=0)
        Entry(master, textvariable=d12).grid(row=28, column=0)

    def submit():
        '''Stores variables after pressing submit button'''
        names = [str(a1.get()), str(a2.get()), str(a3.get()), str(a4.get()),
                 str(a5.get()), str(a6.get()), str(a7.get()), str(a8.get())]
        detergents = list(filter(lambda item: item != "", [str(d1.get()), str(d2.get()), str(d3.get()),
                                                           str(d4.get()), str(d5.get()), str(d6.get()),
                                                           str(d7.get()), str(d8.get()), str(d9.get()), str(d10.get()),
                                                           str(d11.get()), str(d12.get())]))
        for e in end_marker:
            for f in [12, 1]:
                data_extractor.extractor(str(path_tk.get()), int(is_detergent_screen_tk.get()), names, e,
                                         end_marker.get(e), detergents, f)
        master.destroy()

    Button(master, text='Submit', command=submit).grid(row=30, column=0)

    mainloop()


extractor_gui()
