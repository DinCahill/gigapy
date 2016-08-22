import csv
import glob
import threading
import os
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


def readTemp(csvreader, index):
    line = next(csvreader)
    return float(line[index])


class Reader(threading.Thread):
    pass


class OHMFileSystemEventHandler(PatternMatchingEventHandler):
    patterns = ['*.csv']

    def setCSV(self, OHMFile):
        self.OHMFile = os.path.normpath(OHMFile)

        self.csvfile = open(self.OHMFile, newline='')
        self.csvreader = csv.reader(self.csvfile)

        # Search for the CPU temperature column
        headings = enumerate(next(self.csvreader))
        self.temp_index = -1
        for k, v in headings:
            if 'temperature' in v:
                print('Using {0} from OHM'.format(v))
                self.temp_index = k

        # Discard existing rows
        for line in self.csvreader:
            pass

    def __init__(self, OHMFile, qOut, qNewCSV):
        super(OHMFileSystemEventHandler, self).__init__()
        self.qOut = qOut
        self.qNewCSV = qNewCSV
        self.setCSV(OHMFile)

    def on_modified(self, event):
        src = os.path.normpath(event.src_path)
        if self.OHMFile != src:
            self.qNewCSV.put(src)

        try:
            while True:
                self.qOut.put(readTemp(self.csvreader, self.temp_index))
        except StopIteration:
            return


class OHMReader(Reader):

    def __init__(self, OHMDir, qOut):
        super(OHMReader, self).__init__()
        self.OHMDir = OHMDir
        self.OHMFile = glob.glob(
            os.path.join(self.OHMDir, '*.csv'))[-1]

        self.qOut = qOut

    def setup(self, observer):
        qNewCSV = Queue()
        event_handler = OHMFileSystemEventHandler(
            self.OHMFile, self.qOut, qNewCSV)
        watch = observer.schedule(
            event_handler, self.OHMDir)
        return (qNewCSV, event_handler, watch)

    def newCSV(self, observer, qNewCSV, watch):
        newOHMFile = qNewCSV.get()
        if self.OHMFile == newOHMFile:
            return False
        observer.unschedule(watch)
        self.OHMFile = newOHMFile
        print('New CSV: {}'.format(self.OHMFile))
        return True

    def run(self):
        observer = Observer()
        qNewCSV, event_handler, watch = self.setup(observer)
        observer.start()
        while True:
            if self.newCSV(observer, qNewCSV, watch):
                qNewCSV, event_handler, watch = self.setup(observer)
            else:
                continue
