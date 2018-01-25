#!/usr/bin/env python3
import random
import argparse
import requests
import sys
import pygit2
import os
import datetime
from executeQueryLog import MonitorThread


class EvalCommits:
    logFile = ''
    commits = []

    QUERY = """
        SELECT * WHERE { graph ?g { ?s ?p ?o .}} LIMIT 10"""

    def __init__(
            self,
            endpoint='http://localhost:5000/sparql',
            repoDir='',
            logFile='',
            logDir='/var/logs',
            runs=100):

        self.endpoint = endpoint
        self.logDir = logDir
        self.logFile = os.path.join(self.logDir, logFile)
        self.repoDir = repoDir
        try:
            response = requests.post(endpoint, data={'query': self.QUERY}, headers={'Accept': 'application/json'})
        except Exception:
            raise Exception('Cannot access {}'.endpoint)

        if response.status_code == 200:
            pass
        else:
            raise Exception('Something wrong with sparql endpoint.')

        try:
            self.repo = pygit2.Repository(self.repoDir)
        except Exception:
            raise Exception('{} is no repository'.format(self.repoDir))

        if isinstance(runs, int):
            self.runs = runs
        else:
            raise Exception('Expect integer for argument "runs", got {}, {}'.format(runs, type(runs)))

        # collect commits
        commits = {}
        i = 0
        for commit in self.repo.walk(self.repo.head.target, pygit2.GIT_SORT_REVERSE):
            commits[i] = (str(commit.id))
            i += 1
        self.commits = commits
        self.interval = round(len(commits.items())/self.runs)
        print('Found {} commits. Interval will be {}'.format(len(commits.items()), str(self.interval)))

    def runBenchmark(self):
        i = 0

        for pos, ref in self.commits.items():
            with open(self.logFile, 'a') as executionLog:
                if pos % self.interval == 0:
                    start, end = self.postRequest(ref)
                    data = [str(pos), str(end - start), str(start), str(end), str(ref)]
                    executionLog.write(' '.join(data) + '\n')
                    print(' '.join(data))
                    i = i + 1

    def postRequest(self, ref):
        start = datetime.datetime.now()
        res = requests.post(
            self.endpoint + '/' + ref,
            data={'query': self.QUERY},
            headers={'Accept': 'application/json'})
        end = datetime.datetime.now()
        print('Result:', res, res.status_code)
        return start, end


def parseArgs(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-E', '--endpoint',
        type=str,
        default='http://localhost:5000/sparql',
        help='Link to the SPARQL-Endpoint')

    parser.add_argument(
        '-L',
        '--logdir',
        type=str,
        default='/var/logs/',
        help='The link where to log the benchmark')

    parser.add_argument(
        '-O',
        '--observeddir',
        default='.',
        help='The directory that should be monitored')

    parser.add_argument(
        '-P',
        '--processid',
        type=int,
        help='The command name of the process to be monitored')

    parser.add_argument(
        '-runs', '--runs',
        type=int,
        default=100)

    parser.add_argument(
        '-R',
        '--repodir',
        type=str)

    return parser.parse_args()


if __name__ == '__main__':
    args = parseArgs(sys.argv[1:])
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')

    bm = EvalCommits(
        endpoint=args.endpoint,
        repoDir=args.repodir,
        logFile='eval.commits.log',
        logDir=args.logdir,
        runs=args.runs)

    mon = MonitorThread(logDir=args.logdir, logFile='memory.commits.log')

    mon.setstoreProcessAndDirectory(
        pid=args.processid,
        observedDir=args.observeddir)

    mon.start()
    bm.runBenchmark()
    mon.stop()
