#!/usr/bin/env /Applications/Autodesk/maya2016/Maya.app/Contents/bin/mayapy

import os
import sys
import maya.standalone

from creatureforge.constants import CREATUREFORGE_ROOT


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
    nose.run()

if __name__ == "__main__":
    maya.standalone.initialize(name="python")

    inject_nose()
    main()
