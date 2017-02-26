#!/usr/bin/python3

import sys
import tools.libraries.rolling as r

def main():
    args = sys.argv[1:]
    if (args[0] == '-n'):
        num = args[1]
        args = args[2:]
    else:
        num = 1
    for s in args:
        for i in range(int(num)):
            if (i%20 == 19):
                print('')
            print(r.roll(s), end='  ')
        print('')

if (__name__ == '__main__'):
    main()
