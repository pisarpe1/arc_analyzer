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
    listbox = tk.Listbox(root)
    listbox.pack(pady=20)

    histogram_label = tk.Label(root, text="")
    histogram_label.pack(pady=20)

    average_histogram_label = tk.Label(root, text="")
    average_histogram_label.pack(pady=20)

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
                listbox.insert(tk.END, key)
            average_histogram_text = "\n".join([f"{k}: {v}" for k, v in load_csvs_instance.average_histogram.items()])
            average_histogram_label.config(text=average_histogram_text)

    def on_select(event):
        if listbox.curselection():
            selected_key = listbox.get(listbox.curselection())
            histogram = load_csvs_instance.pairs[selected_key]['voltage'].current_histogram
            histogram_text = "\n".join([f"{k}: {v}" for k, v in histogram.items()])
            histogram_label.config(text=histogram_text)

    def plot_selected():
        if listbox.curselection():
            selected_key = listbox.get(listbox.curselection())
            load_csvs_instance.plot_measurements(selected_key)

    listbox.bind('<<ListboxSelect>>', on_select)

    plot_button = tk.Button(root, text="Plot Selected", command=plot_selected)
    plot_button.pack(pady=20)

    open_button = tk.Button(root, text="Open Files", command=open_files)
    open_button.pack(pady=20)

    root.mainloop()
