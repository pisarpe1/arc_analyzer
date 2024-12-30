# This module contains the DataFiltr class, which is responsible for filtering data.


from scipy.ndimage import gaussian_filter # type: ignore

class DataFiltr:

    NOISE_BAND_WIDTH = 10
    def __init__(self, data):
        self.data = data

    def smoothed_voltage_data(self, flag) -> list:
        """
        Smoothing the data.
        """
        if flag:
            smoothed_data = gaussian_filter(self.data, sigma=30)
        else:
            smoothed_data = self.data  
        return smoothed_data

    def noise_to_zero(self, file) -> list:
        """
        Shifts time data to zero.
        """
        for i in range(0, len(file)):
            try:
                if file[i] == 0:
                    if file[i + 2] == 0:
                        if file[i + 1] > self.NOISE_BAND_WIDTH:
                            file[i + 1] = 0
            except IndexError:
                pass
            file[i] = self.lower_limit(file[i])
        return file

    def filter_negative(self, value):
        """
        Filters negative values.
        """
        if value < 0:
            value = 0
        return value
    
    def lower_limit(self, value):
        """
        Filters values below the limit.
        """
        if value < -3500:
            value = 0
        return value

    def upper_limit(self, value):
        """
        Filters values below the limit.
        """
        if value > 1000:
            value = 0
        return value

    def filter_positive(self, value):
        """
        Filters positive values.
        """
        if value > 0:
            value = 0
        return value