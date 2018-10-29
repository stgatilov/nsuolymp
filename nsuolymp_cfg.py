# some user preferences can be set here

# for each compiler, specify flags added to command line
default_compiler_flags = {
    "dcc32": "-cc",
    "fpc": "-O2",
    "javac": "",
    "cl": "/O2 /EHsc",
    "g++": "-O2 -std=gnu++11",
    "gcc": "-O2 -std=c11",
}

# for each language, specify in which order to try compilers to build it
# (useful e.g. for choosing between cl/g++ and fpc/dcc32 reliably)
default_compiler_order = {
    "cpp": ["cl", "g++"],
    "c": ["cl", "gcc"],
    "pas": ["dcc32", "fpc"],
    "java": ["javac"],
}

# when set to true:
# 1. input file is additionally passed to stdin
# 2. stdout is redirected to temp file, and it is taken instead of file if file is absent/empty
enable_stdinout_redirection = True

# specifies how endlines are encoded on the contest testing machines
# nsuts invokes solutions mainly on Windows platform, hence dos-style is used
# for Linux-hosted contests, set 'linux' here
contest_eoln_style = 'win'

# this function is applied to the time limit extracted from the problem statement
# you can adjust this function in order to match approximately speed of the testing server
def convert_default_time_limit(tl):
    # type: (float) -> float
    return tl       # e.g.:  1.5 * tl
