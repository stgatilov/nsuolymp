## Installation

First of all, you should install [Python].
Both Python 3.5 or Python 2.7 are OK.
You can download it from official site.
Note that latest version of Python includes [pip] automatically.
Both `python` and `pip` should be in PATH.

Now you should make sure all packages used by *nsuolymp* are installed, run e.g.:

    pip install sarge
    pip install psutil
    pip install colorama

On Windows, you'd better add `.PY` extension to PATHEXT environment variable globally.
On POSIX, you should mark all scripts with shebang as executable (with `chmod`).


## Setup

To start working, add *nsuolymp* directory to PATH, e.g. on Windows:
	
	set path=%path%;G:\blahblah\jury\Gatilov\nsuolymp

Now you should be able to run scripts by simply typing `testsol my_sol` into console.


## Conventions

`nsuolymp` relies heavily on conventions about naming and directory structure.
Here is an example of proper directory structure:

	_statements
		problems.tex			# main LaTeX file for statements
		olymp.sty				# prepared with olymp.sty
		problems
			autocomplete.tex	# LaTeX text for each problem statement
			cubes.tex           #
	autocomplete
		validator.cpp			# validator must be present
		check.cpp				# standard checker is expected
		testlib.h				# prepared with C++ testlib
		tests
			1.in				#
			1.out				# 
			2.in				# tests in nsuts naming convention
			2.out				# located in tests/ subdirectory
			...					#
			37.in				#
			37.out
		sol_ruban_ok.dpr		#
		sol_sg_slow.cpp			# solutions start with 'sol_'
		sol_fat_ok.c			#
	cubes
		sol_ss_ok				# Java solutions are subdirectories (for nsuts)
			Task.java			# starting with 'sol_'
			Task.class			# and with Task.java|class in it
		sol_sg_wa.java			# Java solution can be a file too (future of nsuts)
		validator.cpp
		testlib.h
		gen_random.cpp			#
		gen_spiral.cpp			# generators start with 'gen_'
		gen_spiral.exe			#


Here are some rules:

1. All the scripts must be run from problem directory, e.g. from `/autocomplete/`.

2. Problem statement files are looked up in `/_statements/problems/`.
   They must have precise name, have '.tex' extension, be written with olymp.sty.

3. Each problem must be in separate directory, with same name as problem statement.

4. Final tests for the problem must be in `tests/` subdirectory, in *nsuts* naming convention.

5. Validator must be present, exactly named, written in C++, prepared with testlib.

6. Checker must be exactly named, written in C++, prepared with testlib (if necessary for the problem).

7. For interactive problem, interactor source must be named exactly `interactor.cpp`, prepared with testlib.
   Combining interactor with checker is not supported. Output files for tests are ignored.

8. Each solution's name must start with `sol_`.

9. For nsuts, java solution must be a subdirectory with `Task.java` or/and `Task.class` file in it.
   Ordinary java files are also supported as solutions (e.g. `sol_tl.java` or/and `sol_tl.class`).

10. Correct solutions which must pass all tests should have `_ok` in their name.

11. Each generator's name must start with `gen_`


## Samples

Compile everything possible (in current directory):

	compile @

Same as before, but stop if something does not compile:

	compile @ -e

Validate tests in current problem in every supported way:

	validate -a

Same as before, but force to compile validator and checker:

	validate -a -c

Run given solution `sol_sg_ok` on all tests:

	testsol sol_sg_ok

Compile and run given solution `sol_sg_ok` on all tests:

	testsol sol_sg_ok.cpp

Run two solutions without any time and memory limits:

	testsol sol_sg_ok sol_sg_dumb --tl 0 --ml 0

Run all solutions on all tests:

	testsol @

Run all solutions, do not check tests after first fail (ACM-style):

	testsol @ -e

Compile and run all solutions, suppress verbose console output:

	testsol @ -c -q

Run all solutions on three first tests with custom limits:

	testsol @ --tests 1,2,3 --tl 3 --ml 512

Run two solutions on (test 1, tests from 11 to 14, and tests starting with 'bad'):

	testsol sol_sg_ok sol_xx_ok --tests "1,11-14,bad*"

Generate `.out` files for all tests using `sol_sg_ok` solution with big TL:

	testsol sol_sg_ok --gen-output --tl 10

Stress-test two solutions with testlib generator `gen_random` (with parameters `10 3 5 seed`):

	testsol sol_sg_ok sol_sg_dumb -s "gen_random 10 3 5"


## Notes

When working on a platform different from the one competition runs on (e.g. preparing Windows contest on Linux),
you might want to set `validator_eoln_relaxed = True` in `nsuolymp_cfg.py` to avoid [testlib validator issue with EOLNs].

You can customize compilation (compiler parameters and order of preference) in `nsuolymp_cfg.py`.

For stress-testing, you have to pass full generator command line in double quotes after `-s`.
So you might need to prepend `./` (dot slash) to generator executable name on Linux or MacOS.

On Windows 10, python scripts may stop working with output redirection.
This issue can be solved by editing registry: https://stackoverflow.com/a/38901036/556899

On MacOS, you should run testsol as root (via `sudo`), otherwise it won't be able to enforce time and memory limits.

## License

This project is licensed under the terms of the MIT license (see LICENSE.txt).


 [Python]: https://www.python.org/downloads/
 [pip]: https://pip.pypa.io/en/stable/installing/
 [testlib validator issue with EOLNs]: https://github.com/MikeMirzayanov/testlib/pull/49
