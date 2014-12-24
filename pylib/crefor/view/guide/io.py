#!/usr/bin/env python

"""
"""

import os

from maya import cmds

from crefor import api
from crefor.model.guide.guide import Guide
from crefor.lib import libName, libXform
from crefor import log


from PySide.QtCore import QSize, Qt
from PySide.QtGui import QWidget, QHBoxLayout, QPushButton, QIcon, QPixmap

logger = log.get_logger(__name__)

WIDGET = None

class GuideIOWidget(QWidget):
    """

    """

    BUTTON_SIZE = 30

    def __init__(self, parent=None):
        super(GuideIOWidget, self).__init__(parent)

        self.buttons = {}

        self.setup_ui()

    def setup_ui(self):

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.__add_button("write",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/write.png"),
                          self.__write,
                          "Write guide snapshot to disk")
        self.__add_button("read",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/read.png"),
                          self.__read,
                          "Read guide snapshot from disk")
        self.__add_button("rebuild",
                          os.path.join(os.path.dirname(__file__),
                                       "../icons/rebuild.png"),
                          self.__rebuild,
                          "Rebuild guide snapshot from disk")

        self.setLayout(self.layout)
        self.setWindowTitle("Guide IO")

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

    def __write(self):
        """
        Write a guide snapshot to disk
        """

        singleFilter = "Json (*.json)"
        path = cmds.fileDialog2(fileFilter=singleFilter, dialogStyle=2, fileMode=0)

        if path:
            logger.info("Writing guide snapshot: '%s'" % path[0])
            api.write(path[0])

    def __read(self):
        """
        Read a guide snapshot from disk
        """

        singleFilter = "Json (*.json)"
        path = cmds.fileDialog2(fileFilter=singleFilter, dialogStyle=2, fileMode=1)

        if path:
            logger.info("Reading guide snapshot: '%s'" % path[0])
            api.read(path[0])

    def __rebuild(self):
        """
        Rebuild a guide snapshot from disk
        """

        singleFilter = "Json (*.json)"
        path = cmds.fileDialog2(fileFilter=singleFilter, dialogStyle=2, fileMode=1)

        if path:
            logger.info("Reading guide snapshot: '%s'" % path[0])
            api.rebuild(path[0])


def show():
    global WIDGET
    WIDGET = GuideIOWidget()
    WIDGET.show()