#!/usr/bin/env python
from nsuolymp import *
import argparse, sys

def main(argv = None):
	# type: (Optional[List[str]]) -> int
	# handle cmd arguments
	parser = argparse.ArgumentParser(description = "Normalizes EOLN of all tests (to current OS native).")
	args = parser.parse_args(argv)

	files_list = get_tests_inputs() + list(map(get_output_by_input, get_tests_inputs()))
	for fname in files_list:
		with open(fname, 'rb') as f:
			data = f.read()
		with open(fname, 'wb') as f:
			f.write(convert_eoln(data))

	return 0;

if __name__ == "__main__":
	sys.exit(main())
