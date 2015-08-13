#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import sys
import maya.standalone


def inject_nose():
    path = "/Users/eddiehoyle/Code/python/creatureforge/.env/lib/python2.7/site-packages"
    sys.path.insert(0, path)


def main():
    import nose
    nose.run()

if __name__ == "__main__":
    maya.standalone.initialize(name="python")

    inject_nose()
    main()
