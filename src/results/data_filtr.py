# This module contains the DataFiltr class, which is responsible for filtering data.


from scipy.ndimage import gaussian_filter

class DataFiltr:

    NOISE_BAND_WIDTH = 10
    def __init__(self, data):
        self.data = data

    def smoothed_voltage_data(self, flag) -> list:
        """
        Smoothing the data.
        """
        if flag:
            smoothed_data = gaussian_filter(self.data, sigma=15)
        else:
            smoothed_data = self.data  
        return smoothed_data

    def noise_to_zero(self, file) -> list:
        """
        Shifts time data to zero.
        """
        for i in range(1, len(file)-2):
            if file[i] == 0:
                if file[i + 2] == 0:
                    if file[i + 1] > self.NOISE_BAND_WIDTH:
                        file[i + 1] = 0
        return file

    def filter_negative(self, value):
        """
        Filters negative values.
        """
        if value < 0:
            value = 0
        return value

    def filter_positive(self, value):
        """
        Filters positive values.
        """
        if value > 0:
            value = 0
        return value