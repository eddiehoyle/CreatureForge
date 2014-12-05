#!/usr/bin/env python

'''
'''

import os

from PySide.QtCore import *
from PySide.QtGui import *


# from crefor.view.layouts import FlowLayout

class GuideTools(QWidget):

    BUTTON_SIZE = 30

    def __init__(self, parent=None):
        super(GuideTools, self).__init__(parent)

        self.buttons = {}

        self.setup_ui()
        # self.setFixedSize(self.sizeHint())

    def setup_ui(self):

        # self.layout = FlowLayout()
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.__add_button('set_parent',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/setParent.png'),
                          self.__set_parent)
        self.__add_button('add_child',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/addChild.png'),
                          self.__add_child)
        self.__add_button('remove_parent',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/removeParent.png'),
                          self.__remove_parent)
        self.__add_button('duplicate',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/duplicate.png'),
                          self.__duplicate)
        self.__add_button('create_hierarchy',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/createHierarchy.png'),
                          self.__create_hierarchy)
        self.__add_button('cycle_aim',
                          os.path.join(os.path.dirname(__file__),
                                       'icons/cycleAim.png'),
                          self.__cycle_aim)

        self.setLayout(self.layout)
        self.setWindowTitle("Guide tools")

    def __add_button(self, object_name, icon_path, func):

        
        # button.setObjectName(object_name)
        button = QPushButton()
        button.setIcon(QIcon(QPixmap(icon_path)))
        button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        button.setIconSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        button.clicked.connect(func)

        self.layout.addWidget(button)
        self.buttons[object_name] = button

    def sizeHint(self):
        return QSize(self.BUTTON_SIZE*len(self.buttons.keys()), self.BUTTON_SIZE)

    def __set_parent(self):
        print '__set_parent'

    def __add_child(self):
        print '__add_child'

    def __remove_parent(self):
        print '__remove_parent'

    def __duplicate(self):
        print '__duplicate'

    def __create_hierarchy(self):
        print '__create_hierarchy'

    def __cycle_aim(self):
        print '__cycle_aim'
