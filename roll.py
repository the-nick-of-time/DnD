#!/usr/bin/python3

import sys
import re

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
    try:
        main()
    except:
        usage()
