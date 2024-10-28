# Plot graphs

def create_directory(measure, output):
    filepath = os.path.join(output, wave(measure))
    for m in measure:
        if not os.path.exists(filepath):
            os.mkdir(filepath)
    return (filepath)


def check_detergent_names(measure_table, xlims):
    ''' Check whether detergents have been added. '''

    meta_dict = None

    if len(xlims[1]) > 0:  # xlims is a str not int. Check it contains then sets x limits.
        xlims_in = [int(xlims[0]), int(xlims[1])]

    else:
        xlims_in = [5, 18]
    print(xlims_in)

    # if file_check: # checks whether the plate map is present. If present, create dict with metadata.
    # meta_dict = extract_metadata(path)

    def plot_graphs_for_alphanumeric(y_labels, no_label, no_names, letters_dict, out_path, xlims, meta_dict):
        plt.close('all')
        try:
            letters_iterator = iter(letters_dict)
            for i in range(len(letters_dict.items())):
                key = next(letters_iterator)
                value = letters_dict[key]
                if no_names:
                    name = names[i]
                if no_label:
                    y_labels = value
                # elif file_check:
                # name = meta_dict[i]
                elif no_names:
                    name = key

                measure_table.plot(kind='line', title=name, x="Retention Volume (mL)", ylabel='Intensity (mV)',
                                   label=y_labels, y=value, xlim=xlims,
                                   color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
                                          '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', 'darkblue'])
                plt.savefig(f"{create_directory(measure, out_path)}//{wave(measure)}-{name}.svg")
                plt.close('all')
        except ValueError:
            open_error_window(
                "Labels not the same length as y axes. Re-open and check you have inputted detergents correctly.")

    def plot_graphs_for_other(sample_names, out_path, xlims):
        plt.close('all')
        for sample in sample_names:
            measure_table.plot(kind='line', title=sample, x="Retention Volume (mL)", ylabel='Intensity (mV)',
                               label=sample, xlim=xlims, y=sample, color='blue')
            plt.savefig(f"{create_directory(measure, out_path)}//{wave(measure)}-{sample}.svg")
            plt.close('all')

    def plot_graphs_for_meta(metadata, out_path, xlims):
        plt.close('all')
        print(metadata.items())
        for key in metadata:
            for i in range(9):
                grouping = [k for k, v in metadata.items if v[i] == 'Joana']
                print(grouping)
                measure_table.plot(kind='line', title=f'{key}-{metadata[key][i]}', x="Retention Volume (mL)",
                                   ylabel='Intensity (mV)',
                                   label=grouping, xlim=xlims, y=grouping, color='blue')
                plt.savefig(f"{create_directory(measure, out_path)}//{wave(measure)}-{key}-{metadata[key][i]}.svg")
                plt.close('all')

    # Check whether there is a metadata excel file.

    def excel_check(path):
        '''submit button for metadata question.'''
        files = [f for f in os.listdir(path) if f.endswith('.xlsx')]
        if len(files) == 1:
            file = files[0]
            df = pd.read_excel(os.path.join(path, file), 'Plate map')
            metadata = {}
            for index, row in df.iterrows():
                metadata[row[0].replace('0', '')] = [row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                                     row[9], row[10]]
            print(metadata)
        else:
            open_error_window("Too many or no Excel files found.")
        return (metadata)

    if excel_check(path):
        output_path_2 = os.path.join(path, 'Plots for metadata')  # output path
        if not os.path.exists(output_path_2):
            os.mkdir(output_path_2)
        plot_graphs_for_meta(excel_check(path), output_path_2, xlims_in)

    # Check whether alphanumeric columns exist and store in "letters_dict"
    ls = []
    for c in ascii_uppercase[:8]:
        temp = []
        for i in range(12):
            temp.append(c + str(i + 1))
        ls.append(temp)
    letters = {}
    letter_count = 0
    for c in ascii_uppercase[:8]:
        letters[c] = list(filter(lambda x: x in measure_table.columns, ls[letter_count]))
        letter_count = letter_count + 1
    letters_dict = {k: v for k, v in letters.items() if v}

    if letters_dict:

        no_label = False
        no_names = False
        if is_detergent_screen:
            y_labels = ['DDM', 'DDM CHS', 'DM', 'DM CHS', 'OG', 'LMNG', 'OGNG CHS', 'LDAO', 'C12E8',
                        'C12E9 CHS', 'CYMAL-5']
        if detergents:
            y_labels = detergents
        else:
            # If user left detergent fields blank
            y_labels = []
            no_label = True
        if not (list(filter(lambda x: x != "", names))):
            no_names = True

        output_path1 = os.path.join(path, 'Rows plotted together')
        if not os.path.exists(output_path1):
            os.mkdir(output_path1)

        plot_graphs_for_alphanumeric(y_labels, no_label, no_names, letters_dict, output_path1, xlims_in, meta_dict)

        output_path = os.path.join(path, 'Individual plots')  # output path
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        sample_names = list(measure_table)
        sample_names.pop(0)
        plot_graphs_for_other(sample_names, output_path, xlims_in)
    else:
        output_path = os.path.join(path, 'Individual plots')  # output path
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        sample_names = list(measure_table)
        sample_names.pop(0)
        plot_graphs_for_other(sample_names, output_path, xlims_in)


# Call functions to extract data into "dfr" and "dfs".



