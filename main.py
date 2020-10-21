# This Python file uses the following encoding: utf-8
import sys
import os

from PySide2.QtWidgets import (QApplication, QMainWindow, QFileSystemModel,
                               QTableView, QToolBar, QStatusBar, QLineEdit,
                               QWidget, QHeaderView)
from PySide2.QtCore import QFile, QDir, QFileInfo, QProcess
from PySide2.QtUiTools import QUiLoader

from stack import stack

class tfm(QWidget):
    def __init__(self):
        super(tfm, self).__init__()

        self.back_stack = stack()
        self.forward_stack = stack()

        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        ## MAIN VIEW ##
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

        # connect double click action
        self.ui.table_view.doubleClicked.connect(self.item_open_event)

        ## FS TREE ##
        # create seperate FileSystemModel for the fs tree
        self.fs_tree_model = QFileSystemModel()
        self.fs_tree_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.fs_tree_model.setRootPath(QDir.rootPath())

        # connect model to view
        self.ui.fs_tree.setModel(self.fs_tree_model)
        # hide unneeded columns
        for column in range(1, self.ui.fs_tree.header().count()):
            self.ui.fs_tree.hideColumn(column)
        # expand root item
        self.ui.fs_tree.expand(self.fs_tree_model.index(0, 0))

        # connect selection action
        self.ui.fs_tree.clicked.connect(self.fs_tree_event)

        ## TOOLBAR ##

        # initially disable back/forward navigation
        self.ui.action_back.setEnabled(False)
        self.ui.action_forward.setEnabled(False)

        # adress bar
        self.adressbar = QLineEdit()
        self.adressbar.setText(self.current_path)
        self.ui.toolbar.insertWidget(self.ui.action_go, self.adressbar)

        # connect actions to their event functions
        self.adressbar.returnPressed.connect(self.action_go_event)
        self.ui.action_go.triggered.connect(self.action_go_event)

        # TODO: move Home action to future bookmark menu
        self.ui.action_home.triggered.connect(self.action_home_event)
        self.ui.action_up.triggered.connect(self.action_up_event)

        self.ui.action_back.triggered.connect(self.action_back_event)
        self.ui.action_forward.triggered.connect(self.action_forward_event)


    def action_go_event(self):
        next_dir = QDir(self.adressbar.text())
        if (next_dir.isAbsolute() and next_dir.exists()):
            next_path = next_dir.path()
            self.update_current_path(next_path)
        else:
            # TODO: Error handling
            print("ERROR: Path doesn't exist")

    def action_home_event(self):
        next_path = QDir().homePath()
        self.update_current_path(next_path)

    def action_up_event(self):
        dir_up = QDir(self.current_path)
        if (dir_up.cdUp()):
            next_path = dir_up.path()
            self.update_current_path(next_path)
        else:
            # TODO: Error Handling -> this should never occur, since the action gets disabledyy1
            print("ERROR: No dir up exisiting")

    def action_back_event(self):
        next_path = self.back_stack.pop()
        self.forward_stack.push(self.current_path)
        self.ui.action_forward.setEnabled(True)
        if (self.back_stack.empty()):
            self.ui.action_back.setEnabled(False)
        self.update_current_path(next_path, skip_stack=True, reset_forward_stack=False)

    def action_forward_event(self):
        if (not self.forward_stack.empty()):
            next_path = self.forward_stack.pop()
            self.update_current_path(next_path, reset_forward_stack=False)
            # disable forward action if there are no more forward actions
            if (self.forward_stack.empty()):
                self.ui.action_forward.setEnabled(False)
        else:
            # TODO: Error Handling
            print('ERROR: Forward Stack unexpectedly empty')

    def item_open_event(self):
        selected_item = QFileInfo(os.path.join(self.current_path,
                                               self.ui.table_view.currentIndex().data()))
        if (selected_item.isDir()):
            next_path = selected_item.absoluteFilePath()
            self.update_current_path(next_path)
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

    def fs_tree_event(self):
        next_path = self.fs_tree_model.filePath(self.ui.fs_tree.currentIndex())
        self.update_current_path(next_path)

    # TODO: Performance
    def update_current_path(self, next_path:str, skip_stack=False, reset_forward_stack=True):
        self.filesystem.setRootPath(next_path)
        self.ui.table_view.setRootIndex(
            self.filesystem.index(next_path))
        self.adressbar.setText(next_path)
        # disable up navigation if in fs root
        if (next_path == QDir().rootPath()):
            self.ui.action_up.setEnabled(False)
        else:
            self.ui.action_up.setEnabled(True)
        # handle back stack
        if (not skip_stack):
            if (self.back_stack.empty() or self.back_stack.top() != self.current_path):
                self.back_stack.push(self.current_path)
                # reenable back navigation
                self.ui.action_back.setEnabled(True)
        if (reset_forward_stack):
            self.forward_stack.drop()
            self.ui.action_forward.setEnabled(False)
        self.current_path = next_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = tfm()
    window.ui.show()
    sys.exit(app.exec_())
