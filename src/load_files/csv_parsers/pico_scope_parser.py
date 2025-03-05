import csv
from src.load_files.csv_parsers.csv_parser import CSVFileParser


class ParserPicoScopeCSV(CSVFileParser):
    def __init__(self, file_path):
        super().__init__(file_path)
        self._data["voltage"] = []
        self._data["current"] = []
        self.set_name()


    def set_name(self):
        self.name = self.full_name[0:-4]

    def parse_head(self,file):

        for i in len(file[0]):
            key, value = file[0][i], file[1][i]
            self._head[key] = value
        
    def parse_data(self, row):
        self.data["time"].append(float(row[0]))
        self.data["voltage"].append(float(row[1]))  # Voltage
        self.data["current"].append(float(row[2]))  # Current

    def parse_file(self):
        with open(self.path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            file = list(reader)
            self.parse_head(file[:2])

        for index, row in enumerate(file):
                if index > self.type_index:
                    self.parse_data(row)
                else:
                    continue