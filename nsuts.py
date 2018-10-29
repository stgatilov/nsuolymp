#!/usr/bin/env python

from nsuolymp_cfg import *
from nsuolymp import *
from nsuts_base import NsutsClient
import argparse, sys
from time import sleep


#
# Actions
#

def submit(nsuts, task, filename):
    # type: (NsutsClient, int, str) -> int
    source_code = ""

    ext = guess_source_language(filename)
    if ext == 'java dir':
        ext = 'java'
        filename = path.join(filename, 'Task.java')
    compiler = nsuts_options['compiler'][ext]

    with open(filename) as source_file:
        source_code = source_file.read()

    nsuts.submit_solution(task, compiler, source_code)

    submit_id = nsuts.get_my_last_submit_id()
    if submit_id is None:
        raise Exception("Cannot find submit immediately after sending")
    return submit_id

def wait_status(nsuts, solutions):
    # type: (NsutsClient, List[Tuple[int, str]]) -> None
    queued, testing = len(solutions), 0

    max_filename_len = 1
    for id, filename in solutions:
        max_filename_len = max(max_filename_len, len(filename))
    
    while queued + testing > 0:
        print("Status:")
        queued, testing = 0, 0

        submits = nsuts.get_my_submits_status()
        submit_by_id = {}
        for submit in submits:
            submit_by_id[int(submit['id'])] = submit

        for id, filename in solutions:
            submit = submit_by_id[id]
            status = int(submit['status'])
            result = submit['result_line']
            if result is None:
                result = "."
            else:
                result = get_verdict_full_name(result[-1])

            print("  " + filename.ljust(max_filename_len, ' ') + " : " + result)

            if status == 1:
                queued += 1
            if status == 2:
                testing += 1
        sleep(3)

def main(argv = None):
    # type: (Optional[List[str]]) -> int
    parser = argparse.ArgumentParser(description = "Submit solutions to NSUTs")
    parser.add_argument('action', type = str, choices = ['submit'])
    parser.add_argument('task', type = int, help = "task id")
    parser.add_argument('-w', '--wait', help = 'wait and do not exit until all solutions will be tested.', action = 'store_true')
    parser.add_argument('solution', help = "one or several solution source files (* or @ means 'all solutions')", nargs = '+')
    args = parser.parse_args(argv)

    nsuts = NsutsClient(nsuts_options)
    nsuts.auth()
    nsuts.select_olympiad(nsuts_options['olympiad_id'])
    nsuts.select_tour(nsuts_options['tour_id'])

    solution_list = args.solution
    if '@' in solution_list or '*' in solution_list:
        solution_list = get_solution_sources()

    solution_ids = []
    for solution in solution_list:
        id = submit(nsuts, args.task, solution)
        sleep(1)
        solution_ids.append(id)

    if args.wait == True:
        wait_status(nsuts, list(zip(solution_ids, solution_list)))

    return 0

if __name__ == '__main__':
    sys.exit(main())
