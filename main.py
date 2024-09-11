import csv
import pathlib

import matplotlib.pyplot as plt
import numpy as np
from numpy import fft

PATHTOFILES = pathlib.Path("csv_files/")


def smooth_moving_window(l, window_len=99, include_edges='On'):
        if window_len % 2 == 0:
            raise ValueError('>window_len< kwarg in function >smooth_moving_window< must be odd')

        # print l
        l = np.array(l, dtype=float)
        w = np.ones(window_len, 'd')

        if include_edges == 'On':
            edge_list = np.ones(window_len)
            begin_list = [x * l[0] for x in edge_list]
            end_list = [x * l[-1] for x in edge_list]

            s = np.r_[begin_list, l, end_list]

            y = np.convolve(w / w.sum(), s, mode='same')
            y = y[window_len + 1:-window_len + 1]

        elif include_edges == 'Wrap':
            s = np.r_[2 * l[0] - l[window_len - 1::-1], l, 2 * l[-1] - l[-1:-window_len:-1]]
            y = np.convolve(w / w.sum(), s, mode='same')
            y = y[window_len:-window_len + 1]

        elif include_edges == 'Off':
            y = np.convolve(w / w.sum(), l, mode='valid')

        else:
            raise NameError('Error in >include_edges< kwarg of function >smooth_moving_window<')

        return y


def get_pulse(voltage_vals: list[float]):
    pulse_interval: list = []

    for val in voltage_vals:
        if val < -200:
            pulse_interval.append(True)
        else:
            pulse_interval.append(False)

    intervals = []
    start_flag = False
    end_false = False
    interval = {'start': None,
                'end': None}
    for i in range(len(pulse_interval)):
        if i < len(pulse_interval)-1:
            if not pulse_interval[i]:
                if pulse_interval[i + 1]:
                    interval['start'] = i + 1
                    start_flag = True

            if pulse_interval[i]:
                if not pulse_interval[i + 1]:
                    interval['end'] = i + 65
                    end_false = True

        if start_flag and end_false:
            if interval['end'] - interval['start'] > 100:
                intervals.append(interval)
            start_flag = False
            end_false = False
            interval = {'start': None,
                        'end': None}

    return intervals


def load_files():
    files_path = []
    for child in PATHTOFILES.iterdir():
        files_path.append(child)

    data_dict: dict = {}

    for file_path in files_path:
        with (open(file_path, newline="") as csvfile):
            print(csvfile.name)
            reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
            list_of = enumerate(reader)
            full_name = csvfile.name.split('\\')[-1][0:-4]
            name = full_name.split('\\')[-1][0:-1]
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


def volt_in_intervals(data_dict):

    for key in data_dict.keys():
        data_dict[key]['pulse_curr_in_ranges'] = []
        for interval in data_dict[key]['pulse_ranges']:
            interval_voltage = []
            for i in range(interval['start'], interval['end']):
                interval_voltage.append(data_dict[key]['current'][i])
            data_dict[key]['pulse_curr_in_ranges'].append(interval_voltage)

    return data_dict


def data_filter(data_dict):

    for key in data_dict.keys():
        # filtr sumu  vystrelky hodnot
        values_cur = data_dict[key]['current']
        values_vol = data_dict[key]['voltage']

        try:
            # current filter
            for i in range(1, len(values_cur)):
                if values_cur[i] == 0:
                    if values_cur[i + 2] == 0:
                        if values_cur[i + 1] > 10:
                            values_cur[i + 1] = 0
        except:
            pass

        try:
            # voltage filter
            for i in range(1, len(values_vol)):
                if values_vol[i] > 0:
                    values_vol[i] = 0
                if values_vol[i] < -750:
                    values_vol[i] = -730
        except:
            pass
        rng = get_pulse(data_dict[key]['voltage'])
        data_dict[key]['voltage_fit'] = smooth_moving_window(np.array(data_dict[key]['voltage']))
        data_dict[key]['pulse_ranges'] = rng
        data_dict[key]['pulse_number'] = len(rng)

        data_dict = volt_in_intervals(data_dict)

    return data_dict


def result():
    data_dict_raw = load_files()
    data_dict = data_filter(data_dict_raw)


    peak_num = 0
    peak_num_vol = 0
    inter_0_50 = 0
    inter_50_80 = 0
    inter_80_120 = 0
    inter_more_120 = 0

    for key in data_dict.keys():
        values = data_dict[key]['current']
        val_vol = smooth_moving_window(data_dict[key]['voltage'])
        # rozdeleni do intervalu
        try:
            for i in range(1, len(values)):
                if values[i - 1] <= values[i]:
                    if values[i] > values[i + 1]:
                        peak_num += 1
                        if values[i] <= 50:
                            inter_0_50 += 1
                        elif values[i] <= 80:
                            inter_50_80 += 1
                        elif values[i] <= 120:
                            inter_80_120 += 1
                        else:
                            inter_more_120 += 1

            for i in range(1, len(val_vol)):
                if val_vol[i - 1] >= val_vol[i]:
                    if val_vol[i] < val_vol[i + 1]:
                        peak_num_vol += 1

        except:
            pass

        values = np.array(data_dict[key]['current'])
        times = np.array(data_dict[key]['time'])
        spectrum = fft.fft(values)
        freq = fft.fftfreq(len(spectrum))

        #plt.plot(freq, abs(spectrum))

        wave_plt = plt
        wave_plt.figure(layout="constrained")
        wave_plt.xlabel("")
        wave_plt.ylabel("")

        wave_plt.plot(times, values, label="label", marker='o')
        print(f"{key}  numbers of peaks 0-50:{inter_0_50} 50-80:{inter_50_80} 80-120:{inter_80_120} 120+:{inter_more_120}")
        # giving a title to my graph
        wave_plt.title(key)

        wave_plt.show()



        x = times
        y = data_dict[key]['voltage']
        y1 = data_dict[key]['voltage_fit']
        print(len(y), len(y1))
        plt.plot(x, y)
        plt.plot(x, y1, )
        plt.show()


def result2():
    data_dict_raw = load_files()
    data_dict = data_filter(data_dict_raw)

    for key in data_dict.keys():
        time = data_dict[key]['time']
        current = data_dict[key]['current']

        inter_0_50 = 0
        inter_50_80 = 0
        inter_80_120 = 0
        inter_more_120 = 0

        for interval in data_dict[key]['pulse_curr_in_ranges']:
            max_val = max(interval)
            if max_val <= 50:
                inter_0_50 += 1
            elif max_val <= 80:
                inter_50_80 += 1
            elif max_val <= 120:
                inter_80_120 += 1
            else:
                inter_more_120 += 1

        print(f"{key}\n \tnumbers of peaks: {len(data_dict[key]['pulse_curr_in_ranges'])}\n \t0-50:{inter_0_50}\n \t50-80:{inter_50_80}\n \t80-120:{inter_80_120}\n \t120+:{inter_more_120}")

        for xc in data_dict[key]['pulse_ranges']:

            plt.axvline(x=data_dict[key]['time'][xc['start']], color='green', ls=':')
            plt.axvline(x=data_dict[key]['time'][xc['end']], color='red', ls=':')

        plt.plot(time, current, 'o')
        plt.plot(time, current)
        plt.plot(time, abs(data_dict[key]['voltage_fit']))
        plt.show()


if __name__ == '__main__':
    print('runing')
    result2()

    # frek = 100Hz
    # osciloskop 10 dilku na obrazovce x
    # hlavicka 7 , 13, 15, 16, 20, 24
    # prvy soubor napeti druhá proud

    # histogram 0-50
    #           50-80
    #           80-120
