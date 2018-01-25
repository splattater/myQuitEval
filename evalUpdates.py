#!/usr/bin/env python3
import argparse
import sys
import os

class evalUpdates:
    memoryLog = ''
    executionLog = ''
    memoryEntries = []
    executionEntries = []

    def __init__(self, memoryLog, executionLog):
        if os.path.isfile(memoryLog):
            self.memoryLog = memoryLog
        else:
            print('File not found {}'.format(memoryLog))

        if os.path.isfile(executionLog):
            self.executionLog = executionLog
        else:
            print('File not found {}'.format(executionLog))

        self.readMemoryLog()
        self.readExecutionLog()

    def readMemoryLog(self):
        with open(self.memoryLog) as memlogFile:
            for line in list(memlogFile):
                print('M', line.split())

    def readExecutionLog(self):
        with open(self.executionLog) as executionFile:
            for line in list(executionFile):
                print('E', line.split())

    def evaluate(self):
        pass

def parseArgs(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-E',
        '--executionlog',
        type=str,
        help='The path/name of execution log file.')

    parser.add_argument(
        '-M',
        '--memorylog',
        type=str,
        help='The path/name of memory log file.')

    parser.add_argument(
        '-T',
        '--targetdir',
        default='.',
        help='The directory where the output should be stored.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parseArgs(sys.argv[1:])

    bm = evalUpdates(
        executionLog=args.executionlog,
        memoryLog=args.memorylog)

    bm.evaluate()
