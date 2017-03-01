#!/usr/bin/python3

import sys
import tools.libraries.rolling as r

def main():
    width = 16
    args = sys.argv[1:]
    if (args[0] == '-n'):
        num = args[1]
        args = args[2:]
    else:
        num = 1
    for s in args:
        for i in range(int(num)):
            print('{0:3}'.format(r.roll(s)), end=' ')
            if (i%width == width-1):
                print('')
        print('')

if (__name__ == '__main__'):
    main()
