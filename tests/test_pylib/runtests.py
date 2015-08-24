#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import os
import sys
import argparse

import maya.standalone

from creatureforge.constants import CREATUREFORGE_ROOT
import logging


import argparse


class DisableLogger():
    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, a, b, c):
        logging.disable(logging.NOTSET)


def get_parser():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-t", "--test", dest="tests", default=[], action="append",
                        help="Run specific tests", required=False)
    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Verbose output", required=False)
    return parser


def get_tests(tests):
    data = []

    base = "creatureforge"
    add = lambda module: "test_{module}".format(module=module)
    for test in tests:
        test = "{base}.{test}".format(base=base, test=test)
        data.append(".".join(map(add, test.split("."))))

    return data


def inject_nose():
    """
    Inject nose for import
    """

    root = os.getenv(CREATUREFORGE_ROOT)
    site_packages = ".env/lib/python2.7/site-packages"
    path = os.path.join(root, site_packages)
    sys.path.insert(0, path)


def main():
    import nose

    # Parse input args
    parser = get_parser()
    args = parser.parse_args()
    tests = get_tests(args.tests)

    # NOTE:
    #   Only add --verbose if input argv otherwise we
    #   get no output of tests ran

    # Add nose args
    nose_args = []
    if args.tests:
        nose_args.append("--tests")
        nose_args.extend(tests)
        nose_args.extend(["--verbose"])

    # Run tests
    with DisableLogger():
        if nose_args:
            nose.run(argv=nose_args)
        else:
            nose.run()

if __name__ == "__main__":
    maya.standalone.initialize(name="python")

    inject_nose()
    main()
