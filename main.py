# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import (QApplication, QMainWindow, QFileSystemModel,
                               QTableView, QToolBar, QStatusBar, QLineEdit,
                               QWidget, QHeaderView)
from PySide2.QtCore import QFile, QDir, QFileInfo, QProcess
from PySide2.QtUiTools import QUiLoader


class tfm(QWidget):

    def __init__(self):
        super(tfm, self).__init__()

        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # set up QFileSystemModel
        self.current_path = QDir.homePath()
        self.filesystem = QFileSystemModel()
        self.filesystem.setRootPath(self.current_path)

        # connect QFileSystemModel to View
        self.ui.table_view.setModel(self.filesystem)
        self.ui.table_view.setRootIndex(self.filesystem.index(self.current_path))

        # set up header
        self.horizontal_header = self.ui.table_view.horizontalHeader()
        self.horizontal_header.setSectionsMovable(True)
        # name
        self.horizontal_header.resizeSection(0, 200)
        # size
        self.horizontal_header.resizeSection(1, 85)
        # type
        self.horizontal_header.resizeSection(2, 100)

        self.adressbar = QLineEdit()
        self.adressbar.setText(self.current_path)
        self.ui.toolbar.insertWidget(self.ui.action_go, self.adressbar)

        # connect actions to their event functions
        self.adressbar.returnPressed.connect(self.action_go_event)
        self.ui.action_go.triggered.connect(self.action_go_event)

        self.ui.action_home.triggered.connect(self.action_home_event)
        self.ui.action_up.triggered.connect(self.action_up_event)

        self.ui.table_view.doubleClicked.connect(self.item_open_event)

    def action_go_event(self):
        next_dir = QDir(self.adressbar.text())
        if (next_dir.isAbsolute() and next_dir.exists()):
            self.current_path = next_dir.path()
            self.update_ui_to_path()
        else:
            # TODO: Error handling
            print("ERROR: Path doesn't exist")

    def action_home_event(self):
        self.current_path = QDir().homePath()
        self.update_ui_to_path()

    def action_up_event(self):
        dir_up = QDir(self.current_path)
        if (dir_up.cdUp()):
            self.current_path = dir_up.path()
            self.update_ui_to_path()
        else:
            # TODO: Error Handling
            print("ERROR: No dir up exisiting")

    def item_open_event(self):
        selected_item = QFileInfo(os.path.join(self.current_path, self.ui.table_view.currentIndex().data()))
        if (selected_item.isDir()):
            self.current_path = selected_item.absoluteFilePath()
            self.update_ui_to_path()
        elif (selected_item.isFile()):
            if (selected_item.isExecutable()):
                QProcess().startDetached(selected_item.absoluteFilePath(),
                                         [],
                                         self.current_path)
            else:
                QProcess().startDetached('xdg-open',
                                         [selected_item.absoluteFilePath()],
                                         self.current_path)
                print('xdg-open ' + selected_item.absoluteFilePath())
        else:
            # TODO: Error Handling
            print("ERROR: Can't obtain the type of the selected file")

    # TODO: Use Qt signal
    def update_ui_to_path(self):
        self.filesystem.setRootPath(self.current_path)
        self.ui.table_view.setRootIndex(
            self.filesystem.index(self.current_path))
        self.adressbar.setText(self.current_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = tfm()
    window.ui.show()
    sys.exit(app.exec_())
