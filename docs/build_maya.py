#!/usr/bin/env mayapy

import maya.standalone
maya.standalone.initialize(name='python')
import sphinx
import sys
import subprocess
import os
if __name__ == '__main__':
    argv = sys.argv[1:]
    cwd = os.getcwd()
    argv.insert(0, sphinx.__file__)

    # path = os.getcwd()
    argv = [sphinx.__file__, "-b", "html", ".", "_build"]
    sphinx.main(argv)