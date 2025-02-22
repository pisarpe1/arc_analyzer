from threading import Thread
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.filedialog import askopenfilenames

from src.load_files.load_csv import LoadCSVs


class CSVPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Plotter")
        self.root.geometry("800x600")

def output_values_and_plot():


    def start_loading(listbox, average_histogram_label):
        """Start the file-loading process in a separate thread."""
        new_window = tk.Toplevel(root)
        new_window.title("Loading Progress")
        new_window.geometry("400x200")

        progress = ttk.Progressbar(new_window, orient="horizontal", length=300, mode="determinate")
        progress.pack(pady=10)

        label_load = ttk.Label(new_window, text="Click 'Load Files' to start.")
        label_load.pack(pady=10)

        progress['value'] = 0
        label_load.config(text="Starting...")
        Thread(target=open_files, args=(listbox, average_histogram_label, new_window, progress, label_load), daemon=True).start()



    def create_main_window():
        root = tk.Tk()
        root.title("CSV Plotter")
        root.geometry("900x700")  # Set the window size to 800x600
        return root

    def create_listbox(root):
        listbox = tk.Listbox(root, width=50)
        listbox.pack(pady=20, side=tk.LEFT, fill=tk.BOTH, expand=True)
        return listbox

    def create_right_frame(root):
        right_frame = tk.Frame(root)
        right_frame.pack(pady=20, side=tk.RIGHT, fill=tk.BOTH, expand=True)
        return right_frame

    def create_labels(right_frame):
        histogram_label = tk.Label(right_frame, text="File Current Histogram")
        histogram_label.pack(pady=20)

        separator = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        average_histogram_label = tk.Label(right_frame, text="Average Current Histogram")
        average_histogram_label.pack(pady=20)

        separator = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        return histogram_label, average_histogram_label

    def open_files(listbox, average_histogram_label,new_window, progress, label_load):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        #update_loading_status(file_paths)
        
        if file_paths:
            global load_csvs_instance
            load_csvs_instance = LoadCSVs(list(file_paths),new_window, progress, label_load)
            load_csvs_instance.set_max_current_in_impulses()
            load_csvs_instance.calculate_average_histogram()
            listbox.delete(0, tk.END)
            files_color(listbox)
            average_histogram_text = "\n".join([f"{k:<10}: {v:>5}" for k, v in load_csvs_instance.average_histogram.items()])
            average_histogram_label.config(text="Average Current Histogram\n\n" + average_histogram_text)

    def on_select(event, listbox, histogram_label):
        if listbox.curselection():
            selected_key = listbox.get(listbox.curselection())
            histogram = load_csvs_instance.pairs[selected_key]['voltage'].current_histogram
            histogram_text = "\n".join([f"{k:<10}: {v:>5}" for k, v in histogram.items()])
            histogram_label.config(text=f"{selected_key} Current Histogram\n\n" + histogram_text)

    def plot_selected(listbox):
        if listbox.curselection():
            selected_key = listbox.get(listbox.curselection())
            load_csvs_instance.plot_measurements(selected_key)

    root = create_main_window()
    listbox = create_listbox(root)
    right_frame = create_right_frame(root)
    histogram_label, average_histogram_label = create_labels(right_frame)

    def create_input_fields(right_frame):
        setup_label = tk.Label(right_frame, text="Setup Intervals for Current Peaks searching")
        setup_label.pack(pady=5)

        input_frame = tk.Frame(right_frame)
        input_frame.pack(pady=20)

        enhance_start_label = tk.Label(input_frame, text="Start time shift [s]")
        enhance_start_label.grid(row=0, column=0, padx=5)

        enhance_start_entry = tk.Entry(input_frame)
        enhance_start_entry.grid(row=0, column=1, padx=5)
        enhance_start_entry.insert(0, "0.0")

        enhance_end_label = tk.Label(input_frame, text="End  time shift [s]")
        enhance_end_label.grid(row=0, column=2, padx=5)

        enhance_end_entry = tk.Entry(input_frame)
        enhance_end_entry.grid(row=0, column=3, padx=5)
        enhance_end_entry.insert(0, "0.0")

        submit_button = tk.Button(input_frame, text="Submit", command=lambda: enhance_selected_file(listbox, enhance_start_entry, enhance_end_entry))
        submit_button.grid(row=0, column=4, columnspan=4, pady=10)

        separator = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        return enhance_start_entry, enhance_end_entry
    def time_to_index(time_value, frequency):
        """
        Convert a given time value to an index based on the file frequency.

        :param time_value: Time value in seconds.
        :param frequency: Frequency of the file in Hz.
        :return: Corresponding index.
        """
        return int(time_value * frequency)
    
    def enhance_selected_file(listbox, enhance_start_entry, enhance_end_entry):
        if listbox.curselection():
            selected_key = listbox.get(listbox.curselection())
            start_index = time_to_index(float(enhance_start_entry.get()), load_csvs_instance.pairs[selected_key]['voltage'].frequency)
            end_index = time_to_index(float(enhance_end_entry.get()), load_csvs_instance.pairs[selected_key]['voltage'].frequency)

            load_csvs_instance.pairs[selected_key]['voltage'].CUSTOM_START_INDEX = start_index
            load_csvs_instance.pairs[selected_key]['voltage'].CUSTOM_END_INDEX = end_index
            load_csvs_instance.pairs[selected_key]['voltage'].set_impulses_indexies()
            load_csvs_instance.set_max_current_in_impulses()
            load_csvs_instance.calculate_average_histogram()
            # Update the histograms in the GUI
            histogram = load_csvs_instance.pairs[selected_key]['voltage'].current_histogram
            histogram_text = "\n".join([f"{k:<10}: {v:>5}" for k, v in histogram.items()])
            histogram_label.config(text=f"{selected_key} Current Histogram\n\n" + histogram_text)

            average_histogram_text = "\n".join([f"{k:<10}: {v:>5}" for k, v in load_csvs_instance.average_histogram.items()])
            average_histogram_label.config(text="Average Current Histogram\n\n" + average_histogram_text)

            # Update the listbox item color based on the new histogram values
            listbox.delete(0, tk.END)
            files_color(listbox)

            print(f"Enhanced {selected_key} from index time {float(enhance_start_entry.get())} {start_index} \n {float(enhance_end_entry.get())} to {end_index}")

    def files_color(listbox):
        for key in load_csvs_instance.pairs.keys():
            if load_csvs_instance.pairs[key]['voltage'].current_histogram.get('0-3 A') == 100 or load_csvs_instance.pairs[key]['voltage'].current_histogram.get('0-3 A') == 200:
                listbox.insert(tk.END, key)
                listbox.itemconfig(tk.END, {'fg': 'yellow'})
            elif len(load_csvs_instance.pairs[key]['voltage'].impulses) != 100 and len(load_csvs_instance.pairs[key]['voltage'].impulses) != 200:
                listbox.insert(tk.END, key)
                listbox.itemconfig(tk.END, {'fg': 'red'})
            else:
                listbox.insert(tk.END, key)

    enhance_start_entry, enhance_end_entry = create_input_fields(right_frame)

    listbox.bind('<<ListboxSelect>>', lambda event: on_select(event, listbox, histogram_label))

    def plot_average_histogram():
        load_csvs_instance.plot_average_histogram()

    gui_buttins(start_loading, plot_selected, listbox, right_frame, average_histogram_label, plot_average_histogram)

    root.mainloop()

def gui_buttins(start_loading, plot_selected, listbox, right_frame, average_histogram_label, plot_average_histogram):
    plot_button = tk.Button(right_frame, text="Show Chart", command=lambda: plot_selected(listbox))
    plot_button.pack(pady=20, anchor='center')

    plot_average_button = tk.Button(right_frame, text="Plot Average Histogram", command=plot_average_histogram)
    plot_average_button.pack(pady=20, anchor='center')

    separator = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill=tk.X, padx=5, pady=5)

    open_button = tk.Button(right_frame, text="Load CSV Files", command=lambda: start_loading(listbox, average_histogram_label))
    open_button.pack(pady=0, side=tk.BOTTOM, anchor='center')
