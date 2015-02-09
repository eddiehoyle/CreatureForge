#!/usr/bin/env python

"""
"""

import os

from maya import cmds

from crefor.control import guide
from crefor.model.guide import Guide
from crefor.view.guide.dialogs import CreateGuideDialog
from crefor.lib import libName, libXform
from crefor import log

from PySide.QtCore import QSize, Qt
from PySide.QtGui import QWidget, QHBoxLayout, QPushButton, QIcon, QPixmap

logger = log.get_logger(__name__)

class GuideWidget(QWidget):

    BUTTON_SIZE = 30

    def __init__(self, parent=None):
        super(GuideWidget, self).__init__(parent)

        self.buttons = {}

        self.setup_ui()

    def setup_ui(self):

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.__add_button("create_guide",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/create.png"),
                          self.__create,
                          "Create guide")
        self.__add_button("remove_guide",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/remove.png"),
                          self.__remove,
                          "Remove selected guides")
        self.__add_button("set_parent",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/setParent.png"),
                          self.__set_parent,
                          "Set selected guides parent to be last selected")
        self.__add_button("add_child",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/addChild.png"),
                          self.__add_child,
                          "Add all selected guides as child to last selected")
        self.__add_button("remove_parent",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/removeParent.png"),
                          self.__remove_parent,
                          "Remove parent from selected guides")
        self.__add_button("duplicate",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/duplicate.png"),
                          self.__duplicate,
                          "Duplicate selected guide")
        self.__add_button("create_hierarchy",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/createHierarchy.png"),
                          self.__create_hierarchy,
                          "Create hierarchy out of selected guides")
        self.__add_button("cycle_aim",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/cycleAim.png"),
                          self.__cycle_aim,
                          "Cycle aim of selected guides")
        self.__add_button("compile",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/compile.png"),
                          self.__compile,
                          "Compile guides into joints")
        # self.__add_button("decompile",
        #                   os.path.join(os.path.dirname(__file__),
        #                                "../icons/decompile.png"),
        #                   self.__decompile,
        #                   "Decompile joints into guides")

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

    def __validate(self):
        """
        """

        guides = []
        selected = cmds.ls(sl=1)
        for sel in selected:
            try:
                guides.append(Guide.validate(sel))
            except Exception:
                pass

        return guides

    def __create(self):
        """
        Create a new guide
        """

        global CREATE_GUIDE_DIALOG
        CREATE_GUIDE_DIALOG = CreateGuideDialog()
        CREATE_GUIDE_DIALOG.exec_()

        position, description, index = CREATE_GUIDE_DIALOG.results
        if all([position, description, isinstance(index, int)]):
            _guide = guide.create(position, description, index)
            cmds.select(_guide.node, r=True)

    def __remove(self):
        """
        Remove guide from scene
        """

        cmds.undoInfo(openChunk=True)

        guides = self.__validate()

        for _guide in guides:
            guide.remove(_guide)

        cmds.undoInfo(closeChunk=True)

    def __set_parent(self):
        """
        Set all selected guides to have the same parent
        """

        guides = self.__validate()

        if len(guides) >= 2:

            children = guides[:-1]
            parent = guides[-1]
            for child in children:
                guide.set_parent(child, parent)

            cmds.select(parent.node, r=True)

    def __add_child(self):
        """
        Add all selected guides as child to first selected
        """

        guides = self.__validate()

        if len(guides) >= 2:

            children = guides[:-1]
            parent = guides[-1]
            for child in children:
                guide.add_child(parent, child)

            cmds.select([g.node for g in children], r=True)

    def __remove_parent(self):
        """
        Remove parent from guide
        """

        guides = self.__validate()

        if guides:
            for _guide in guides:
                _guide.remove_parent()

    def __duplicate(self):
        """
        Duplicate selected guides hierarchy
        """

        guides = self.__validate()

        top = []
        for _guide in guides:

            nodes = guide.duplicate(_guide, hierarchy=True)
            top.append(nodes[0])

        # Select top guides
        cmds.select(top, r=True)

    def __create_hierarchy(self):
        """
        Create hierarchy from sequentially selected guides 
        """

        guides = self.__validate()

        last = None
        while len(guides):
            parent = last or guides.pop(0)
            child = guides.pop(0)

            last = child

            guide.set_parent(child, parent)

    def __cycle_aim(self):
        """
        Cycle selected guides aim index to next
        in enum. Skips world/local aims.
        """

        guides = self.__validate()

        for _guide in guides:
            aims = cmds.attributeQuery("aimAt", node=_guide.node, listEnum=True)[0].split(":")
            current_index = cmds.getAttr("%s.aimAt" % _guide.node)
            index = 1

            if not current_index == (len(aims) - 1):
                index = (current_index + 1)

            cmds.setAttr("%s.aimAt" % _guide.node, index)

    def __decompile(self):
        """
        """

        guide.decompile()

    def __compile(self):
        """
        """

        guide.compile()


def show():
    global GUIDE_WIDGET
    GUIDE_WIDGET = GuideWidget()
    GUIDE_WIDGET.show()