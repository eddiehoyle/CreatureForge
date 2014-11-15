#!/usr/bin/env python

'''
'''

from PySide.QtCore import *
from PySide.QtGui import *

from crefor.view.guide import GuideTools

class CreMain(QMainWindow):
    def __init__(self, parent=None):
        super(CreMain, self).__init__(parent)
        
        self.setup_ui()

        self.resize(self.sizeHint())

    def setup_ui(self):
        '''
        '''

        self.dock = QDockWidget(self)
        guide_tools = GuideTools(self)
        self.dock.setWidget(guide_tools)
        self.addDockWidget(Qt.DockWidgetArea(1), self.dock)

        self.dock.setFeatures(QDockWidget.NoDockWidgetFeatures |
                              QDockWidget.DockWidgetMovable |
                              QDockWidget.DockWidgetVerticalTitleBar)
