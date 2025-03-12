import abc
from typing import Optional

from src.load_files.csv_parsers.Enum_file_types import Enum_input_source
import csv

def get_csv_source(path: str) -> Enum_input_source:
    empty_row: int = Enum_input_source.GwInstek
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if not row :  # Check if the row is empty
                empty_row = i
                break

            if row[0] is None or row[0] == 'Waveform Data':  # Check if the row is empty
                empty_row = i
                break

    if empty_row ==  Enum_input_source.GwInstek: 
        return Enum_input_source.GwInstek
    if empty_row ==  Enum_input_source.PicoScope:
        return Enum_input_source.PicoScope
    else:
        raise ValueError("The file is not a valid source")
 
class CSVFileParser(metaclass=abc.ABCMeta):
    def __init__(self, path: str, type: Enum_input_source):
        self._path = path
        self._type = type
        self._full_name = self._path.split("/")[-1]
        self._name = self.set_name()

        self._head_index: int = type

        self._head: dict[str, str] = {}
        self._data: dict[str, list] = {"time": [],
                                      "voltage": None,
                                      "current": None
                                     }
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def full_name(self) -> str:
        return self._full_name
    
    @property
    def type(self) -> int:
        return self._type.name
    
    @property
    def head_index(self) -> int:
        return self._head_index
    
    @property
    def head(self) -> dict[str, str]:
        return self._head
    
    @property
    def time(self) -> list:
        return self._data["time"]
    
    @property
    def voltage(self) -> Optional[list]:
        return self._data["voltage"]
    
    @property
    def current(self) -> Optional[list]:
        return self._data["current"]

    @abc.abstractmethod
    def set_name(self):
        raise NotImplementedError

    @abc.abstractmethod
    def parse_head(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def parse_data(self):
        raise NotImplementedError
