#!/usr/bin/env python

"""
"""

from PySide.QtCore import *
from PySide.QtGui import *

from crefor.model.guide.guide import Guide
from crefor.lib import libName

class CreateGuideDialog(QDialog):
    """
    """

    def __init__(self, parent=None, label=None):
        super(CreateGuideDialog, self).__init__(parent)

        self.setup_ui()

        self.__position = None
        self.__description = None
        self.__index = None

    def setup_ui(self):

        self.setWindowTitle("Create guide")

        self.layout = QVBoxLayout()
        self.form = QFormLayout()

        self.form.setVerticalSpacing(5)
        self.form.setHorizontalSpacing(10)
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.__setup_position()
        self.__setup_description()
        self.__setup_index()
        self.__setup_button()

        self.layout.setContentsMargins(5, 5, 5, 5)

        self.layout.addLayout(self.form)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def __setup_position(self):
        self.position = QComboBox()

        positions = ["C", "L", "R"]
        self.position.addItems(positions)

        self.position.currentIndexChanged.connect(self.__update_button)

        self.form.addRow(self.tr("&Name:"), self.position)

    def __setup_description(self):
        self.description = QLineEdit()
        self.description.setPlaceholderText("root")

        self.description.textChanged.connect(self.__update_button)
        self.description.textEdited.connect(self.__update_button)

        self.form.addRow(self.tr("&Description:"), self.description)

    def __setup_index(self):
        self.index = QSpinBox()
        self.index.valueChanged.connect(self.__update_button)

        self.form.addRow(self.tr("&Index:"), self.index)

    def __setup_button(self):
        self.button = QPushButton()
        self.button.clicked.connect(self.close)

        self.__update_button()

    def __update_button(self):

        self.__position = self.position.currentText()
        self.__description = self.description.text()
        self.__index = self.index.value()

        if all([self.__position, self.__description, isinstance(self.__index, int)]):
            name = libName.compile(self.__position, self.__description, self.__index, Guide.SUFFIX)
            self.button.setText("Create: '%s'" % name)

        else:
            self.button.setText("Please enter a description.")

    @property
    def results(self):
        return (self.__position, self.__description, self.__index)
