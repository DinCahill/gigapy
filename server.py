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


def readTemp(csvreader, temps):
    line = next(csvreader)
    temp = float(line[temp_index])
    temps.append(temp)  # Keep a deque of temperatures
    return temp


profile = profiles.normal
sysprofile = profiles.low

if __name__ == '__main__':
    OHMDir = 'G:\Downloads\OpenHardwareMonitor'
    OHMFile = glob.glob(
        os.path.join(OHMDir, '*.csv'))[-1]

    with open(OHMFile, newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        # Search for the CPU temperature column
        headings = enumerate(next(csvreader))
        temp_index = -1
        for k, v in headings:
            if 'temperature' in v:
                print('Heading {0}: {1}'.format(k, v))
                temp_index = k

        # Discard existing rows
        for line in csvreader:
            pass

        currentpwm = -1
        currentsyspwm = -1
        i = 3
        b, a = butter(3, 0.05)  # Low-pass filter

        print('Collecting 13 temperatures... ', end='')
        while True:
            time.sleep(1)
            # Get the latest row. If there isn't a new one, skip to the sleep
            try:
                temp = readTemp(csvreader, temps)
                # If there are multiple new rows, get the latest
                try:
                    while True:
                        temp = readTemp(csvreader, temps)
                except StopIteration:
                    pass

                # Needs at least 13 temperatures. Print them out as we go
                if len(temps) < 13:
                    print('{0} '.format(temp), end='', flush=True)
                    continue
                if len(temps) == 13:
                    print('{0} '.format(temp), flush=True)

                # Limit the deque length
                if len(temps) > 100:
                    temps.popleft()

                smooth_temps = filtfilt(b, a, temps)
                smooth_temp = smooth_temps[-1]
                pwm = profile(smooth_temp)
                syspwm = sysprofile(smooth_temp)
                print(
                    'temp: {0}, smooth_temp: {1}, pwm: {2}, vrm: {3}'.format(
                        temp, smooth_temp, pwm, syspwm))

                # Set the fan speed after every fourth temperature reading
                if i == 3:
                    changed = False  # Only set the speed if it has changed
                    for new, current, fanid in zip(  # Set each fan individually
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
