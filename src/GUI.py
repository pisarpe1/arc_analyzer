import tkinter as tk
from tkinter import Tk, filedialog
from tkinter.filedialog import askopenfilenames

from load_files.load_csv import LoadCSVs




def get_files():
    Tk().withdraw()
    filenames = askopenfilenames()

    return filenames if filenames else []

def output_values_and_plot():
    root = tk.Tk()
    root.title("CSV Plotter")
    root.geometry("800x600")  # Set the window size to 800x600

    listbox = tk.Listbox(root, width=50)
    listbox.pack(pady=20, side=tk.LEFT, fill=tk.BOTH, expand=True)

    right_frame = tk.Frame(root)
    right_frame.pack(pady=20, side=tk.RIGHT, fill=tk.BOTH, expand=True)

    histogram_label = tk.Label(right_frame, text="File Current Histogram")
    histogram_label.pack(pady=20)

    separator = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill=tk.X, padx=5, pady=5)

    average_histogram_label = tk.Label(right_frame, text="Average Current Histogram")
    average_histogram_label.pack(pady=20)

    separator = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(fill=tk.X, padx=5, pady=5)

    def open_files():
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if file_paths:
            global load_csvs_instance
            load_csvs_instance = LoadCSVs(list(file_paths))
            load_csvs_instance.all_files = load_csvs_instance.load_files()
            load_csvs_instance.set_max_current_in_impulses()
            load_csvs_instance.calculate_average_histogram()
            listbox.delete(0, tk.END)
            for key in load_csvs_instance.pairs.keys():
                if load_csvs_instance.pairs[key]['voltage'].current_histogram.get('inter_0_3') == 100:
                    listbox.insert(tk.END, key)
                    listbox.itemconfig(tk.END, {'fg': 'red'})
                else:
                    listbox.insert(tk.END, key)
            average_histogram_text = "\n".join([f"{k}: {v}" for k, v in load_csvs_instance.average_histogram.items()])
            average_histogram_label.config(text="Average Current Histogram\n\n" + average_histogram_text)

    def on_select(event):
        if listbox.curselection():
            selected_key = listbox.get(listbox.curselection())
            histogram = load_csvs_instance.pairs[selected_key]['voltage'].current_histogram
            histogram_text = "\n".join([f"{k}: {v}" for k, v in histogram.items()])
            histogram_label.config(text=f"{selected_key} Current Histogram\n\n" + histogram_text)

    def plot_selected():
        if listbox.curselection():
            selected_key = listbox.get(listbox.curselection())
            load_csvs_instance.plot_measurements(selected_key)

    listbox.bind('<<ListboxSelect>>', on_select)

    plot_button = tk.Button(right_frame, text="Plot Open", command=plot_selected)
    plot_button.pack(pady=20, side=tk.BOTTOM, anchor='center')

    open_button = tk.Button(right_frame, text="Load Files", command=open_files)
    open_button.pack(pady=20, side=tk.BOTTOM, anchor='center')

    root.mainloop()
