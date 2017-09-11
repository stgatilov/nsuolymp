#!/usr/bin/env python
from nsuolymp import *
import argparse, sys

def main(argv = None):
	# handle cmd arguments
	parser = argparse.ArgumentParser(description = "Compiles given source code files.")
	parser.add_argument('sources', help = "list of source files to compile (may be empty, * to compile everything possible)", nargs = '*')
	parser.add_argument('-q', '--quiet', help = "print only results (no intermediate messages)", action = "store_true")
	parser.add_argument('-e', '--stop-on-error', help = "stop script after first error encountered", action = "store_true")
	parser.add_argument('-v', '--validator', help = "compile validator", action = "store_true")
	parser.add_argument('-c', '--checker', help = "compile checker & interactor", action = "store_true")
	parser.add_argument('-s', '--solutions', help = "compile all solutions", action = "store_true")
	parser.add_argument('-g', '--generators', help = "compile all generators", action = "store_true")
	parser.add_argument('-a', '--all', help = "compile all problem stuff (shortcut for -v -c -s -g)", action = "store_true")
	args = parser.parse_args(argv)
	if args.all:
		args.validator = args.checker = args.solutions = args.generators = True
	if not (args.validator or args.checker or args.solutions or args.generators or len(args.sources) > 0):
		parser.print_help()
		return 100

	cfg = Config(quiet = args.quiet, stop = args.stop_on_error)

	compile_list = []
	if '*' in args.sources or '@' in args.sources:
		all_sources = filter(is_source, glob.glob('*'))
		compile_list.extend(list(all_sources))
	else:	
		compile_list.extend(args.sources)
		compile_list.extend(get_sources_in_problem(validator = args.validator, checker = args.checker, solutions = args.solutions, generators = args.generators))

	compile_results = compile_sources(compile_list, cfg)
	print_compile_results(compile_results)

	ret_code = 0
	if compile_results[1]:
		ret_code = 1
	return ret_code


if __name__ == "__main__":
	sys.exit(main())
