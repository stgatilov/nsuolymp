from typing import Dict, Any
# some user preferences can be set here

# for each compiler, specify flags added to command line
default_compiler_flags = {
    "dcc32": "-cc",
    "fpc": "-O2",
    "javac": "",
    "kotlinc": "",
    "cl": "/O2 /EHsc",
    "g++": "-O2 -std=gnu++11",
    "gcc": "-O2 -std=c11",
    "python": "-m py_compile",
}

# for each language, specify in which order to try compilers to build it
# (useful e.g. for choosing between cl/g++ and fpc/dcc32 reliably)
default_compiler_order = {
    "cpp": ["cl", "g++"],
    "c": ["cl", "gcc"],
    "pas": ["dcc32", "fpc"],
    "java": ["javac"],
    "kotlin": ["kotlinc"],
    "python": ["python"],
}

# NSUTs credentials and contest options
# required to submits solutions
nsuts_options = {
    # may be overriden by contents of nsuts.json in problem directory
    "nsuts": "https://olympic.nsu.ru/nsuts-new",
    # Note: usually overriden by contents of nsuts.json in problem directory
    "olympiad_id": 180,
    "tour_id": 11354,

    # BEWARE: be sure to NOT commit you credentials !
    "email": "user@name.ru",
    "password": "securepassword",
    "session_id": "5c4d2b5a372ca8770923449e286f24a5",

    "compilers": {
        "cpp": ["vcc2015", "mingw8.1cpp"],
        "c": ["vc2015", "mingw8.1c"],
        "java": ["java8u101x32"],
        "kotlin": ["kotlinc"],
        "python": ["python3.6"],
        "pas": ["fpas2.6.4"],
    },
} # type: Dict[str, Any]

# when set to true:
# 1. input file is additionally passed to stdin
# 2. stdout is redirected to temp file, and it is taken instead of file if file is absent/empty
enable_stdinout_redirection = True
# when set to true, stderr is also redirected to temp file (usually not needed)
enable_stderr_redirection = False

# specifies how endlines are encoded on the contest testing machines
# nsuts invokes solutions mainly on Windows platform, hence dos-style is used
# for Linux-hosted contests, set 'linux' here
contest_eoln_style = 'win'

# this function is applied to the time limit extracted from the problem statement
# you can adjust this function in order to match approximately speed of the testing server
def convert_default_time_limit(tl):
    # type: (float) -> float
    return tl       # e.g.:  1.5 * tl
