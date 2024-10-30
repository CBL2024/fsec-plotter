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

    #correction_tk = tk.BooleanVar()  # Checkbutton
    #Checkbutton(master, text='Correct baselines? ', variable=correction_tk, bg=background_color).grid(
    #    row=4, column=1, padx=10,
    #    sticky=W)

    xlim1_tk = tk.StringVar() # Enter x limits for graphs
    xlim2_tk = tk.StringVar()
    ylim1_tk = tk.StringVar() # Enter x limits for graphs
    ylim2_tk = tk.StringVar()


    Label(master, width=10, anchor="e", text='x limits:',bg=background_color).grid(row=4, column=1, padx=(10, 20))
    Entry(master, textvariable=xlim1_tk, bg='#f2f2f2', width=2).grid(row=4, column=2, padx=(0, 10))
    Entry(master, textvariable=xlim2_tk, bg='#f2f2f2', width=2).grid(row=4, column=3, padx=(0, 10))
    Label(master, width=10, anchor="e", text='y limits:',bg=background_color).grid(row=5, column=3, padx=(10, 20))
    Entry(master, textvariable=ylim1_tk, bg='#f2f2f2', width=2).grid(row=5, column=2, padx=(0, 10))
    Entry(master, textvariable=ylim2_tk, bg='#f2f2f2', width=2).grid(row=5, column=3, padx=(0, 10))

    path_tk = StringVar()  # Entry box for directory
    Label(master, width=30, anchor="e", text='Path to folder containing .txt files:', fg="red",
          font=("sans", 8, "bold"), bd=5, bg=background_color).grid(row=1, padx=(10, 20))
    Entry(master, textvariable=path_tk, bg='#fff7ec', width=20).grid(row=1, column=1, padx=(0, 10))

    def submit():
        """Stores variables after pressing submit button"""

        master.destroy()

    Button(master, text='Submit', font=("arial", 10, "bold"), command=submit, width=10,
           borderwidth=1).grid(row=40, column=0, pady=10, padx=(100, 0))

    mainloop()

    # Store user-inputted values:
    xlims = (xlim1_tk.get(),xlim2_tk.get())
    ylims = (ylim1_tk.get(),ylim2_tk.get())

    parameters = {
        'path':str(path_tk.get()),
        'xlims':xlims,
        'ylims':ylims
    }
    return parameters

if __name__ == "__main__":
    extractor_gui()