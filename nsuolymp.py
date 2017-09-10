from __future__ import division
from __future__ import print_function 
from __future__ import absolute_import
import glob, fnmatch, os, shutil, re, itertools, operator, string, random, subprocess, copy, time, tempfile
import sarge							# simple wrapper over subprocess
import psutil							# for measuring CPU time and memory
import colorama							# for colored console output (cross-platform)
from os import path
from collections import namedtuple
from nsuolymp_cfg import *	# load some user preferences

# print all the given things if quiet = False
def printq(quiet, *args):
	if not quiet:
		print(*args)

# wrapper for copying files
def copyfile(src, dst):
	if path.abspath(src) == path.abspath(dst):
		return
	shutil.copyfile(src, dst)

# context manager to restore CWD easily
class save_cwd():
	def __enter__(self):
		self.cwd = os.getcwd();
	def __exit__(self, type, value, traceback):
		os.chdir(self.cwd)

# returns contents of file by given path (or None if it is not present)
def read_file_contents(filepath):
	if not filepath or not path.isfile(filepath):
		return None
	with open(filepath, 'rb') as f:
		return f.read()

# returns a function that can run given CMD line
# it supresses output to stdout/stderr if quiet is set
def cmd_runner(quiet = False):
	return sarge.capture_both if quiet else sarge.run

################################# Test files ###################################

# returns index of test from its filename
# absolute/relative, input/output does not matter
def get_test_index(f):
	name = path.splitext(path.basename(f))[0]
	return int(name)

# returns relative path to input file of test with given index
def get_test_input(idx):
	return 'tests/%s.in' % str(idx)

# returns output file by a path to input file
def get_output_by_input(f):
	return path.splitext(f)[0] + '.out'

# returns list of tests for current problem, sorted by test index
# CWD must be set to problem's directory
def get_tests_inputs():
	all_t = glob.glob('tests/*.in')
	def sort_key(name):
		try:
			return [0, get_test_index(name)]
		except ValueError:
			return [1, name]
	return sorted(all_t, key = sort_key)

# returns True when test passes user-specified filter (and False otherwise)
# filter_str is user-specified string with comma/space-separated tokens
# each token can be one of the following kinds:
#   min2  : matches exactly the test with given name 'min2'
#   3-7   : matches tests with numeric names from 3 to 7 inclusive
#   bad*  : matches any test whose name suits the glob 'bad*', e.g. 'bad', 'bad4', 'bad_luck'
# Note that the filter applies to basename of the test (no directories, no extension)
def if_test_passes_filter(test, filter_str):
	if filter_str is None:
		return True
	name = path.splitext(path.basename(test))[0]
	tokens = re.split(r'\,|\s', filter_str)
	for tok in tokens:
		if tok == name:
			return True
		if fnmatch.fnmatch(name, tok):
			return True
		match = re.match(r'(?x) ([0-9]+) - ([0-9]+) $', tok)
		if match is not None:
			try:
				rmin = int(match.group(1))
				rmax = int(match.group(2))
				idx = get_test_index(test)
				if idx >= rmin and idx <= rmax:
					return True
			except ValueError:
				pass
	return False

########################## Solutions and executables ###########################

# returns whether an executable file with given name (path) exists
# f must not have extension; checks for both f and f.exe
def if_exe_exists(f):
	return path.isfile(f) or path.isfile(f + '.exe')

# returns whether the given file is a java class file
def is_java_class(f):
	return ('$' not in f) and path.isfile(f + '.class')
	
# returns whether the given file is a directory with Task.class file
def has_java_task(f):
	return path.isdir(f) and path.isfile(path.join(f, 'Task.class'))
	
# returns whether a given file/directory is a problem solution
# f must be specified without extension
# in case of c++/pas, it must be executable
# in case of java, it is one of:
#   class file with .class extension    (proper way)
#   a directory with Task.class in it   (for old nsuts)
def is_solution(f):
	return if_exe_exists(f) or is_java_class(f) or has_java_task(f)

# returns list of solutions for current problem
# CWD must be set to problem's directory
# by convention its name must have predetermined prefix, also it must be executable
def get_solutions():
	all_files = glob.glob('*')
	files_noext = list(set([path.splitext(f)[0] for f in all_files]))
	files_sol = filter(lambda f : path.basename(f).startswith('sol_'), files_noext)
	solutions = filter(is_solution, files_sol)
	return list(sorted(solutions))

################################# Colored text #################################

# enable cross-platform colored text
colorama.init()

# returns bright version of a string
def color_highlight(s):
	return colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL

# taken from here: http://stackoverflow.com/a/14693789/556899
_ansi_color_regex = re.compile(r'\x1b[^m]*m')
# returns string with all the color escape codes removed
def stripcolor(s):
	res = _ansi_color_regex.sub("", s)
	return res

# pretty-print a table with colors
# workaround for texttable's inability to handle escape codes for colors
def draw_table_colored(data):
	if not data:
		return ''
	# manual table construction, supports colors
	k = len(data[0])
	widths = [0] * k
	for row in data:
		assert(len(row) == k)
		for i in range(k):
			widths[i] = max(widths[i], len(stripcolor(row[i])) + 2)
	horiz_line = '+'
	for w in widths:
		horiz_line = horiz_line + '-' * w + '+'
	res = [horiz_line]
	for row in data:
		row_str = '|'
		for i in range(k):
			start = ' ' + row[i]
			padding = widths[i] - len(stripcolor(start))
			row_str = row_str + start + ' ' * padding + '|'
		res = res + [row_str, horiz_line]
	return '\n'.join(res)

#################################### Verdicts ##################################

# returns full name of single-letter verdict
def get_verdict_full_name(verdict):
	vstr = "(none)"
	if verdict == 'A':
		vstr = "Accepted"
	if verdict == 'W':
		vstr = "Wrong answer"
	if verdict == 'P':
		vstr = "Presentation error"
	if verdict == 'J':
		vstr = "Jury error"
	if verdict == 'R':
		vstr = "Runtime error"
	if verdict == 'T':
		vstr = "Time limit exceeded"
	if verdict == 'M':
		vstr = "Memory limit exceeded"
	if verdict == 'D': # idleness limit exceeded
		vstr = "Deadlock"
	if verdict == 'O':
		vstr = "Output for test not found"
	if verdict == '.': # not asked to run this test
		vstr = "Skipped"
	if verdict == 'K': # intermediate + interactive only
		vstr = "Killed"
	return vstr

# returns colored version of a vstr, according to given verdict (single-letter or full)
def colored_verdict(verdict, vstr = None):
	if vstr is None:
		vstr = verdict
	if verdict[0] == 'A':
		return colorama.Style.BRIGHT + colorama.Fore.GREEN + vstr + colorama.Style.RESET_ALL
	if verdict[0] in ['W', 'P', 'J']:
		return colorama.Style.BRIGHT + colorama.Fore.RED + vstr + colorama.Style.RESET_ALL
	if verdict[0] == 'R':
		return colorama.Style.BRIGHT + colorama.Fore.YELLOW + vstr + colorama.Style.RESET_ALL
	if verdict[0] == 'T':
		return colorama.Style.BRIGHT + colorama.Fore.MAGENTA + vstr + colorama.Style.RESET_ALL
	if verdict[0] == 'M':
		return colorama.Style.BRIGHT + colorama.Fore.BLUE + vstr + colorama.Style.RESET_ALL
	if verdict[0] == 'D':
		return colorama.Style.BRIGHT + colorama.Fore.CYAN + vstr + colorama.Style.RESET_ALL
	if verdict in ['.', 'Skipped']:
		return colorama.Style.BRIGHT + colorama.Fore.WHITE + vstr + colorama.Style.RESET_ALL
	return vstr

# returns colored version of a string with verdicts
def colored_verdicts(verdicts):
	return ''.join([colored_verdict(v) for v in verdicts])

############################## Problem statements ##############################

# finds all sample texts in a given problem statement (in LaTeX with olymp.sty)
# returns list of pairs (input, output), which are the extracted samples in order of appearance
# returns None on fail
# Note: in case of \exmpfile command, paths are searched relative to CWD
def extract_samples(text):
	if text is None:
		return None
	text = re.sub(b'%(.*?)\n', b'', text) # note: false positives with percent as \%

	exmp_re = br'''
		\\exmp \{                  # the command
			(?P<input>  .*?)       # input in braces
		\} \{
			(?P<output> .*?)       # output in braces
		\}
	'''
	exmpfile_re = br'''
		\\exmpfile \{              # the command
			(?P<input_file>  .*?)  # input filename in braces
		\} \{
			(?P<output_file> .*?)  # output filename in braces
		\}
	'''
	final_re = b'(?sx) (%s)|(%s)' % (exmp_re, exmpfile_re)

	all_samples = []
	for match in re.finditer(final_re, text):
		args = match.groupdict()
		if args['input_file'] is not None:
			test_input = read_file_contents(args['input_file'])
			test_output = read_file_contents(args['output_file'])
		else:
			test_input = args['input']
			test_output = args['output']
		if test_input is None or test_output is None:
			return None
		test_input = test_input.strip() + b'\n'
		test_output = test_output.strip() + b'\n'
		all_samples.append((test_input, test_output))
	return all_samples

# finds time and memory limits in a given problem statement (in LaTeX with olymp.sty)
# returns pair of (tl, ml), where: tl is in seconds, ml is in MB
# returns None on fail
def extract_limits(text):
	if text is None:
		return None
	text = re.sub(b'%(.*?)\n', b'', text) # note: false positives with percent as \%

	problem_re  = br'(?x) \\begin \s* \{ problem \}'
	problem_re += br'\s* \{ (.*?) \}' * 5
	match = re.search(problem_re, text)
	if match:
		tl_txt = match.group(4)
		ml_txt = match.group(5)
		try:
			tl = float(tl_txt.split()[0])
			ml = float(ml_txt.split()[0])
		except ValueError:
			return None
		return (tl, ml)
	return None

# returns relative path to the file with LaTeX problem statement (or None if not found)
# statements_name is the name of the directory with statements
# if problem_name is not specified, it is determined as the last directory in CWD
# Note: CWD must be equal to the problem's directory
def find_problem_statement(statements_name = None, problem_name = None):
	if statements_name is None:
		statements_name = '_statements'
	if problem_name is None:
		problem_name = path.basename(os.getcwd())
	stat_file = path.join(os.pardir, statements_name, 'problems', problem_name + '.tex')
	if not path.isfile(stat_file):
		return None
	return stat_file

# returns all sample tests for a given problem
# statement_path is a relative path to existing LaTeX problem statement file
#    (can be obtained from find_problem_statement)
# see extract_samples for description of return value
def read_samples(statement_path):
	if statement_path is None:
		return None
	statement_text = read_file_contents(statement_path)
	with save_cwd():
		os.chdir(path.dirname(statement_path))
		os.chdir(os.pardir)
		return extract_samples(statement_text)

# returns time and memory limits for a given problem
# statement_path is a relative path to existing LaTeX problem statement file
#    (can be obtained from find_problem_statement)
# see extract_limits for description of return value
def read_limits(statement_path):
	return extract_limits(read_file_contents(statement_path))

############################## Compiling sources ###############################

# returns whether a given file/directory is a source file (for solution of anything else)
# in case of c++/pas, it must have commonly used extension
# in case of java, it must be either a java source file or a directory with Task.java in it
def is_source(f):
	return path.splitext(f)[1] in ['.cpp', '.c', '.c++', '.cxx', '.pas', '.dpr', '.java'] or path.isfile(path.join(f, 'Task.java'))

# returns list of generator source files for current problem
# CWD must be set to problem's directory
def get_generator_sources():
	all_files = glob.glob('*')
	files_gen = filter(lambda f : path.basename(f).startswith('gen_'), all_files)
	solutions = filter(is_source, files_gen)
	return list(sorted(solutions))

# returns list of solution source files for current problem
# CWD must be set to problem's directory
def get_solution_sources():
	all_files = glob.glob('*')
	files_sol = filter(lambda f : path.basename(f).startswith('sol_'), all_files)
	solutions = filter(is_source, files_sol)
	return list(sorted(solutions))

# searches for globally installed program and returns full path to it
# returns None if command is not found in PATH
# in fact, it is similar to "which" or "where" shell command
# e.g. given "cl" should return "C:\Prog...\VC\bin\amd64\cl.exe"
def get_command_path(f):
	# taken from http://stackoverflow.com/a/377028/556899
	for path in os.environ["PATH"].split(os.pathsep):
		path = path.strip('"')
		path = os.path.join(path, f)
		if if_exe_exists(path):
			return path
	return None

# checks if the program is globally installed
def if_command_exists(f):
	return (get_command_path(f) is not None)

# returns language string for specified source file
# in some cases mode is appended to the string (e.g. for a directory with Task.java)
# if language is unknown, then None is returned
def guess_source_language(source):
	(name, ext) = path.splitext(source)
	if ext in ['.cpp', '.c', '.c++', '.cxx']:
		return 'cpp'		# gcc/msvc is determined later
	elif ext in ['.pas', '.dpr']:
		return 'pas'		# fpc/dcc32 can be used...
	elif ext in ['.java']:
		return 'java'		# javac can be used directly
	elif ext == '' and path.isfile(path.join(source, 'Task.java')):
		return 'java dir'	# directory with Task.java
	return None

# returns command-line string which should be used to compile given source
# source_local must be relative path to a file in current directory
# returns None if specified compiler is not found or cannot be used
# note: prefer using compile_source instead of this one
def get_compile_cmd(source_local, compiler, compiler_flags):
	if compiler in ['cl', 'dcc32'] and os.name != 'nt':
		return None
	if not if_command_exists(compiler):
		return None
	cmd = '%s %s %s' % (compiler, compiler_flags.get(compiler), source_local);
	if compiler == 'g++':
		cmd += ' -o %s' % path.splitext(source_local)[0]
	return cmd

# compiles a given source code file (in its directory)
# if language is not set, it is chosen automatically by extension
# unless you pass compiler_flags and compiler_order arguments, global compiler settings are used
# CWD is not important, and it is changed only temporarily
def compile_source_impl(source, language = None, compiler_flags = None, compiler_order = None, quiet = False):
	if compiler_flags is None:
		compiler_flags = default_compiler_flags
	if compiler_order is None:
		compiler_order = default_compiler_order
	if language is None:
		language = guess_source_language(source)
		if language is None:
			printq(quiet, colored_verdict('W', "No language is known for target %s" % source))
			return False
	def runner(cmd):
		printq(quiet, "Cmd: %s" % colored_verdict('R', cmd))
		return cmd_runner(quiet)(cmd)
	err = None
	order = compiler_order.get(language.split()[0])
	with save_cwd():
		os.chdir(path.dirname(path.abspath(source)))
		source_local = path.basename(source)
		if language == 'java dir':
			printq(quiet, "Compiling java-task solution %s" % colored_verdict('R', source_local))
			os.chdir(source_local)
			source_local = 'Task.java'
		for compiler in order:
			cmd = get_compile_cmd(source_local, compiler, compiler_flags)
			if cmd is not None:
				err = runner(cmd).returncode
				if err == 0:
					break
	if err != 0:
		printq(quiet, "Failed to compile %s" % colored_verdict('W', source))
		return False
	printq(quiet, "Successfully compiled %s" % colored_verdict('A', source))
	return True

############################### Running processes ##############################

# avoid crash dialog windows popping up on Windows
# http://stackoverflow.com/a/5103935
if os.name == 'nt':
	import ctypes
	SEM_NOGPFAULTERRORBOX = 0x0002
	ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)

RunResult = namedtuple('RunResult', 'verdict exit_code time memory')

# if not in quiet mode, prints some info about several processes soon to be started
# each argument (except "quiet") is a list with one element per process
def proclaim_process_runs(popen_args, time_limits, memory_limits, quiet = False):
	if quiet:
		return
	k = len(popen_args)
	for i in range(k):
		ml_str = tl_str = None
		if time_limits[i] is not None:
			tl_str = "%0.1lf" % time_limits[i]
		if memory_limits[i] is not None:
			ml_str = "%0.1lf" % memory_limits[i]
		print("{0}: Starting: {1}    [TL = {2}, ML = {3}]".format(i, str(popen_args[i]), tl_str, ml_str))

# controls execution of several processes just started via psutil.Popen (until all of them terminate)
# processes - list of process handles returned from psutil.Popen
# time_limits, memory_limits - lists of values, same-indexed as processes:
#    time_limit: maximal cpu time in seconds
#    memory_limit: maximal allowed memory usage in megabytes
# returns list of RunResult-s, same-indexed as processes:
#    verdict: 'A' if executed successfully, 'R' on nonzero return code, 'T' if TL exceeded, 'M' if ML exceeded, 'D' on deadlock
#    exit_code: exit code returned by process on termination
#    time: how much CPU time was spent (in seconds)
#    memory: peak memory consumption (in MB)
# if deadpipe_guard is set, then all remaining processes will be terminated (with 'K' verdict) if they all seem to wait 
# this happens if idle time elapsed since last process termination is greater than deadpipe_guard for all alive processes
def control_processes_execution(processes, time_limits, memory_limits, deadpipe_guard = None, quiet = False):
	k = len(processes)
	verdicts = [None] * k
	exit_codes = [None] * k
	max_cpu_time = [0.0] * k
	max_memory = [0.0] * k

	def handle_process_termination(proc):
		i = processes.index(proc)
		if exit_codes[i] is not None:
			return # already terminated earlier
		exit_codes[i] = processes[i].returncode
		printq(quiet, "%d: %s (err = %d, mem = %s MB, time = %s sec)" % (
			i, 
			"Finished" if verdicts[i] is None else get_verdict_full_name(verdicts[i]),
			exit_codes[i],
			color_highlight("%0.1f" % max_memory[i]),
			color_highlight("%0.2f" % max_cpu_time[i])
		))
		if verdicts[i] is None:
			verdicts[i] = ('A' if exit_codes[i] == 0 else 'R')

	start_real_time = time.time()
	last_alive_count = k
	while True:
		try:
			gone, alive = psutil.wait_procs(processes, 0.01, handle_process_termination)
			if len(alive) > 0:
				raise psutil.TimeoutExpired(0)
			break
		except psutil.TimeoutExpired:
			for i in range(k):
				process = processes[i]
				if not process.is_running():
					continue
				try:
					max_cpu_time[i] = max(max_cpu_time[i], process.cpu_times().user)
					max_memory[i] = max(max_memory[i], process.memory_info().rss / (2**20))
					if time_limits[i] is not None and max_cpu_time[i] > time_limits[i]:
						verdicts[i] = 'T'
						process.terminate()
						continue
					if memory_limits[i] is not None and max_memory[i] > memory_limits[i]:
						verdicts[i] = 'M'
						process.terminate()
						continue
					if time_limits[i] is not None and time.time() - start_real_time > (time_limits[i] * 3 + 1):
						verdicts[i] = 'D'
						process.terminate()
						continue
				except psutil.NoSuchProcess: # finished when we checked/terminated it
					continue

			if deadpipe_guard is not None and len(alive) < k:	#note: only for interactive problems!
				idle_time = [time.time() - start_real_time - max_cpu_time[i] for i in range(k)]
				if len(alive) < last_alive_count:
					last_alive_count = len(alive)
					last_idle_time = idle_time[:]
				# alive processes with very small idle time after last process termination:
				still_working = list(filter(lambda i: processes[i].is_running() and idle_time[i] - last_idle_time[i] < deadpipe_guard, range(k)))
				if len(still_working) == 0:
					for i in range(k):
						if processes[i].is_running():
							verdicts[i] = 'K'
							try:
								processes[i].terminate()
							except psutil.NoSuchProcess:
								continue

		except psutil.NoSuchProcess:	# is it possible?
			break
		except psutil.AccessDenied:		# perhaps OSX-specific
			printq(quiet, "Access denied error (perhaps try sudo/admin)")

	res = [RunResult(verdicts[i], exit_codes[i], max_cpu_time[i], max_memory[i]) for i in range(k)]
	return res

# runs a solution by name (either an executable file or java class)
# parameters and results as in controlled_run
# if interactive = True, then solution is run connected to interactor
def controlled_run_solution(solution, time_limit, memory_limit, interactive, quiet = False):
	corrected_memory_limit = memory_limit
	if if_exe_exists(solution):
		solution_path = solution if os.name == 'nt' else path.join('./', solution)
		popen_args = solution_path
	else:
		assert(is_java_class(solution) or has_java_task(solution))
		heap_size_key = '-Xmx1G' if memory_limit is None else '-Xmx%dM' % int(memory_limit)
		corrected_memory_limit = None
		popen_args = ['java', heap_size_key, '-Xms64M', '-Xss32M']
		if is_java_class(solution):
			popen_args += [path.splitext(solution)[0]]
		elif has_java_task(solution):
			popen_args += ['-cp', solution, 'Task']

	if interactive:
		interactor_args = ['interactor', 'input.txt', 'output.txt']
		args_list = [interactor_args, popen_args]
		TLs = [time_limit * 2 + 5, time_limit] if time_limit is not None else [None, None]
		MLs = [memory_limit + 256, corrected_memory_limit] if memory_limit is not None else [None, None]

		proclaim_process_runs(args_list, TLs, MLs, quiet)
		process_inter = psutil.Popen(interactor_args, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
		process_sol = psutil.Popen(popen_args, stdin = process_inter.stdout, stdout = process_inter.stdin)
		inter_res, sol_res = control_processes_execution([process_inter, process_sol], TLs, MLs, 0.1, quiet)

		exitcode_verdict = get_verdict_for_checker_code(inter_res.exit_code)
		assert(inter_res.verdict != 'K' or sol_res.verdict != 'K')
		if inter_res.verdict not in ['A', 'R', 'K']:  # T/M/D
			return sol_res._replace(verdict = 'J')
		if sol_res.verdict not in ['A', 'R', 'K']:    # T/M/D
			return sol_res
		if sol_res.verdict == 'R':
			if exitcode_verdict != 'J' and inter_res.verdict != 'K': # may be simply WA e.g. in case of java
				return sol_res._replace(verdict = exitcode_verdict)
			else:
				return sol_res
		if inter_res.verdict == 'K':                  # solution ended prematurely
			return sol_res._replace(verdict = 'W')
		return sol_res._replace(verdict = exitcode_verdict)
	else:
		proclaim_process_runs([popen_args], [time_limit], [corrected_memory_limit], quiet)
		process = psutil.Popen(popen_args)
		res = control_processes_execution([process], [time_limit], [corrected_memory_limit], None, quiet)
		return res[0]

############################## Diffs and checkers ##############################

# returns whether two files with given names (paths) are equal as streams of tokens
# can be used as built-in replacement for wcmp.cpp checker from testlib distribution
# note that it works a bit different from standard commands fc/diff
# if any of the files is not present, returns false
def is_file_diff_empty(ap, bp):
	try:
		with open(ap, "rb") as af:
			with open(bp, "rb") as bf:
				a_tokens = af.read().split()
				b_tokens = bf.read().split()
				return a_tokens == b_tokens
	except IOError:
		return False

# given return code of checker process, returns verdict for solution
def get_verdict_for_checker_code(errcode):
	if errcode == 0:
		return 'A'
	if errcode == 1:
		return 'W'
	if errcode == 2:
		return 'P'
	if errcode == 3:
		return 'J'
	if errcode >= 0 and errcode <= 16:
		return 'W'	# still can be a valid return
	return 'J'		# most likely a crash

# runs checker and returns its opinion on the output file
# returns 'A' if output is correct, and 'W'/'P'/'J' otherwise
# Note: CWD must be equal to the problem directory
# Data taken from files:
#   'input.txt' - input data
#   'answer.txt' - jury's output data
#   'output.txt' - contestant's output data
def run_checker(quiet = False):
	if if_exe_exists('check'):
		errcode = cmd_runner(quiet)('./check input.txt output.txt answer.txt').returncode
	else:
		errcode = 0 if is_file_diff_empty('output.txt', 'answer.txt') else 1
	return get_verdict_for_checker_code(errcode)

################################### Archives ###################################

# finds 7-zip command line executable
# usually uses a version available in PATH (7za / 7z)
# returns path to 7z or None if it is not found
def find_7zip():
	if if_command_exists('7za'):
		return '7za'
	if if_command_exists('7z'):
		return '7z'
	if os.name == 'nt' and if_exe_exists('C:/Program Files/7-Zip/7z'):
		return 'C:/Program Files/7-Zip/7z'
	if os.name == 'nt' and if_exe_exists('C:/Program Files (x86)/7-Zip/7z'):
		return 'C:/Program Files (x86)/7-Zip/7z'
	return None

# creates a very simple flat .zip archive with given files
# input_files - list of filenames of what to put into archive
# output_file - filename of output archive (overwritten if already exists)
# quiet - if True, then output to console is suppressed
# note: may break for lengthy file list due to OS limit on cmd length (8K-32K)
# returns True on success, False on fail
def create_flat_zip(input_files, output_file, quiet = False, level = 3):
	if path.isfile(output_file):
		os.remove(output_file)
	executable = find_7zip()
	if executable is None:
		printq(quiet, "7-Zip not found")
		return False
	def dot_path(f):
		if f.startswith('.'):
			return path
		return path.join('./', f)
	dot_inputs = map(dot_path, input_files)
	cmdline = "%s a -tzip -y -mx=%d %s %s" % (executable, level, output_file, ' '.join(dot_inputs))
	err = cmd_runner(quiet)(cmdline)
	return err == 0

##################################### Config ###################################

# common configuration settings for everything
class Config:
	def __init__(self, quiet = False, stop = False, tl = None, ml = None, cl_flags = None, cl_order = None):
		# time limit on solution's cpu time (real, in seconds, may be None)
		self.tl = tl
		# memory limit on solution's memory (real, in megabytes, may be None)
		self.ml = ml
		# whether print output is suppressed during operation
		self.quiet = quiet
		# whether to stop on the first error noticed
		self.stop = stop
		# options passed to compilers in command line (if None, then default_compiler_flags is used)
		self.cl_flags = cl_flags
		# order of compiler preference for each language (if None, then default_compiler_order is used)
		self.cl_order = cl_order

############################## User-callable functions #########################

# Note: For most of the functions below:
#  1. CWD must be the problem's directory
#  2. cfg parameter must be a Config instance

# run a given solution on a given test
# solution: path to solution (executable or directory with java Task)
# input_file: path to test's input file
# returns RunResult tuple (see description above)
# if gen_output = True, then:
#   test's output file is ignored
#   it is overwritten with the output of solution (unless it was terminated prematurely)
# if interactor is present, solution is run with it
def check_solution_on_test(cfg, solution, input_file, gen_output = False):
	assert(path.dirname(path.abspath(solution)) == path.abspath(os.getcwd()))
	copyfile(input_file, 'input.txt')
	interactive = if_exe_exists('interactor')
	res = controlled_run_solution(solution, cfg.tl, cfg.ml, interactive, cfg.quiet)
	if gen_output:
		copyfile('output.txt', 'answer.txt')
	if not interactive:
		if not gen_output:
			if path.isfile(get_output_by_input(input_file)):
				copyfile(get_output_by_input(input_file), 'answer.txt')
			elif res.verdict == 'A':
				res = res._replace(verdict = 'O')
		if res.verdict == 'A':
			checker_res = run_checker(cfg.quiet)
			res = res._replace(verdict = checker_res)
	printq(cfg.quiet, "on %s: %s" % (input_file, colored_verdict(res.verdict)))
	if gen_output and res.verdict in ['A', 'W', 'P', 'J']:
		copyfile('answer.txt', get_output_by_input(input_file))
	return res

# run given solution on all tests (or on specified subset)
# solution: path to solution (executable or directory with java Task)
# tests_filter: string specifying which tests to check (if None, then all tests are run)
# returns list of RunResult tuples, one per test (see description above)
# if cfg.stop=True, then shorter string is returned (up to first error inclusive)
# see check_solution_on_test for explanation of gen_output = True case
def check_solution(cfg, solution, tests_filter = None, gen_output = False):
	res_list = []
	for f in get_tests_inputs():
		if not if_test_passes_filter(f, tests_filter):
			res_list.append(RunResult('.', 0, 0, 0))
			continue
		res = check_solution_on_test(cfg, solution, f, gen_output)
		res_list.append(res)
		if res.verdict != 'A' and cfg.stop:
			printq(cfg.quiet, "Stopped with %s on %s: %s" % (solution, f, colored_verdict(res.verdict)))
			break
	return res_list

# returns formatted version of solution results
# run_results must be a RunResult tuple
# it represents single row in table of results (returned as list of colored strings)
def format_solution_result(solution_name, run_results):
	total_verdict = 'A'
	test_index = len(run_results) - 1
	for i,res in enumerate(run_results):
		if res.verdict not in ['A', '.']:
			total_verdict = res.verdict
			test_index = i
			break
	verdicts_chars = ''.join(res.verdict for res in run_results)
	verdicts_string = '_'.join(verdicts_chars[i:i+10] for i in range(0, len(verdicts_chars), 10))
	full_verdict_name = get_verdict_full_name(total_verdict)
	max_time = max(res.time for res in run_results)
	max_mem = max(res.memory for res in run_results)
	return [
		color_highlight(solution_name),
		colored_verdict(full_verdict_name),
		"%d" % (test_index + 1),
		colored_verdicts(verdicts_string),
		color_highlight("%0.2f" % max_time) + " s",
		color_highlight("%0.1f" % max_mem) + " mb"
	]

# run given solutions on given tests
# solutions: list of solutions to check (if None, all solutions are found)
# tests: list of tests to check (if None, then all tests are used)
# returns list of pairs:
#   first - name of solution
#   second - list of RunResult tuples
def check_many_solutions(cfg, solutions = None, tests = None):
	if solutions is None:
		solutions = get_solutions()
		printq(cfg,quiet, "Solutions: %s" % str(solutions))
	res_table = []
	for sol in solutions:
		res = check_solution(cfg, sol, tests)
		res_table.append((sol, res))
		if not cfg.quiet:
			row = format_solution_result(sol, res)
			print("%s:   %s (%s)        %s\n" % (row[0], row[1], row[2], row[3]))
	return res_table

# pretty-print the results returned by check_all_solutions
def print_solutions_results(data):
	text_table = [format_solution_result(*elem) for elem in data]
	print(draw_table_colored(text_table))

# converts EOLN style of given byte string to system's default
# note: data must be read and written to/from file in binary mode
def convert_eoln(contents):
	return contents.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', os.linesep.encode())

# run validator on given test (i.e. input_file)
# returns True on success, False on validation error, None if something is missing
def validate_test(input_file, quiet = False):
	if not if_exe_exists('validator') or not path.isfile(input_file):
		return None
	printq(quiet, './validator < ' + input_file)
	with open(input_file, 'rb') as f:
		if validator_eoln_relaxed:
			data = f.read()
			data = convert_eoln(data)
			f = tempfile.TemporaryFile()
			f.write(data)
			f.seek(0)
		err = cmd_runner(quiet)('./validator', input = f).returncode
	return err == 0

# run validator on all tests
# returns a list of relative paths to all the failed test input files
# if validator is missing, some string is returned
def validate_all_tests(quiet = False):
	incorrect = []
	for f in get_tests_inputs():
		ok = validate_test(f, quiet)
		if ok is None:
			return "not found"
		if not ok:
			incorrect.append(f)
	return incorrect

# pretty-print the results returned by validate_all_tests
def print_validate_results(results):
	if type(results) == str:
		print(colored_verdict('T', "Validator not found!"))
	elif len(results) == 0:
		print(colored_verdict('A', "All tests are correct"))
	else:
		print(colored_verdict('W', "Failed tests:"))
		for f in results:
			print("	  " + f)

# checks if all the tests are in form tests\[1.in, 2.in, 3.in, ..., {k}.in]
# returns list of error messages (empty list if everything is OK)
def validate_tests_indices():
	tests = get_tests_inputs()
	non_numeric = []
	numeric = []
	for f in tests:
		try:
			numeric.append(get_test_index(f))
		except ValueError:
			non_numeric.append(f)
	# copy-pasted from http://stackoverflow.com/a/2154437
	ranges = []
	for k, g in itertools.groupby(enumerate(numeric), lambda ix: ix[0]-ix[1]):
		group = list(map(operator.itemgetter(1), g))
		ranges.append((group[0], group[-1]))
	results = []
	if non_numeric:
		results.append(colored_verdict('W', 'Tests without indices: ') + str(non_numeric))
	if not ranges:
		results.append(colored_verdict('W', 'No tests found'))
	else:
		if ranges[0][0] != 1:
			results.append(colored_verdict('W', 'Tests start from ') + str(ranges[0][0]))
		if len(ranges) != 1:
			results.append(colored_verdict('W', 'Tests with indices: ') + str(ranges))
	return results

# pretty-print results of validate_tests_indices
def print_validate_indices_results(results):
	if len(results) == 0:
		print(colored_verdict('A', 'Tests names are correct'))
	else:
		for message in results:
			print(message)

# checks whether all samples from the problem statement are properly included in the tests
# returns list of bad tests, which are different/incompatible/nonexistent with the corresponding samples
#      or some string if failed to extract samples from the problem statement
def check_samples(statements_name = None, quiet = False):
	def is_sample_bad(path_in, path_out, sample, quiet):
		if not (path.isfile(path_in) and path.isfile(path_out)):
			printq(quiet, colored_verdict('R', "One of sample files is missing: %s and %s" % (path_in, path_out)))
			return True
		with open(path_in, 'rb') as f:
			test_in = f.read()
		if convert_eoln(test_in) != convert_eoln(sample[0]):
			printq(quiet, colored_verdict('W', "Sample test input %s is different from statement" % path_in))
			return True
		copyfile(path_in, 'input.txt')
		copyfile(path_out, 'answer.txt')
		with open('output.txt', 'wb') as f:
			f.write(sample[1])
		if run_checker(quiet) != 'A':
			printq(quiet, colored_verdict('W', "Sample test %s has wrong output in statement" % path_in))
			return True
		printq(quiet, "Sample test %s is ok" % path_in)
		return False

	samples = read_samples(find_problem_statement(statements_name))
	if samples is None:
		return "not found"
	bad_tests = []
	printq(quiet, "Number of samples: %d" % len(samples))
	for i,sample in enumerate(samples):
		path_in = get_test_input(i + 1)
		path_out = get_output_by_input(path_in)
		if (is_sample_bad(path_in, path_out, sample, quiet)):
			bad_tests.append(path_in)
	return bad_tests

# pretty-print results of check_samples call
def print_check_samples_results(results):
	if type(results) is str:
		print(colored_verdict('T', "Failed to extract samples from problem statement!"))
	elif len(results) == 0:
		print(colored_verdict('A', "Sample tests are compatible"))
	else:
		print(colored_verdict('W', "Incompatible sample tests: ") + str(results))

# run stress-testing of given solutions on given generator
# returns an infinite iterable sequence of problematic seeds (i.e. works as a generator of bad tests)
# generator_args - generator and list of its parameters (i.e. Popen args)
# solutions - list of solutions (usually at least 2, but may be 1) to be stress-tested
# for each test, one int32 argument is added to generator's args as the last one (seed)
# first solution is used to generate answer for a test, others are compared to it
# validator is used if available (and not used otherwise)
def stress_test_solutions(cfg, generator_args, solutions):
	if not isinstance(generator_args, list):
		generator_args = [generator_args]
	test_name = 'stress_test.in'
	do_validate = if_exe_exists('validator')
	quiet = cfg.quiet
	cfg = copy.copy(cfg)
	cfg.quiet = True
	printq(quiet, "Validator enabled" if do_validate else "No validator found")
	while True:
		gen_seed = random.randint(1, 1000000000) - 1
		seeded_args = generator_args + [str(gen_seed)]
		printq(quiet, "Generating test: " + str(seeded_args))
		test = subprocess.check_output(seeded_args)
		with open(test_name, 'wb') as f:
			f.write(test)
		if do_validate and not validate_test(test_name, True):
			printq(quiet, colored_verdict('R', "Invalid input on seed ") + str(gen_seed))
			yield gen_seed
			continue
		verdicts = []
		for k,sol in enumerate(solutions):
			res = check_solution_on_test(cfg, sol, test_name, k==0)
			verdicts.append(res.verdict)
		if verdicts.count('A') == len(verdicts):
			continue
		printq(quiet, colored_verdict('W', "Incompatible outputs: ") + colored_verdicts(verdicts) + " on seed " + str(gen_seed))
		yield gen_seed

# compiles given source file (in its directory)
# language is guessed from extension
# returns True on success, False on error
def compile_source(source, cfg):
	return compile_source_impl(source, None, cfg.cl_flags, cfg.cl_order, cfg.quiet)

# compiles given list of source files
# returns two lists in a tuple: list of successfully compiled sources, and list of unsucessfully compiled ones
# if cfg.stop=True, then lists may be incomplete (they include all sources up to first error inclusive)
def compile_sources(sources, cfg):
	successes = []
	fails = []
	for source in sources:
		ok = compile_source(source, cfg)
		if ok:
			successes.append(source)
		else:
			fails.append(source)
			if cfg.stop:
				break
	return [successes, fails]

# returns which source files in the specified groups are present in the current problem
# flags solutions, generators, checker, validator tells if such a group should be returned
# return list of filenames, which can be passed to compile_sources
def get_sources_in_problem(solutions = False, generators = False, checker = False, validator = False):
	sources = []
	def check_and_add(source):
		if path.isfile(source):
			sources.append(source)
	if validator:
		check_and_add('validator.cpp')
	if checker:
		check_and_add('check.cpp')
	if generators:
		sources.extend(get_generator_sources())
	if solutions:
		sources.extend(get_solution_sources())
	return sources

# pretty-print results returned by compile_in_problem
def print_compile_results(results):
	successes = results[0]
	fails = results[1]
	sources = "{none}"
	if len(successes) > 0:
		sources = '[' + ', '.join(successes) + ']'
	print(colored_verdict('A', "Successfully compiled: " + sources))
	if len(fails) > 0:
		sources = '[' + ', '.join(fails) + ']'
		print(colored_verdict('W', "Failed to compile: " + sources))
