#!/usr/bin/env 

from creatureforge.model.blueprint.base import BlueprintBaseModel

class BlueprintFkModel(BlueprintBaseModel):
    """
    describes an fk part

    exists by checking metadata on guide?
    """

    def __init__(self, position, primary, primary_index, secondary, secondary_index):
        super(BlueprintFkModel, self).__init__(position, primary, primary_index, secondary, secondary_index)

        self.__guides = []

    def set_guides(self, guides):
        self.__guides = guides

    def get_hooks(self):
        return None

    def reinit(self):
        pass
