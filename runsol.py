#!/usr/bin/env python
from nsuolymp import *
import argparse, sys

def main(argv = None):
    # type: (Optional[List[str]]) -> int
    # handle cmd arguments
    parser = argparse.ArgumentParser(description = "Run given solution executable with time/memory measurement and limits.")
    parser.add_argument('solution', help = "name of solution/executable to run (enclose into double quotes if run with parameters)", nargs='+')
    parser.add_argument('-t', '--tl', help = "specify time limit in seconds (default: no limit)", type = float)
    parser.add_argument('-m', '--ml', help = "specify memory limit in megabytes (default: no limit)", type = float)
    parser.add_argument('-i', '--interactive', help = "run with interactor", action = "store_true")
    parser.add_argument('-q', '--quiet', help = "print only results (no intermediate messages)", action = "store_true")
    args = parser.parse_args()

    tl = None
    ml = None
    # resolve limits
    if args.tl and args.tl > 0.0:
        tl = args.tl
    if args.ml and args.ml > 0.0:
        ml = args.ml

    # check if solution has many parameters in quotes
    solution = args.solution
    if len(solution) == 1:
        solution = solution[0].split()
    if len(solution) == 1:
        solution = solution[0]

    res = controlled_run_solution(solution, tl, ml, args.interactive, args.quiet)

    name = solution if type(solution) == str else ' '.join(solution)
    data = [(name, [res])]
    print_solutions_results(data)
    
    return 0 if res.verdict == 'A' else 1

if __name__ == "__main__":
    sys.exit(main())
