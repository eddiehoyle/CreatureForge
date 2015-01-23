#!/usr/bin/env python

"""
"""

import json
from crefor.model.guide.template import Template
from crefor.contol.guide import read

def create_template(guides):
    """
    """

    # Snapshot
    if isinstance(guides, dict):
        pass

    # Disk snapshot
    elif os.path.exists(str(guides)):
        try:
            with open(path, "rU") as f:
                data = json.loads(f.read())
        except Exception:
            raise

    # Array of guides
    elif isinstance(guides, list):
        pass

    # Raise
    else:
        pass

    return Template(guides)
