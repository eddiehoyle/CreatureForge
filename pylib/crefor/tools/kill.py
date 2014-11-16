#!/usr/bin/env python

"""
Maya is unstable likes to crash lots when working
on my tiny laptop. This script greps for Maya and
kills it so I can reload... sigh
"""

import sys
import subprocess

def main():

    # Get Maya process ID
    grep_cmd = ['ps aux | grep Maya.app | grep -v grep | grep -v kill']
    result = subprocess.check_output(grep_cmd, shell=True, stderr=subprocess.PIPE)

    if result:
        _id = result.split()[1]

        # Kill Maya
        kill_cmd = ['kill %s - 9' % _id]
        kill_result = subprocess.check_output(kill_cmd, shell=True, stderr=subprocess.PIPE)
        print "Killing Maya... %s" % _id
    else:
        print "No Maya.app ID found."

if __name__ == '__main__':
    main()
