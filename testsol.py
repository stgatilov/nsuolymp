#!/usr/bin/env python
from nsuolymp import *
import argparse, sys

def main(argv = None):
    # type: (Optional[List[str]]) -> int
    # handle cmd arguments
    parser = argparse.ArgumentParser(description = "Runs one or many solutions on current tests.")
    parser.add_argument('solutions', help = "one or several solutions: either executables or source files (* or @ means 'all solutions')", nargs = '+')
    parser.add_argument('-q', '--quiet', help = "print only results (no intermediate messages)", action = "store_true")
    parser.add_argument('-e', '--stop-on-error', help = "stop script after first error encountered", action = "store_true")
    parser.add_argument('-c', '--compile', help = "force compilation of solutions and checker from sources", action = "store_true")
    parser.add_argument('-g', '--gen-output', help = "overwrite test output files with answers generated by solution", action = "store_true")
    parser.add_argument('-s', '--stress', help = "stress test solutions; generator with arguments must be specified just afterwards in double quotes", metavar = "GEN")
    parser.add_argument('-t', '--tl', help = "specify time limit in seconds (by default taken from problem statement, 0 means 'no limit')", type = float)
    parser.add_argument('-m', '--ml', help = "specify memory limit in megabytes (by default taken from problem statement, 0 means 'no limit')", type = float)
    parser.add_argument('-i', '--tests', help = "comma-separated list of test names/globs/ranges to run on (by default all tests are used)", metavar = "TESTS")
    args = parser.parse_args()

    test_all_solutions = ('*' in args.solutions or '@' in args.solutions)
    if args.gen_output:
        if args.stress:
            print("Option --stress is incompatible with --gen-output")
            return 200
        if test_all_solutions or len(args.solutions) != 1:
            print("Exactly one solution must be specified with --gen-output")
            return 201

    cfg = Config(quiet = args.quiet, stop = args.stop_on_error)
    # resolve limits
    if args.tl is None or args.ml is None:
        problem_limits = read_limits(find_problem_statement())
        if problem_limits is not None:
            if args.tl is None:
                args.tl = convert_default_time_limit(problem_limits[0])
            if args.ml is None:
                args.ml = problem_limits[1]
    if args.tl and args.tl > 0.0:
        cfg.tl = args.tl
    if args.ml and args.ml > 0.0:
        cfg.ml = args.ml

    compile_results = test_results = stress_results = None

    # helper for return code & stop-on-error
    err = [0]
    on_error = error_handling_helper(cfg, err)

    try:
        # find out what should we compile
        compile_list = []
        if args.compile or (not if_exe_exists('check') and not if_exe_exists('interactor')):
            compile_list.extend(get_sources_in_problem(checker = True))
        if args.compile and args.stress:
            compile_list.extend(get_sources_in_problem(validator = True))

        # find out solutions we have to compile
        sol_prelist = []        # type: List[str]
        if test_all_solutions:
            if args.compile:
                compile_list.extend(get_sources_in_problem(solutions = True))
        else:
            for sol in args.solutions:
                exe = add_source_to_compile_list(cfg, sol, compile_list, args.compile)
                sol_prelist.append(exe)

        # compile all the necessary sources
        compile_results = compile_sources(compile_list, cfg)
        if len(compile_results[1]) > 0:
            on_error(10)

        # filter only solutions which are present
        solutions_list = []     # type: List[str]
        if test_all_solutions:
            solutions_list = get_solutions()
        else:
            for sol in sol_prelist:
                if is_solution(sol):
                    solutions_list.append(sol)
                else:
                    printq(cfg.quiet, colored_verdict('W', "Solution %s does not exist" % sol))
                    on_error(11)

        # test all solutions
        if args.stress:
            generator = args.stress.split()
            for seed in stress_test_solutions(cfg, generator, solutions_list):
                stress_results = seed
                on_error(12, True)
        elif args.gen_output:
            solution = solutions_list[0]
            test_results = [(solution, check_solution(cfg, solution, args.tests, True))]
        else:
            test_results = check_many_solutions(cfg, solutions_list, args.tests)
    except (StopError):
        pass

    if compile_results is not None:
        print_compile_results(compile_results)
    if test_results is not None:
        print_solutions_results(test_results)
    if stress_results is not None:
        print(colored_verdict('W', "Stopped on a problematic test generated with seed = " + str(stress_results)))

    return err[0]


if __name__ == "__main__":
    sys.exit(main())
