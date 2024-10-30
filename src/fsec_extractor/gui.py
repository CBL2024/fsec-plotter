import tkinter as tk
from tkinter import *
from extractor import *
from graph import *

def extractor_gui():

    """
    The GUI for the data extractor.
    User inputs values and when called,
    returns dictionary of inputted values with keys 'path', 'names', 'detergents'.
    """

    master = Tk()
    master.title('F-SEC data plotter')
    background_color = 'white'
    master.config(bg=background_color)
    master.resizable(False, False)

    is_detergent_screen_tk = tk.BooleanVar()  # Checkbutton for detergent screen
    Checkbutton(master, text='12 detergent screen ', variable=is_detergent_screen_tk, bg=background_color).grid(
        row=4, column=0, padx=10,
        sticky=W)

    correction_tk = tk.BooleanVar()  # Checkbutton
    Checkbutton(master, text='Correct baselines? ', variable=correction_tk, bg=background_color).grid(
        row=4, column=1, padx=10,
        sticky=W)

    xlim1_tk = tk.StringVar() # Enter x limits for graphs
    xlim2_tk = tk.StringVar()
    Label(master, width=10, anchor="e", text='X limits:',bg=background_color).grid(row=4, column=3, padx=(10, 20))
    Entry(master, textvariable=xlim1_tk, bg='#f2f2f2', width=2).grid(row=4, column=4, padx=(0, 10))
    Entry(master, textvariable=xlim2_tk, bg='#f2f2f2', width=2).grid(row=4, column=5, padx=(0, 10))

    path_tk = StringVar()  # Entry box for directory
    Label(master, width=30, anchor="e", text='Path to folder containing .txt files:', fg="red",
          font=("sans", 8, "bold"), bd=5, bg=background_color).grid(row=1, padx=(10, 20))
    Entry(master, textvariable=path_tk, bg='#fff7ec', width=20).grid(row=1, column=1, padx=(0, 10))

    alpha = []
    for i in range(8):
        alpha.append(StringVar())

    delta = []
    for i in range(12):
        delta.append(StringVar())

    Label(master, font=("arial", 8), width=20, anchor="w", text='(Optional) Names of constructs ', bd=5,
          bg=background_color).grid(
        row=6, padx=(10, 110))
    Label(master, font=("arial", 8), width=20, anchor="w", text='for each row (A-H):', bd=5,
          bg=background_color).grid(
        row=7, padx=(10, 100))
    for a, i in zip(alpha, range(len(alpha))):
        Entry(master, borderwidth=2, relief="sunken", width=20, textvariable=a, bg='white').grid(row=9 + i,
                                                                                                 column=0,
                                                                                                 padx=(10, 100))

    Label(master, font=("arial", 8), width=30, anchor="w", text="(Optional) Names of detergents",
          bg=background_color).grid(row=6,
                                    column=1, padx=(10, 10))
    Label(master, font=("arial", 8), width=30, anchor="w", text=" for each column (1-12):",
          bg=background_color).grid(row=7,
                                    column=1, padx=(10, 10))
    for d, i in zip(delta, range(len(delta))):
        Entry(master, borderwidth=2, relief="sunken", width=20, textvariable=d, bg='white').grid(row=9 + i,
                                                                                                 column=1,
                                                                                                 padx=(0, 10))
    def submit():
        """Stores variables after pressing submit button"""

        master.destroy()

    def plate_button():
        master.destroy()
        plate_gui()

    Button(master, text='Submit', font=("arial", 10, "bold"), command=submit, width=10,
           borderwidth=1).grid(row=40, column=0, pady=10, padx=(100, 0))

    Button(master, text='Select from plate layout', font=("arial", 10, "bold"), command=plate_button, width=25,
           borderwidth=1).grid(row=40, column=1, pady=10)

    mainloop()

    # Store user-inputted values:
    names = []
    for a in range(len(alpha)):
        names.append(str(alpha[a].get()))
    detergents_ls = []
    for d in range(len(delta)):
        detergents_ls.append(str(delta[d].get()))
    xlims = [xlim1_tk.get(),xlim2_tk.get()]

    parameters = {
        'path':str(path_tk.get()),
        'names':names,
        'detergents':detergents_ls,
        'xlims':xlims
    }
    return parameters

if __name__ == "__main__":
    extractor_gui()