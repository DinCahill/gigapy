import csv
import glob
import threading
import os
import time


def readTemp(csvreader, index):
    line = next(csvreader)
    return float(line[index])


class Reader(threading.Thread):
    pass


class OHMReader(Reader):

    def __init__(self, OHMDir, qOut):
        super(OHMReader, self).__init__()
        self.OHMDir = OHMDir
        self.OHMFile = glob.glob(
            os.path.join(self.OHMDir, '*.csv'))[-1]

        self.qOut = qOut

    def run(self):
        with open(self.OHMFile, newline='') as csvfile:
            csvreader = csv.reader(csvfile)

            # Search for the CPU temperature column
            headings = enumerate(next(csvreader))
            temp_index = -1
            for k, v in headings:
                if 'temperature' in v:
                    print('Using {0} from OHM'.format(v))
                    temp_index = k

            # Discard existing rows
            for line in csvreader:
                pass

            while True:
                time.sleep(1)
                try:
                    while True:
                        self.qOut.put((readTemp(csvreader, temp_index),))
                except StopIteration:
                    pass
