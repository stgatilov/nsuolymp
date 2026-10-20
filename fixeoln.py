#!/usr/bin/env python
from nsuolymp import *
import argparse, sys

def main(argv = None):
    # type: (Optional[List[str]]) -> int
    parser = argparse.ArgumentParser(description = "Normalizes EOLN of all tests (by default: to current OS native).")
    parser.add_argument('-w', '--windows', help = "convert to windows style (crlf)", action = "store_true")
    parser.add_argument('-l', '--linux', help = "convert to linux style (lf)", action = "store_true")
    # handle cmd arguments
    args = parser.parse_args(argv)
    style = ""
    if args.linux:
        style = "linux"
    if args.windows:
        style = "windows"

    input_list = get_tests_inputs()
    output_list = list(filter(path.isfile, map(get_output_by_input, get_tests_inputs())))
    files_list = input_list + output_list
    for fname in files_list:
        with open(fname, 'rb') as f:
            data = f.read()
        with open(fname, 'wb') as f:
            f.write(convert_eoln(data, style))

    return 0;

if __name__ == "__main__":
    sys.exit(main())
