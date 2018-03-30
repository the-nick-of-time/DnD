#!/usr/bin/python3

import sys
import re
from optparse import OptionParser

import tools.libraries.rolling as r

def usage():
    msg = """Usage: roll [OPTION] [-n NUMBER] ROLL...

Options:
  -a      Take the average roll
  -c      Roll as a critical hit (number of dice doubled)
  -e      Roll in default mode (same as if no options are given)
  -v      Roll in verbose mode (shows rolls, constant modifiers, and total)
  -vc     Roll in verbose mode as a critical hit (shows rolls, constant
            modifiers, and total)

Number of rolls:
  -n [NUMBER]   Roll each ROLL NUMBER times
"""
    print(msg)


def main():
    width = 16
    args = sys.argv[1:]
    if (len(args) == 0):
        print('{0:2}'.format(r.roll('1d20')))
    opt = 'execute'
    num = 1
    i = 0
    while (i < len(args)):
        if (args[i] == '-n'):
            num = int(args[i+1])
            i += 2
        elif (re.match('-([vcae]+)', args[i])):
            o = re.match('-([vcae]+)', args[i]).group(1)
            map_ = {'v': 'multipass', 'vc': 'multipass_critical',
                    'a': 'average', 'e': 'execute', 'c': 'critical'}
            if (o in map_):
                opt = map_[o]
            else:
                opt = 'execute'
            i += 1
        else:
            for j in range(num):
                if (j%width == 0 and j != 0):
                    print()
                print('{0:2}'.format(r.roll(args[i], option=opt)), end=' ')
            print()
            i += 1

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
    if len(args) == 0:
        print(fmt.format(r.roll("1d20")))
    else:
        if options.verbose:
            if options.crit:
                op = "multipass_critical"
            else:
                op = "multipass"
        elif options.average:
            op = "average"
        else:
            op = "execute"
        for expr in args:
            for i in range(options.number):
                if (i%width == 0 and i != 0):
                    print()
                print(fmt.format(r.roll(expr, option=op)), end="  ")
            print()
