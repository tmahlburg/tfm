# This Python file uses the following encoding: utf-8
import sys
import os
import collections

from PySide2.QtWidgets import (QApplication, QWidget, QFileSystemModel,
                               QLineEdit, QLabel)
from PySide2.QtCore import (QFile, QDir, QFileInfo, QProcess, QMimeData, QUrl,
                            )
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QKeySequence

from prefixed import Float

from stack import stack


class tfm(QWidget):
    def __init__(self):
        super(tfm, self).__init__()

        self.clipboard = QApplication.clipboard()
        self.marked_to_cut = []

        self.back_stack = stack()
        self.forward_stack = stack()

        loader = QUiLoader()
        path = os.path.join(os.path.dirname(__file__), "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # MAIN VIEW #
        # set up QFileSystemModel
        self.current_path = QDir.homePath()
        self.filesystem = QFileSystemModel()
        self.filesystem.setRootPath(self.current_path)

        # connect QFileSystemModel to View
        self.ui.table_view.setModel(self.filesystem)
        self.ui.table_view.setRootIndex(
            self.filesystem.index(self.current_path))

        # set up header
        self.horizontal_header = self.ui.table_view.horizontalHeader()
        self.horizontal_header.setSectionsMovable(True)
        # name
        self.horizontal_header.resizeSection(0, 200)
        # size
        self.horizontal_header.resizeSection(1, 85)
        # type
        self.horizontal_header.resizeSection(2, 100)

        # setup context menu
        self.ui.table_view.addAction(self.ui.action_copy)
        self.ui.table_view.addAction(self.ui.action_paste)
        self.ui.table_view.addAction(self.ui.action_cut)
        self.ui.table_view.addAction(self.ui.action_show_hidden)

        # connect double click action
        self.ui.table_view.doubleClicked.connect(self.item_open_event)
        self.ui.table_view.clicked.connect(self.item_selected_event)

        # FS TREE #
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

        # STATUSBAR #
        #self.update_statusbar()
        self.item_info = QLabel()
        #self.dir_info = QLabel()
        self.part_info = QLabel()
        self.ui.statusbar.addPermanentWidget(self.item_info)
        #self.ui.statusbar.addPermanentWidget(self.dir_info)
        self.ui.statusbar.addPermanentWidget(self.part_info)

        self.update_part_info(self.current_path)

        # TOOLBAR #
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

        self.ui.action_copy.setShortcuts(QKeySequence.keyBindings(QKeySequence.Copy))
        self.ui.action_copy.triggered.connect(self.action_copy_event)
        self.ui.action_paste.setShortcuts(QKeySequence.keyBindings(QKeySequence.Paste))
        self.ui.action_paste.triggered.connect(self.action_paste_event)
        self.ui.action_cut.setShortcuts(QKeySequence.keyBindings(QKeySequence.Cut))
        self.ui.action_cut.triggered.connect(self.action_cut_event)

        # raises a TypeError, but works as expected?
        self.ui.action_show_hidden.setShortcuts(QKeySequence('Ctrl+H'))
        self.ui.action_show_hidden.toggled.connect(self.action_show_hidden_event)


    # ---------------- events ---------------------------------------------- #
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
            # TODO: Error Handling
            # -> this should never occur, since the action should be disabled
            print("ERROR: No dir up exisiting")

    def action_back_event(self):
        next_path = self.back_stack.pop()
        self.forward_stack.push(self.current_path)
        self.ui.action_forward.setEnabled(True)
        if (self.back_stack.empty()):
            self.ui.action_back.setEnabled(False)
        self.update_current_path(next_path,
                                 skip_stack=True,
                                 reset_forward_stack=False)

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
        selected_item = QFileInfo(
            os.path.join(self.current_path,
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

    def item_selected_event(self):
        # Update item_info in the statusbar
        name = self.ui.table_view.currentIndex().data()
        selected_item = QFileInfo(
            os.path.join(self.current_path, name))
        if (selected_item.isFile()):
            # this uses the prefixed library
            size = '{:!.2j}B'.format(Float(selected_item.size()))
            self.item_info.setText(name + ': ' + size)
        else:
            self.item_info.setText(name)

    def fs_tree_event(self):
        next_path = self.fs_tree_model.filePath(self.ui.fs_tree.currentIndex())
        self.update_current_path(next_path)

    def action_copy_event(self):
        # get current selection
        self.copy_files(self.ui.table_view.selectionModel().selectedIndexes())

    # TODO: Multithreaded and progress / status information
    # TODO: support folders
    # TODO: handle existing file
    def action_paste_event(self):
        if self.clipboard.mimeData().hasUrls():
            file_path_list = []
            for url in self.clipboard.mimeData().urls():
                if (url.isLocalFile()):
                    file_path_list.append(url.toLocalFile())
            for file_path in file_path_list:
                new_file_path = os.path.join(self.current_path,
                                             os.path.basename(file_path))
                if (QFile().exists(file_path)
                        and not QFile().exists(new_file_path)):
                    QFile().copy(file_path, new_file_path)
            # remove pasted files, if they were cut
            print(file_path_list)
            print(self.marked_to_cut)
            if (collections.Counter(file_path_list)
                    == collections.Counter(self.marked_to_cut)):
                for file_path in file_path_list:
                    QFile().remove(file_path)

    # TODO: visual feedback for cut files
    def action_cut_event(self):
        self.marked_to_cut = self.copy_files(self.ui.table_view.selectionModel().selectedIndexes())


    def action_show_hidden_event(self):
        if self.ui.action_show_hidden.isChecked():
            self.filesystem.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Hidden)
        else:
            self.filesystem.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)


    # ---------------- functions ------------------------------------------- #
    # TODO: Performance
    def update_current_path(self,
                            next_path: str,
                            skip_stack=False,
                            reset_forward_stack=True):
        self.filesystem.setRootPath(next_path)
        self.ui.table_view.setRootIndex(
            self.filesystem.index(next_path))
        self.adressbar.setText(next_path)
        # update directory and partition information
        #self.update_dir_info(next_path)
        self.update_part_info(next_path)
        # disable up navigation if in fs root
        if (next_path == QDir().rootPath()):
            self.ui.action_up.setEnabled(False)
        else:
            self.ui.action_up.setEnabled(True)
        # handle back stack
        if (not skip_stack):
            if (self.back_stack.empty()
                    or self.back_stack.top() != self.current_path):
                self.back_stack.push(self.current_path)
                # reenable back navigation
                self.ui.action_back.setEnabled(True)
        if (reset_forward_stack):
            self.forward_stack.drop()
            self.ui.action_forward.setEnabled(False)
        self.current_path = next_path

    # updates directory information in the statusbar
    # TODO: find an efficient way or multithread this
    def update_dir_info(self, path: str):
        pass

    # updates partition information
    def update_part_info(self, path: str):
        # get fs statistics using statvfs system call
        part_stats = os.statvfs(path)
        fs_size = '{:!.1j}B'.format(Float(part_stats.f_frsize
                                    * part_stats.f_blocks))
        fs_free = '{:!.1j}B'.format(Float(part_stats.f_frsize
                                    * part_stats.f_bfree))
        self.part_info.setText(fs_free + ' of ' + fs_size + ' free')

    # TODO: proper type hints
    def copy_files(self, files_as_indexes):
        """
        :returns: files as str list of paths, which were copied to clipboard
        """
        files_as_path = []
        for index in files_as_indexes:
            if (index.column() == 0):
                files_as_path.append(QFileSystemModel().filePath(index))
        file_urls = []

        for file in files_as_path:
            file_urls.append(QUrl.fromLocalFile(file))

        mime_data = QMimeData()
        mime_data.setUrls(file_urls)

        self.clipboard.setMimeData(mime_data)
        return files_as_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = tfm()
    window.ui.show()
    sys.exit(app.exec_())
