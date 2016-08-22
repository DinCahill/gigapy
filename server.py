#!/usr/bin/env python3

import collections
import csv
import gigapy
import glob
import numpy as np
import os
import time
from scipy.signal import filtfilt, butter
import profiles

temps = collections.deque([])
smooth_temps = []


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


profile = profiles.normal
sysprofile = profiles.low

if __name__ == '__main__':
    OHMDir = 'G:\Downloads\OpenHardwareMonitor'
    OHMFile = glob.glob(
        os.path.join(OHMDir, '*.csv'))[-1]

    with open(OHMFile, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        headings = enumerate(next(csvreader))
        temp_index = -1
        for k, v in headings:
            if 'temperature' in v:
                print('Heading {0}: {1}'.format(k, v))
                temp_index = k
        temp = -1
        pwm = -1
        currentpwm = -1
        currentsyspwm = -1
        i = 0
        for line in csvreader:
            pass

        b, a = butter(3, 0.05)
        while True:
            try:
                line = next(csvreader)
                try:
                    while True:
                        line = next(csvreader)
                except StopIteration:
                    pass

                temp = float(line[temp_index])
                temps.append(temp)
                if len(temps) >= 13:
                    smooth_temps = filtfilt(b, a, temps)
                if len(temps) > 100:
                    temps.popleft()
                smooth_temp = smooth_temps[-1] if len(smooth_temps) > 0 else 0
                pwm = profile(smooth_temp)
                syspwm = sysprofile(smooth_temp)
                print(
                    'temp: {0}, smooth_temp: {1}, pwm: {2}, vrm: {3}'.format(
                        temp, smooth_temp, pwm, syspwm))

                if i == 3:
                    changed = False
                    for new, current, fanid in zip(
                            [pwm, syspwm], [currentpwm, currentsyspwm], [0, 1]):
                        if new != current:
                            gigapy.setFixedSpeed(fanid, pwm)
                            changed = True
                    if changed:
                        gigapy.startThermald()
                        currentpwm = pwm
                        currentsyspwm = syspwm
                    i = 0
                else:
                    i += 1
            except StopIteration:
                pass

            time.sleep(1)
