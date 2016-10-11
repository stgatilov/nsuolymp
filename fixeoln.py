#!/usr/bin/env python
from nsuolymp import *

# normalize EOLN of tests
files_list = get_tests_inputs() + map(get_output_by_input, get_tests_inputs())
for fname in files_list:
	with open(fname, 'rb') as f:
		data = f.read()
	with open(fname, 'wb') as f:
		f.write(convert_eoln(data))
