#!python3

# Downloads source code of all submits in the selected tour into "submits" local subdirectory.
# Used e.g. for giving solutions from WSO first round to a sponsor (in case it was negotiated before the contest).
#
# Usage:
#   1) Copy this script into nsuolymp directory.
#   2) Ensure that correct credentials and nsuts URL are set in config.
#   3) Run this script with olympiadId and tourId from nsuts as command line arguments.

import sys, argparse
from datetime import datetime
from nsuts import *
from nsuolymp_cfg import *

parser = argparse.ArgumentParser(description = 'Downloads source code for all submits from nsuts')
parser.add_argument('olympiadId', help = 'ID of source olympiad in nsuts')
parser.add_argument('tourId', help = 'ID of source tour in nsuts')
parser.add_argument('--teamMap', help = 'path to tsv file with team names: {teamId} {teamName}')
parser.add_argument('--taskMap', help = 'path to tsv file with task names: {taskId} {taskName}')
args = parser.parse_args()

teamMap = None
if args.teamMap:
    teamMap = {}
    for l in open(args.teamMap, 'r').readlines():
        [xid, xname] = l.split('\t')[0:2]
        teamMap[xid] = xname

taskMap = None
if args.taskMap:
    taskMap = {}
    for l in open(args.taskMap, 'r').readlines():
        [xid, xname] = l.strip('\n').split('\t')[0:2]
        taskMap[xid] = xname

if path.isdir('submits'):
    assert len(os.listdir('submits')) == 0, 'Directory "submits" is not empty!'
else:
    os.makedirs('submits')

nsuts = NsutsClient(nsuts_options)
nsuts.auth()
nsuts.select_olympiad(args.olympiadId)
nsuts.select_tour(args.tourId)

res = nsuts.get_admin_queue(limit = 99999)
data = list(sorted(res['submissions'], key = lambda x: int(x['id'])))

for submit in data:
    submitId = submit['id']
    teamId = submit['teamId']
    if teamMap is not None:
        teamId = teamMap[teamId]
    taskId = submit['taskId']
    if taskMap is not None:
        taskId = taskMap[taskId]

    res = submit['res']
    if not isinstance(res, str):
        res = 'Q'   # queued
    status = res[-1] + str(len(res))

    smtime = datetime.strptime(submit['smtime'], '%Y-%m-%d %H:%M:%S')
    timestamp = datetime.strftime(smtime, '%y%m%d%H%M')

    compiler = submit['langName'].lower()
    if 'java' in compiler:
        ext = 'java'
    elif 'python' in compiler:
        ext = 'py'
    elif 'kotlin' in compiler:
        ext = 'kt'
    elif 'pascal' in compiler or 'delphi' in compiler:
        ext = 'kt'
    elif 'c++' in compiler:
        ext = 'cpp'
    elif 'c#' in compiler:
        ext = 'cs'
    else:
        ext = 'txt'

    filename = '%s_%s_%s_%s_%s.%s' % (taskId, teamId, timestamp, status, submitId, ext)
    print(filename)

    try:
        source_result = nsuts.get_solution_source(submitId)
    except Exception as e:
        print('WARNING: cannot download source code for ID = %s' % submitId)
        print(traceback.format_exc())
        continue
    assert isinstance(source_result, bytes)

    with open(path.join('submits', filename), 'wb') as f:
        f.write(source_result)
