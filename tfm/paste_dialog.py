# This Python file uses the following encoding: utf-8
from PySide2.QtWidgets import QDialog

from .paste_dialog_ui import Ui_Dialog


class paste_dialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        super().setupUi(self)
        self.progressBar.setFormat('%v / %m')

    def init(self, steps):
        self.progressBar.reset()
        self.progressBar.setMaximum(steps)

    def update(self, progress):
        self.progressBar.setValue(progress)
