#!/usr/bin/env python

'''
'''

import nose
import os

def main(verbose=False):
    args = [os.path.dirname(__file__)]
    if verbose:
        args.append("--verbose")
    else:
        args.append("-q")
        args.append("-s")
        args.append("--nocapture")
        args.append("--nologcapture")
        args.append("--logging-clear-handlers")

    print "args:", args

    nose.run(argv=args, defaultTest='crefor.tests')

if __name__ == '__main__':
    main()