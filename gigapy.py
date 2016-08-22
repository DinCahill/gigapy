#!/usr/bin/env python3

import os
import xmltodict
import argparse
import sys
import psutil
import subprocess
import time

SIVDir = 'C:\Program Files (x86)\Gigabyte\SIV'
ProfileDir = os.path.join(SIVDir, 'Profile')
thermaldPath = os.path.join(SIVDir, 'thermald.exe')


class MyParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def getFixedSpeed(fan):
    FanFile = os.path.join(ProfileDir, 'FanConfig{0}.xml'.format(fan))
    if not os.path.exists(FanFile):
        print('Fan does not exist!')
        exit(1)

    with open(FanFile, 'r') as fd:
        doc = xmltodict.parse(fd.read())
        print('FanFile: {0}'.format(FanFile))
        return doc['SmartFanConfig']['FixedModeConfig']['StartPWM']


def setFixedSpeed(fan, speed):
    FanFile = os.path.join(ProfileDir, 'FanConfig{0}.xml'.format(fan))
    if not os.path.exists(FanFile):
        print('Fan does not exist!')
        exit(1)

    with open(FanFile, 'r+') as fd:
        doc = xmltodict.parse(fd.read())
        doc['SmartFanConfig']['FixedModeConfig']['StartPWM'] = speed

        fd.seek(0)
        fd.write(xmltodict.unparse(doc, pretty=True))
        fd.truncate()
        print('FanFile: {0}'.format(FanFile))


def startThermald():
    for pid in psutil.pids():
        try:
            if psutil.Process(pid).name() == "thermald.exe":
                p = psutil.Process(pid)
                p.terminate()
                try:
                    p.wait(timeout=10)
                    print('Killed thermald')
                except psutil.TimeoutExpired:
                    print('error: Timeout for killing thermald expired')
                    exit(1)
        except psutil.NoSuchProcess as e:
            print('warning: NoSuchProcess')

    thermald = subprocess.Popen(thermaldPath)
    time.sleep(1.5)
    thermald.terminate()
    thermald.wait()
    print('Started thermald')


if __name__ == '__main__':
    parser = MyParser(description='Set Gigabyte Fan Speed')
    parser.add_argument('--fan', type=int, help='Fan ID')
    parser.add_argument('--pwm', type=int, help='PWM Value')
    args = parser.parse_args()
    if args.fan is None:
        parser.error('Please select a fan')

    if args.pwm is None:
        print('Fan {0}: {1}'.format(args.fan, getFixedSpeed(args.fan)))

    else:
        setFixedSpeed(args.fan, args.pwm)
        print('Fan {0}: {1}'.format(args.fan, args.pwm))
        startThermald()
