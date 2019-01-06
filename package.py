#!/usr/bin/env python
from nsuolymp import *
import argparse, sys
import validate, compile

def main(argv = None):
    # handle cmd arguments
    parser = argparse.ArgumentParser(description = "Packages tests into nsuts-ready zip.")
    parser.add_argument('-q', '--quiet', help = "print only results (no intermediate messages)", action = "store_true")
    parser.add_argument('--no-compile', help = "skip compilation of validator/checker/interactor", action = "store_true")
    parser.add_argument('--no-validator', help = "skip checking tests with validator", action = "store_true")
    parser.add_argument('--no-samples', help = "skip checking first tests against samples from statement", action = "store_true")
    parser.add_argument('--path', help = "path to output zip-file or directory (by default _packages in contest dir)", metavar = "PATH")
    parser.add_argument('--password', help = "protect the resulting zip package with specified password")
    args = parser.parse_args(argv)

    args.compile = not args.no_compile
    args.validator = not args.no_validator
    args.samples = not args.no_samples
    def arg(name):
        if getattr(args, name):
            return ["--" + name]
        return []

    # preparation
    cfg = Config(quiet = args.quiet, stop = True)
    packed_file_list = []
    ret_code = 0

    # compile checker (always if present), validator (unless disabled)
    if args.compile:
        ret_code = compile.main(["--checker"] + arg('validator') + arg('quiet'))
        # add sources if compiled from them
        packed_file_list += get_sources_in_problem(checker = True)
        if args.validator:
            packed_file_list += get_sources_in_problem(validator = True)
    if ret_code != 0:
        return ret_code

    # run validation (validator/samples checkes can be disabled)
    ret_code = validate.main(["--indices", "--output"] + arg('validator') + arg('samples') + arg('quiet'))
    if ret_code != 0:
        return ret_code

    # pack Windows executable of checker/interactor (always if present)
    if path.isfile('check.exe'):
        packed_file_list += ['check.exe']
    if path.isfile('interactor.exe'):
        packed_file_list += ['interactor.exe']

    # pack input/output test files
    packed_file_list += get_tests_inputs()
    if not if_exe_exists('interactor'):
        packed_file_list += map(get_output_by_input, get_tests_inputs())

    # deduce path to output archive
    output_filename = args.path
    if not output_filename:
        output_filename = path.join(os.pardir, '_packages')
    if len(path.splitext(output_filename)[1]) < 2:
        problem_name = path.basename(os.getcwd())
        output_filename = path.join(output_filename, problem_name + '.zip')

    # finally, create archive
    ok = create_flat_zip(packed_file_list, output_filename, quiet = args.quiet, password = args.password)
    if not ok:
        return 13

    return 0


if __name__ == "__main__":
    sys.exit(main())
