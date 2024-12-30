


from copy import deepcopy
import csv

from results.data_filtr import DataFiltr



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

    def __init__(self, path: str):
        self.raw = CSVFile(path)
        self.data = deepcopy(self.raw.raw_data)
        self.time_data = deepcopy(self.raw.time_data)
        self.voltage_flag = False
        self.current_flag = not self.voltage_flag
        self.frequency= self.set_frequency()
        self.set_flag()
        self.filter_data()
        self.plot_data()

    def plot_data(self):
        impulses  = self.find_impulses()
        print(len(impulses))
        import matplotlib.pyplot as plt
        smoothed_data = self.smoothed_voltage_data(self.voltage_flag)   
        plt.figure(figsize=(10, 5))
        #plt.plot(self.time_data, self.raw.raw_data, label='Raw Data', linestyle='--')
        plt.plot(self.time_data, self.data, label='Filtered Data', linestyle='-')
        plt.plot(self.time_data, smoothed_data, label='Smoothed Data_gausian')
        plt.xlabel('Time (s)')
        plt.ylabel('Value')
        plt.title(f'Data Plot for {self.name}')
        plt.legend()
        plt.grid(True)
        plt.show()

    def find_impulses(self, threshold=-0.5, min_distance=10):
        impulses = []
        data = self.smoothed_voltage_data(self.voltage_flag)
        for i in range(1, len(data) - 1):
            if data[i] < threshold and data[i] < data[i - 1] and data[i] < data[i + 1]:
                if not impulses or (i - impulses[-1][0] > min_distance):
                    impulses.append((self.time_data[i], data[i]))
        if len(impulses) != 100:
            print(f"Warning: Expected 100 pulses, but found {len(impulses)}")
        return impulses

    def get_data(self):
        return self.data
    
    def get_time_data(self):
        return self.time_data

    @property
    def name(self):
        return self.raw.get_name()

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
    
    def get_x_units(self):
        return self.raw.raw_data_head['Horizontal Units']
    
    def get_y_units(self):
        return self.raw.raw_data_head['Vertical Units']
    
    def get_x_scale(self):
        return self.raw.raw_data_head['Horizontal Scale']
    
    def get_y_scale(self):
        return self.raw.raw_data_head['Vertical Scale']
    
    def filter_data(self):
        if self.voltage_flag:
            new_vals = [self.filter_positive(value) for value in self.data]
        else:
            new_vals =  [self.filter_negative(value) for value in self.data]
        new_vals = self.noise_to_zero(new_vals)
        self.data = new_vals




class LoadCSVs:
    def __init__(self, paths: list):
        self.paths = paths
        self.pairs: dict[str, dict[str, LoadCSV]] = {}
        self.all_files: list[LoadCSV] = self.load_files()

        
    def load_files(self):
        files = []
        for path in self.paths:
            file = LoadCSV(path)    
            self.set_pairs(file)
            files.append(file)
        self.check_pairs()

        return files

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
           
    
def load_files(paths):
    files_path = paths

    """for child in PATHTOFILES.iterdir():
        files_path.append(child)"""

    data_dict: dict = {}

    for file_path in files_path:
        with (open(file_path, newline="") as csvfile):
            reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
            list_of = enumerate(reader)
            full_name = csvfile.name.split('\\')[-1][0:-4]
            name = full_name.split('\\')[-1][0:-1]
            name =name.split('/')[-1]
            if name in data_dict.keys():
                dictval = data_dict[name]
            else:
                dictval = data_dict[name] = {'head': {},
                                             'voltage': [],
                                             'current': [],
                                             'time': [],
                                             }
            for index, row in list_of:
                if index > 24:
                    if full_name.endswith("1"):
                        dictval['time'].append(float(row[0].split(',')[0]))
                        dictval['voltage'].append(float(row[0].split(',')[1]))
                    else:
                        if float(row[0].split(',')[1]) > 0:
                            dictval['current'].append(float(row[0].split(',')[1]))
                        else:
                            dictval['current'].append(0.0)
                else:
                    if row[0] in dictval['head'].keys():
                        dictval['head'][row[0].split(',')[0]].append(row[0].split(',')[-1])
                    else:
                        dictval['head'][row[0].split(',')[0]] = []
                        dictval['head'][row[0].split(',')[0]].append(row[0].split(',')[-1])

    return data_dict