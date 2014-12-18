#!/usr/bin/env python

"""
"""

import os

from crefor import api
from crefor.lib import libName, libXform
from crefor.exceptions import NodeException
from maya import cmds

from PySide.QtCore import *
from PySide.QtGui import *

WIDGET = None

class GuideWidget(QWidget):

    BUTTON_SIZE = 30

    def __init__(self, parent=None):
        super(GuideWidget, self).__init__(parent)

        self.buttons = {}

        self.setup_ui()
        # self.setFixedSize(self.sizeHint())

    def setup_ui(self):

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.__add_button("create_guide",
                          os.path.join(os.path.dirname(__file__),
                                       'icons/create.png'),
                          self.__create,
                          "Create guide")
        self.__add_button("remove_guide",
                          os.path.join(os.path.dirname(__file__),
                                       'icons/remove.png'),
                          self.__remove,
                          "Remove selected guides")
        self.__add_button('set_parent',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/setParent.png'),
                          self.__set_parent,
                          "Set selected guides parent to be last selected")
        self.__add_button('add_child',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/addChild.png'),
                          self.__add_child,
                          "Add all selected guides as child to last selected")
        self.__add_button('remove_parent',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/removeParent.png'),
                          self.__remove_parent,
                          "Remove parent from selected guides")
        self.__add_button('duplicate',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/duplicate.png'),
                          self.__duplicate,
                          "Duplicate selected guide")
        self.__add_button('create_hierarchy',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/createHierarchy.png'),
                          self.__create_hierarchy,
                          "Create hierarchy out of selected guides")
        self.__add_button('cycle_aim',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/cycleAim.png'),
                          self.__cycle_aim,
                          "Cycle aim of selected guides")

        self.setLayout(self.layout)
        self.setWindowTitle("Guide tools")

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def __add_button(self, object_name, icon_path, func, tooltip):
        """
        Add simple button to UI
        """

        button = QPushButton()
        button.setObjectName(object_name)
        button.setIcon(QIcon(QPixmap(icon_path)))
        button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        button.setIconSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        button.clicked.connect(func)

        button.setToolTip(tooltip)

        self.layout.addWidget(button)
        self.buttons[object_name] = button

    def sizeHint(self):
        return QSize(self.BUTTON_SIZE*len(self.buttons.keys()), self.BUTTON_SIZE)

    def __create(self):
        """
        Create a new guide
        """

        index = 0
        name = "C_temp_%s_gde" % index
        while cmds.objExists(name):
            index += 1
            name = "C_temp_%s_gde" % index

        guide = api.create(*name.split("_")[:-1])
        cmds.select(guide.joint, r=True)

    def __remove(self):
        """
        Remove guide from scene
        """

        selected = cmds.ls(sl=True)
        for guide in selected:

            try:
                print 'view'
                api.remove(guide)
            except NodeException:
                pass

    def __set_parent(self):
        """
        Set all selected guides to have the same parent
        """

        selected = cmds.ls(sl=True)
        if len(selected) >= 2:

            children = selected[:-1]
            parent = selected[-1]
            for child in children:
                api.set_parent(child, parent)

            cmds.select(parent, r=True)

    def __add_child(self):
        """
        Add all selected guides as child to first selected
        """

        selected = cmds.ls(sl=True)
        if len(selected) >= 2:

            children = selected[:-1]
            parent = selected[-1]
            for child in children:
                api.add_child(parent, child)

    def __remove_parent(self):
        """
        Remove parent from guide
        """

        selected = cmds.ls(sl=True)
        if selected:
            for node in selected:
                api.remove_parent(node)

    def __duplicate(self):
        """
        Duplicate selected guides hierarchy
        """

        top = []

        selected = cmds.ls(sl=True)
        for sel in selected:

            nodes = api.duplicate(sel, hierarchy=True)
            top.append(nodes[0])

        # Select top guides
        cmds.select(top, r=True)

    def __create_hierarchy(self):
        """
        Create hierarchy from sequentially selected guides 
        """

        selected = cmds.ls(sl=1)
        last = None
        while len(selected):
            parent = last or selected.pop(0)
            child = selected.pop(0)

            last = child

            api.set_parent(child, parent)

    def __cycle_aim(self):
        """
        Cycle selected guides aim index to next
        in enum. Skips world/local aims.
        """

        selected = cmds.ls(sl=1)
        for node in selected:
            aims = cmds.attributeQuery('aimAt', node=node, listEnum=True)[0].split(':')
            current_index = cmds.getAttr("%s.aimAt" % node)
            index = 1

            if not current_index == (len(aims) - 1):
                index = (current_index + 1)

            cmds.setAttr("%s.aimAt" % node, index)






def show():
    global WIDGET
    WIDGET = GuideWidget()
    WIDGET.show()