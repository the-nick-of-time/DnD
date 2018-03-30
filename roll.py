#!/usr/bin/python3

import sys
import re
from optparse import OptionParser

import tools.libraries.rolling as r


if (__name__ == '__main__'):
    parser = OptionParser(usage="usage: %prog [options] expr [expr...]")
    parser.add_option("-a", "--average",
                      action="store_true", dest="average",
                      help="Take the average roll")
    parser.add_option("-c", "--critical",
                      action="store_true", dest="crit",
                      help="Roll as a critical hit (number of dice doubled)")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose",
                      help="Roll in verbose mode (shows rolls, constant modifiers, and total)")
    parser.add_option("-n", "--number",
                      dest="number", type="int",
                      help="Roll each roll this number of times")
    parser.set_defaults(number=1, verbose=False, crit=False)
    (options, args) = parser.parse_args()
    fmt = "{0:2}"
    width = 16
    if options.verbose:
        if options.crit:
            op = "multipass_critical"
        else:
            op = "multipass"
    elif options.average:
        op = "average"
    else:
        op = "execute"
    if len(args) == 0:
        print(fmt.format(r.roll("1d20", option=op)))
    else:
        for expr in args:
            for i in range(options.number):
                if (i%width == 0 and i != 0):
                    print()
                print(fmt.format(r.roll(expr, option=op)), end="  ")
            print()
