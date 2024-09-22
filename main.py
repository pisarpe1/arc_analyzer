import csv
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pylab

from GUI import get_files#, get_gui

PATHTOFILES = pathlib.Path("csv_files/")


def thresholding_algo(y):
    lag = 5  # average and std. are based on past 5 observations
    threshold = 3.5  # signal when data point is 3.5 std. away from average
    influence = 0.5  # between 0 (no influence) and 1 (full influence)

    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0]*len(y)
    stdFilter = [0]*len(y)
    avgFilter[lag - 1] = np.mean(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y)):
        if abs(y[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
            if y[i] > avgFilter[i-1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i-1]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.mean(filteredY[(i-lag+1):i+1])
            stdFilter[i] = np.std(filteredY[(i-lag+1):i+1])

    return dict(signals = np.asarray(signals),
                avgFilter = np.asarray(avgFilter),
                stdFilter = np.asarray(stdFilter))


def smooth_moving_window(l, window_len=51, include_edges='On'):
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
    #dic = thresholding_algo(voltage_vals)
    pulse_interval: list = []

    for val in voltage_vals:
        if val < -350:
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
            if interval['end'] - interval['start'] > 150:
                intervals.append(interval)
            start_flag = False
            end_false = False
            interval = {'start': None,
                        'end': None}

    return intervals


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


def volt_in_intervals(data_dict):

    for key in data_dict.keys():
        data_dict[key]['pulse_curr_in_ranges'] = []
        for interval in data_dict[key]['pulse_ranges']:
            interval_voltage = []
            for i in range(interval['start'], interval['end']):
                interval_voltage.append(data_dict[key]['current'][i])
            data_dict[key]['pulse_curr_in_ranges'].append(interval_voltage)

    return data_dict


def data_filter(data_dict_in):
    data_dict = data_dict_in

    for key in data_dict.keys():
        data_dict[key]['time_shift'] = [0] * len(data_dict[key]['time'])

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

    return data_dict


def result2(paths):
    data_dict_raw = load_files(paths)
    data_dict = data_filter(data_dict_raw)
    data_dict = volt_in_intervals(data_dict)

    for key in data_dict.keys():
        time = data_dict[key]['time']
        current = data_dict[key]['current']

        inter_0_3 = 0
        inter_0_50 = 0
        inter_50_80 = 0
        inter_80_120 = 0
        inter_more_120 = 0

        for interval in data_dict[key]['pulse_curr_in_ranges']:
            max_val = max(interval)
            if max_val > 0:
                if max_val <= 50:
                    inter_0_50 += 1
                elif max_val <= 80:
                    inter_50_80 += 1
                elif max_val <= 120:
                    inter_80_120 += 1
                else:
                    inter_more_120 += 1
            elif max_val < 3:
                inter_0_3 += 1

        current_peaks = inter_0_3 + inter_0_50 + inter_50_80 + inter_80_120 + inter_more_120

        print(f"{key}\n \tdetected volt peaks: {len(data_dict[key]['pulse_curr_in_ranges'])} "
              f"\n \t0-3:\t{inter_0_3}"
              f"\n \t3-50:\t{inter_0_50}"
              f"\n \t50-80:\t{inter_50_80}"
              f"\n \t80-120:\t{inter_80_120}"
              f"\n \t120+:\t{inter_more_120}"
              f"\n \tdetected peaks \t{current_peaks}")

        for xc in data_dict[key]['pulse_ranges']:

            plt.axvline(x=data_dict[key]['time'][xc['start']], color='green', ls=':', linewidth=0.5)
            plt.axvline(x=data_dict[key]['time'][xc['end']], color='red', ls=':', linewidth=0.5)

        for yc in [3, 50, 80, 120]:

            plt.axhline(y=yc, color='tan')

        plt.text(min(data_dict[key]['time']), 0, inter_0_3, fontsize=15)
        plt.text(min(data_dict[key]['time']), 25, inter_0_50, fontsize=15)
        plt.text(min(data_dict[key]['time']), 65, inter_50_80, fontsize=15)
        plt.text(min(data_dict[key]['time']), 100, inter_80_120, fontsize=15)
        plt.text(min(data_dict[key]['time']), 130, inter_more_120, fontsize=15)

        # plt.plot(time, current, 'o')
        plt.plot(time, current)
        # plt.plot(data_dict[key]['time'], data_dict[key]['voltage'])
        # plt.plot(data_dict[key]['time'], data_dict[key]['voltage_fit'])
        plt.title(f'{key} '
                  f'\nvolt peaks: {len(data_dict[key]['pulse_curr_in_ranges'])}; current peaks: {current_peaks}')
        plt.show()


if __name__ == '__main__':
    print('runing')
    paths = get_files()
    result2(paths)

    # frek = 100Hz
    # osciloskop 10 dilku na obrazovce x
    # hlavicka 7 , 13, 15, 16, 20, 24
    # prvy soubor napeti druhá proud

    # histogram 0-50
    #           50-80
    #           80-120
