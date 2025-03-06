import csv
from src.load_files.csv_parsers.csv_parser import CSVFileParser


class ParseGwInsteakCSV(CSVFileParser):
    def __init__(self, file_path):
        super().__init__(file_path)
        self._voltage_flag = False
        self.set_name()
        self.raw_data = self.parse_file()

    def parse_file(self):
        with open(self.path, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",", quotechar='"')
            file = list(reader)

        for index, row in enumerate(file):
            if index < self.type_index:
                self.parse_head(row)
            elif index == self.type_index:
                self.data_type_voltage()
            else:
                self.parse_data(row)
        return file

    def data_type_voltage(self):
        """
        Determines if the data type is voltage based on the 'Vertical Units' header.
        This method checks if the 'Vertical Units' in the header is 'V' (voltage).
        If it is, it initializes the '_data' dictionary with an empty list for the 'voltage' key
        and returns True. Otherwise, it initializes the '_data' dictionary with an empty list
        for the 'current' key and returns False.
        Returns:
            bool: True if the 'Vertical Units' is 'V', False otherwise.
        """

        if self.head["Vertical Units"] == "V":
            self._data["voltage"] == []
            self._voltage_flag = True
        elif self.head["Vertical Units"] == "A":
            self._data["current"] == []
            self._voltage_flag = False
        else:
            raise ValueError(
                f"Vertical Units [{self.head['Vertical Units']}] type not recognized inside the file {self.path}"
            )

    def parse_head(self, row):
        if row[0] in self.head:
            self.head[row[0]].append(row[1:])
        else:
            self.head[row[0]] = row[1:][-1]

    def parse_data(self, row):
        self.data["time"].append(float(row[0]))
        if self._voltage_flag == True:
            self._data["voltage"].append(float(row[1]))
        else:
            self._data["current"].append(float(row[1]))

    def set_name(self):
        self.name = self.full_name[0:-5]

class DataType(enumerate):
    V = '[V]'
    A = '[A]'
    S = '[s]'
    Hz = '[Hz]'
