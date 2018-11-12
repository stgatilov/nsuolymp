#!/usr/bin/env python
from nsuolymp import *
import argparse, sys, os

def main(argv = None):
    # type: (Optional[List[str]]) -> int
    # handle cmd arguments
    parser = argparse.ArgumentParser(description = "Renames given tests by adding a specified shift to their numbers.")
    parser.add_argument('range', help = "range of tests with 'minus' in-between (or several comma-separated ranges)")
    parser.add_argument('shift', help = "the number of each test will be increased by this shift (may be negative)")
    parser.add_argument('--svn', help = "rename using 'svn rename'", action = "store_true")
    parser.add_argument('-q', '--quiet', help = "print only results (no intermediate messages)", action = "store_true")
    args = parser.parse_args()

    # check if we are inside 'tests' directory: then we should go up
    # recall that the whole nsuolymp works in the root problem directory
    old_tests = get_tests_inputs()
    old_cwd = os.getcwd()
    os.chdir(os.pardir)
    if len(get_tests_inputs()) <= len(old_tests):
        os.chdir(old_cwd)

    shift = int(args.shift)
    if shift == 0:
        print(colored_verdict('T', "Zero shift, nothing to rename"))
        return 0

    renamed = {}
    remain = []
    for f in get_tests_inputs():
        if if_test_passes_filter(f, args.range):
            idx = get_test_index(f)
            nidx = idx + shift
            if nidx < 1:
                print(colored_verdict('P', "File %s goes out of bounds to %d" % (f, nidx)))
                return 3
            renamed[f] = get_test_input(nidx)
        else:
            remain.append(f)

    if len(renamed) == 0:
        print(colored_verdict('T', "No tests match filter"))
        return 4

    for old,new in renamed.items():
        if any([path.isfile(new) and path.samefile(rem, new) for rem in remain]):
            print(colored_verdict('W', "Cannot rename test %s to %s: overwrites existing test" % (old, new)))
            return 1

    def rename(fr, to):
        # type: (str, str) -> None
        fr_o = get_output_by_input(fr)
        to_o = get_output_by_input(to)
        if args.svn:
            os.system('svn rename %s %s' % (fr, to))
            if path.isfile(fr_o):
                os.system('svn rename %s %s' % (fr_o, to_o))
        else:
            os.rename(fr, to)
            if path.isfile(fr_o):
                os.rename(fr_o, to_o)

    from_all = list(renamed.keys())
    to_all = list(renamed.values())
    old_list = ",".join([str(get_test_index(f)).rjust(2) for f in from_all])
    new_list = ",".join([str(get_test_index(f)).rjust(2) for f in to_all])
    if not args.quiet:
        mode = ""
        if args.svn:
            mode = " (with svn rename)"
        print("To be renamed%s:" % mode)
        print("  old: " + old_list)
        print("  new: " + new_list)
        print(color_highlight("Do you really want to rename these tests? [Yes/No] "), end="")
        yesno = input()
        if yesno != "Yes":
            print("Cancelled")
            return 100

    while len(renamed) > 0:
        for old,new in renamed.items():
            if not path.isfile(new):
                rename(old, new)
                if path.isfile(old):
                    print(colored_verdict('R', "Failed to rename %s to %s" % (old,new)))
                    return 2
                del renamed[old]
                break

    print(colored_verdict('A', "%d tests renamed" % len(from_all)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
