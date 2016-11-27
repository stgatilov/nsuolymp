# some user preferences can be set here

# for each compiler, specify flags added to command line
default_compiler_flags = {
	"dcc32": "-cc",
	"fpc": "-O2",
	"javac": "",
	"cl": "/O2 /EHsc",
	"g++": "-O2 --std=gnu++11",
}

# for each language, specify in which order to try compilers to build it
# (useful e.g. for choosing between cl/g++ and fpc/dcc32 reliably)
default_compiler_order = {
	"cpp": ["cl", "g++"],
	"pas": ["dcc32", "fpc"],
	"java": ["javac"],
}

# if set to true, then endlines are converted on-the-fly to local system defaults before being passed to validator
# note: useful when preparing contest on OS different from the one used on contest
validator_eoln_relaxed = False

# this function is applied to the time limit extracted from the problem statement
# you can adjust this function in order to match approximately speed of the testing server
def convert_default_time_limit(tl):
	return tl		# e.g.:  1.5 * tl
