#!/usr/bin/env python

"""
Blueprint is a runtime representation of a part on top of a guide system

blueprint accepts guides as input
blueprint describes parts
blueprint calls into parts for reinitialisation
blueprint stores hooks, junctions
"""

#!/usr/bin/env 

class BlueprintBaseModel(object):
    """
    describes an fk part

    exists by checking metadata on guide?
    """

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(BlueprintBaseModel, self).__init__(position, primary, primary_index, secondary, secondary_index)
