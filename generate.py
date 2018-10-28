#!/usr/bin/env python
from nsuolymp import *
import argparse, sys
import validate


def main(argv = None):
	# type: (Optional[List[str]]) -> int
	# handle cmd arguments
	parser = argparse.ArgumentParser(description = "Generate tests with simple batch-like script.")
	parser.add_argument('script', help = "name of .cmd script to run in order to generate test inputs", nargs = '?', default = "gen.cmd")
	parser.add_argument('-s', '--solution', help = "name of etalon solution to be used to generate outputs")
	parser.add_argument('-v', '--validate', help = "run validation of generated test inputs", action = "store_true")
	parser.add_argument('-c', '--compile', help = "force compilation of generators from sources", action = "store_true")
	parser.add_argument('-e', '--stop-on-error', help = "stop script after first error encountered", action = "store_true")
	parser.add_argument('-q', '--quiet', help = "print only results (no intermediate messages)", action = "store_true")
	parser.add_argument('-a', '--all', help = "perform full generation and validation of complete problem (implies -c, -v, -e, -s)", action = "store_true")
	args = parser.parse_args()
	if args.all:
		args.compile = args.validate = args.stop_on_error = True
		if args.solution is None:
			args.solution = list(filter(lambda s: '_ok' in s, get_sources_in_problem(solutions = True)))[0]

	cfg = Config(quiet = args.quiet, stop = args.stop_on_error)
	script_results = compile_results = generate_results = test_results = None
	validate_results = None     # type: Optional[Union[str, List[str]]]

	# helper for return code & stop-on-error
	err = [0]
	on_error = error_handling_helper(cfg, err)

	try:
		# parse the script
		script_results = parse_generation_script(args.script)
		if isinstance(script_results, str):
			on_error(1, force = True)
		assert(not isinstance(script_results, str))
		test_indices = [line.test for line in script_results]

		# compile various stuff
		compile_list = []   # type: List[str]
		for gen in set([line.generator for line in script_results]):
			add_source_to_compile_list(cfg, gen, compile_list, args.compile)
		if args.solution is not None:
			args.solution = add_source_to_compile_list(cfg, args.solution, compile_list, args.compile)
		if args.validate:
			for src in get_sources_in_problem(validator = True, checker = True):
				add_source_to_compile_list(cfg, src, compile_list, args.compile)
		compile_results = compile_sources(compile_list, cfg)
		if len(compile_results[1]) > 0:
			on_error(2)

		# execute script line by line to generate inputs
		generate_results = execute_generation_script(cfg, script_results)
		if len(generate_results[1]) > 0:
			on_error(3)

		# validate the tests just generated
		if args.validate:
			test_inputs = [get_test_input(k) for k in test_indices]
			validate_results = validate_many_tests(test_inputs, cfg.quiet)
			if len(validate_results) > 0:
				on_error(4)

		# generate output files by running the solution
		if args.solution is not None:
			test_results = (args.solution, check_solution(cfg, args.solution, ','.join(str(i) for i in test_indices), True))
			if not all(res.verdict == 'A' for res in test_results[1]):
				on_error(5)

	except (StopError):
		pass

	# print all results in one batch
	if script_results is not None:
		print_parse_generation_script(script_results)
	if compile_results is not None:
		print_compile_results(compile_results)
	if generate_results is not None:
		print_execute_generation_script(generate_results)
	if validate_results is not None:
		print_validate_results(validate_results)
	if test_results is not None:
		print_solutions_results([test_results])

	return err[0]

if __name__ == "__main__":
	sys.exit(main())
