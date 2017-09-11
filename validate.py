#!/usr/bin/env python
from nsuolymp import *
import argparse, sys

def main(argv = None):
	# handle cmd arguments
	parser = argparse.ArgumentParser(description = "Validates tests in various ways.")
	parser.add_argument('-q', '--quiet', help = "print only results (no intermediate messages)", action = "store_true")
	parser.add_argument('-e', '--stop-on-error', help = "stop script after first error encountered", action = "store_true")
	parser.add_argument('-c', '--compile', help = "compile validator/checker if required", action = "store_true")
	parser.add_argument('-v', '--validator', help = "check all tests against validator", action = "store_true")
	parser.add_argument('-s', '--samples', help = "check that samples are taken from statements", action = "store_true")
	parser.add_argument('-i', '--indices', help = "check tests' names", action = "store_true")
	parser.add_argument('-o', '--output', help = "check that outputs for tests are present", action = "store_true")
	parser.add_argument('-a', '--all', help = "check everything (implies -v, -s, -i, -o)", action = "store_true")
	args = parser.parse_args(argv)
	if args.all:
		args.validator = args.samples = args.indices = args.output = True

	# check if no flag is specified
	if not (args.validator or args.samples or args.indices or args.output):
		parser.print_help()
		return 100

	# preparation
	cfg = Config(quiet = args.quiet, stop = args.stop_on_error)
	compile_results = validator_results = samples_results = indices_results = output_results = None

	# helper for return code & stop-on-error
	class StopError(Exception):
		pass
	class ret:
		code = 0
	def on_error(code):
		ret.code = ret.code or code
		if cfg.stop:
			raise StopError()

	try:
		# compile validator (if asked for)
		if args.compile:
			compile_results = compile_sources(get_sources_in_problem(validator = args.validator, checker = args.samples), cfg)
			if len(compile_results[1]) > 0:
				on_error(1)
		# run all types of validation
		if args.validator:
			validator_results = validate_all_tests(quiet = args.quiet)
			if len(validator_results) > 0:
				on_error(2)
		if args.samples:
			samples_results = check_samples(quiet = args.quiet)
			if len(samples_results) > 0:
				on_error(3)
		if args.indices:
			indices_results = validate_tests_indices()
			if len(indices_results) > 0:
				on_error(4)
		if args.output:
			output_results = check_output_files()
			if len(output_results) > 0:
				on_error(5)
	except (StopError):
		pass

	# print all results in one batch
	if compile_results is not None:
		print_compile_results(compile_results)
	if validator_results is not None:
		print_validate_results(validator_results)
	if samples_results is not None:
		print_check_samples_results(samples_results)
	if indices_results is not None:
		print_validate_indices_results(indices_results)
	if output_results is not None:
		print_check_output_files(output_results)

	return ret.code


if __name__ == "__main__":
	sys.exit(main())
