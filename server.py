#!/usr/bin/env python3

import collections
import gigapy
import numpy as np
from scipy.signal import filtfilt, butter
import profiles
import readers
from queue import Queue


def readTemp(q, temps):
    temp = q.get()
    temps.append(temp)
    return temp


def readAllTemps(q, temps):
    temp = readTemp(q, temps)
    while not q.empty():
        temp = readTemp(q, temps)
    return temp


def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


if __name__ == '__main__':
    profile = profiles.normal
    sysprofile = profiles.low
    b, a = butter(3, 0.05)  # Low-pass filter

    temps = collections.deque([])
    currentpwm = -1
    currentsyspwm = -1
    i = 3

    q = Queue()
    ohm = readers.OHMReader('G:\Downloads\OpenHardwareMonitor', q)
    ohm.start()

    print('Collecting 13 temperatures... ', end='')
    while True:
        temp = readAllTemps(q, temps)

        # Needs at least 13 temperatures. Print them out as we go
        if len(temps) < 13:
            print('{0} '.format(temp), end='', flush=True)
            continue
        elif len(temps) == 13:
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
