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
	class StopError(Exception):
		pass
	class ret:
		code = 0
	def on_error(code, force = False):
		# type: (int, bool) -> None
		ret.code = ret.code or code
		if cfg.stop or force:
			raise StopError()

	# look at solution involved
	sol = sol_noext = None
	if args.solution is not None:
		sol = args.solution
		sol_noext = path.splitext(sol)[0]

	try:
		# parse the script
		script_results = parse_generation_script(args.script)
		if isinstance(script_results, str):
			on_error(1, force = True)
		assert(not isinstance(script_results, str))
		test_indices = [line.test for line in script_results]

		# compile various stuff
		sources = list(set([line.generator for line in script_results]))
		if not args.compile:
			sources = list(filter(lambda gen: not if_exe_exists(gen), sources))
		sources = list(filter(lambda f: path.splitext(f)[0] in sources, get_sources_in_problem(generators = True)))
		if sol is not None and is_solution(sol):
			if args.compile or is_source(sol) and not has_java_task(sol):
				sources.append(sol)
		if args.validate:
			src = get_sources_in_problem(validator = True, checker = True)
			if not args.compile:
				src = list(filter(lambda f: not if_exe_exists(path.splitext(f)[0]), src))
			sources += src
		compile_results = compile_sources(sources, cfg)
		if len(compile_results[1]) > 0:
			on_error(2)

		# execute it line by line to generate inputs
		generate_results = execute_generation_script(cfg, script_results)
		if len(generate_results[1]) > 0:
			on_error(3)

		# validate the whole test set
		if args.validate:
			validate_results = []
			for idx in test_indices:
				f = get_test_input(idx)
				ok = validate_test(f, cfg.quiet)
				if ok is None:
					validate_results = "not found"
					break
				if not ok:
					validate_results.append(f)
			if len(validate_results) > 0:
				on_error(4)

		# generate output files by running the solution
		if isinstance(sol, str) and isinstance(sol_noext, str):
			test_results = (sol_noext, check_solution(cfg, sol_noext, ','.join(str(i) for i in test_indices), True))
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

	return ret.code

if __name__ == "__main__":
	sys.exit(main())
