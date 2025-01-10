

from copy import deepcopy
import csv
import matplotlib.pyplot as plt

from src.results.data_filtr import DataFiltr 



class CSVFile:
    HEAD_INDEX_END = 24
    def __init__(self, path: str):
        self.path = path
        self.raw_data_head: dict = {}
        self.raw_data: list = []
        self.time_data: list = []

        self.raw_file = self.load_csv()
        self.full_name = None
        self.name = self.set_names()

    def load_csv(self):
        with open(self.path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            file = list(reader)
        head = {}
        data = []
        time = []
        for index, row in enumerate(file):
            if index < self.HEAD_INDEX_END:
                if row[0] in head:
                    head[row[0]].append(row[1:])
                else:
                    head[row[0]] = row[1:][-1]
            else:
                if index > self.HEAD_INDEX_END:
                    time.append(float(row[0]))
                    data.append(float(row[1]))
        self.raw_data_head = head
        self.raw_data = data 
        self.time_data = time  
        return file
    
    def set_names(self):
        self.full_name = self.path.split('/')[-1]
        return self.full_name[0:-5]
    
    def get_full_head(self):
        return self.raw_data_head

    def get_name(self) -> str:
        return self.name
    
    def get_path(self) -> str:
        return self.path

class DataType(enumerate):
    V = '[V]'
    A = '[A]'
    S = '[s]'
    Hz = '[Hz]'


class LoadCSV(CSVFile, DataFiltr):

    # frek = 100Hz
    # osciloskop 10 dilku na obrazovce x
    # hlavicka 7 , 13, 15, 16, 20, 24
    # prvy soubor napeti druhá proud

    # histogram 0-50
    #           50-80
    #           80-120
    ENHANCE_START_INDEX = 2
    CUSTOM_START_INDEX = 0
    ENHANCE_END_INDEX = 5
    CUSTOM_END_INDEX = 0

    def __init__(self, path: str):
        self.raw = CSVFile(path)
        self.data = deepcopy(self.raw.raw_data)
        self.time_data = deepcopy(self.raw.time_data)
        self.voltage_flag = False
        self.current_flag = not self.voltage_flag
        self.frequency = self.set_frequency()
        self.current_histogram = self.reset_histogram()
        self.set_flag()
        self.filter_data()

        self.impulses = []
        if self.voltage_flag:
            self.impulses = self.find_impulses()
            self.set_impulses_indexies()

    def reset_histogram(self):
        self.current_histogram = { '0-3 A': 0,
        '0-50 A': 0,
        '50-80 A': 0,
        '80-120 A': 0,
        '120+ A': 0}
        return self.current_histogram

    def set_histogram(self):
        self.current_histogram = self.reset_histogram()
        for impulse in self.impulses:
            if impulse['max_current'] < 3:
                self.current_histogram['0-3 A'] += 1
            elif impulse['max_current'] < 50:
                self.current_histogram['0-50 A'] += 1
            elif impulse['max_current'] < 80:
                self.current_histogram['50-80 A'] += 1
            elif impulse['max_current'] < 120:
                self.current_histogram['80-120 A'] += 1
            else:
                self.current_histogram['120+ A'] += 1

    def get_impuls_start_index(self, impulse) -> int:
        start = impulse['peak'] - self.get_average_impulse_len() * self.ENHANCE_START_INDEX
        start = start - self.CUSTOM_START_INDEX
        if start < 0:
            return 0
        return start
    
    def get_impuls_end_index(self, impulse) -> int:
        end = impulse['peak'] + self.get_average_impulse_len() * self.ENHANCE_END_INDEX
        end = end + self.CUSTOM_END_INDEX
        if end > len(self.time_data):
            return len(self.time_data) - 1
        return end
    
    def set_impulses_indexies(self):
        for impulse in self.impulses:
            impulse['start'] = self.get_impuls_start_index(impulse)
            impulse['end'] = self.get_impuls_end_index(impulse)

    def plot_data(self):
        smoothed_data = self.smoothed_voltage_data(self.voltage_flag)   
        plt.figure(figsize=(10, 5))
        #plt.plot(self.time_data, self.raw.raw_data, label='Raw Data', linestyle='--')
        plt.plot(self.time_data, self.data, label='Filtered Data', linestyle='-')
        plt.plot(self.time_data, smoothed_data, label='Smoothed Data_gausian')

        for impulse in self.impulses:
            plt.axvspan(self.time_data[impulse['start']],
                        self.time_data[impulse['end']], color='red', alpha=0.3)
        plt.xlabel('Time (s)')
        plt.ylabel('Value')
        plt.title(f'Data Plot for {self.name}')
        plt.legend()
        plt.grid(True)

        return plt
    
    def get_average_impulse_len(self):
        average = int(sum([impulse['time_index_len'] for impulse in self.impulses]) / len(self.impulses))

        return average 

    def find_impulses(self, threshold=-100, min_distance=1000):
        impulses = []
        data = self.smoothed_voltage_data(self.voltage_flag)
        for i in range(1, len(data)):
            if data[i] < threshold and data[i] < data[i - 1] and (i + 1 < len(data) and data[i] < data[i + 1]):
                if not impulses or (i - impulses[-1]['peak_time'] > min_distance):
                    start_index = i
                    while i < len(data) and data[i] < threshold:
                        i += 1
                    end_index = i
                    length = self.time_data[end_index] - self.time_data[start_index]
                    length_index = end_index - start_index
                    impulses.append({'peak_time': self.time_data[start_index],
                                     'time_length': length,
                                     'time_index_len': length_index,
                                     'peak': int(start_index),
                                     'max_current': 0,
                                     })
                    
        if len(impulses) != 100:
            if  len(impulses) == 200:
                pass
            else:
                print(f"Warning: Expected 100 pulses, but found {len(impulses)}")

        self.impulses = impulses
        return impulses
    

    def get_data(self):
        return self.data
    
    def get_time_data(self):
        return self.time_data

    @property
    def name(self):
        return self.raw.get_name()
    
    def get_impulses(self):
        return self.impulses

    def set_flag(self):
        if self.raw.raw_data_head['Vertical Units'] == 'V':
            self.voltage_flag = True
            self.current_flag = not self.voltage_flag
        else:
            self.voltage_flag = False
            self.current_flag = not self.voltage_flag

    def set_frequency(self):
        """Return frequency of the signal in Hz"""
        return 1 / float(self.raw.raw_data_head['Sampling Period'])

    def time(self):
        """Return time in seconds"""
        return self.raw.raw_data_head['Time']
    
    def filter_data(self):
        if self.voltage_flag:
            new_vals = [self.filter_positive(value) for value in self.data]
        else:
            new_vals =  [self.filter_negative(value) for value in self.data]
        new_vals = self.noise_to_zero(new_vals)
        self.data = new_vals




class LoadCSVs:
    def __init__(self, paths: list,root, progress, label):
        self.paths = paths
        self.pairs: dict[str, dict[str, LoadCSV]] = {}
        self.all_files: list[LoadCSV] = self.load_files(root, progress, label)
        self.average_histogram = self.reset_histogram()
        self.set_max_current_in_impulses()
    
    def reset_histogram(self):
        self.average_histogram = { '0-3 A': 0,
        '0-50 A': 0,
        '50-80 A': 0,
        '80-120 A': 0,
        '120+ A': 0}
        return self.average_histogram
    
    def get_average_histogram(self):
        print(self.average_histogram)
        return self.average_histogram

    def calculate_average_histogram(self):
        self.reset_histogram()
        valid_files = 0 
        for key in self.pairs.keys():
            print(key ,self.pairs[key]['voltage'].current_histogram)
            if self.pairs[key]['voltage'].current_histogram['0-3 A'] != 100:
                for range in self.pairs[key]['voltage'].current_histogram:
                    self.average_histogram[range] += self.pairs[key]['voltage'].current_histogram[range]
                valid_files += 1         
        print(valid_files)
        for range in self.average_histogram:
            self.average_histogram[range] = round(self.average_histogram[range] / valid_files, 1)
        self.get_average_histogram()
        
    
    def set_max_current_in_impulses(self):
        for pair in self.pairs.keys():
            for impuls in self.pairs[pair]['voltage'].impulses:
                self.get_max_current_in_impulse(self.pairs[pair]['current'].data, impuls)
            self.pairs[pair]['voltage'].set_histogram()
        
    def load_files(self, root, progress, label):
        files = []
        for i, path in enumerate(self.paths):
            file = LoadCSV(path)    
            self.set_pairs(file)
            files.append(file)
            progress['value'] = (i + 1) / len(self.paths) * 100 
            label.config(text=f"Loading {file.raw.full_name}...")
            root.update_idletasks() 
        self.check_pairs()
        label.config(text="Loading Complete!")

        return files
    
    def get_max_current_in_impulse(self, current, impulse):
        impulse['max_current'] = max(current[impulse['start']:impulse['end']])

    def plot_measurements(self, key):
        voltage = self.pairs[key]['voltage']
        current = self.pairs[key]['current']
        plot = None
        if voltage is not None:
            plot  = voltage.plot_data()
        if current is not None:
            plot.plot(current.get_time_data(), current.get_data(), label='Current Data', linestyle='-')
        plot.xlabel('Time [s]')
        plot.ylabel('Value [V]; [A]')
        plot.title(f'{key}')
        plot.legend()
        plot.grid(True)
        plot.axhline(y=3, color='blue', linestyle='--', linewidth=0.3, label='3 A')
        plot.axhline(y=50, color='blue', linestyle='--', linewidth=0.3, label='50 A')
        plot.axhline(y=80, color='blue', linestyle='--', linewidth=0.3, label='80 A')
        plot.axhline(y=120, color='blue', linestyle='--', linewidth=0.3, label='120 A')
        plot.show()

    def plot_histogram(self, key):
        histogram = self.pairs[key]['voltage'].current_histogram
        categories = list(histogram.keys())
        values = list(histogram.values())

        plt.figure(figsize=(10, 5))
        plt.bar(categories, values, color='skyblue')
        plt.xlabel('Current Range')
        plt.ylabel('Frequency')
        plt.title(f'Current Histogram for {key}')
        plt.grid(axis='y')
        plt.show()

    def plot_average_histogram(self):
        categories = list(self.average_histogram.keys())
        values = list(self.average_histogram.values())

        plt.figure(figsize=(10, 5))
        plt.bar(categories, values, color='skyblue', label='Average Histogram')

        # Plot each individual histogram
        for key in self.pairs.keys():
            histogram = self.pairs[key]['voltage'].current_histogram
            values = list(histogram.values())
            plt.plot(categories, values, marker='o', linestyle='-', label=f'{key} Histogram')

        plt.xlabel('Current Range')
        plt.ylabel('Frequency')
        plt.title('Average Current Histogram and Individual Histograms')
        plt.legend()
        plt.grid(axis='y')
        plt.show()

    def set_pairs(self, file):
        if file.name in self.pairs.keys():
            if file.voltage_flag:
                self.pairs[file.name]['voltage'] = file
            else:
                self.pairs[file.name]['current'] = file
        else:
            self.pairs[file.name] = {'voltage': None, 'current': None}
            if file.voltage_flag:
                self.pairs[file.name]['voltage'] = file
            else:
                self.pairs[file.name]['current'] = file

    def check_pairs(self):
        for key in self.pairs.keys():
            if self.pairs[key]['voltage'] is None:
                print(f"Voltage file is missing for {key}")
            if self.pairs[key]['current'] is None:
                print(f"Current file is missing for {key}")
           
