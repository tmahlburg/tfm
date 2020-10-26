# This Python file uses the following encoding: utf-8
import sys
import os
import collections

from PySide2.QtWidgets import (QApplication, QWidget, QFileSystemModel,
                               QLineEdit, QLabel, QMenu, QToolButton,
                               QInputDialog, QMessageBox, QMainWindow)
from PySide2.QtCore import (QFile, QDir, QFileInfo, QProcess, QMimeData, QUrl,
                            )
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QKeySequence, QIcon

from prefixed import Float

from stack import stack


class tfm(QMainWindow):
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
        self.ui.table_view.addAction(self.ui.action_delete)
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

        # main menu
        self.main_menu = QMenu()
        self.main_menu.addAction(self.ui.action_show_hidden)

        self.menu_button = QToolButton()
        self.menu_button.setMenu(self.main_menu)
        self.menu_button.setPopupMode(QToolButton().InstantPopup)
        self.menu_button.setDefaultAction(self.ui.action_menu)

        self.ui.toolbar.insertWidget(self.ui.action_back, self.menu_button)

        # adress bar
        self.adressbar = QLineEdit()
        self.adressbar.setText(self.current_path)
        self.ui.toolbar.insertWidget(self.ui.action_go, self.adressbar)

        # menu for new file or directory
        self.new_menu = QMenu()
        self.new_menu.addAction(self.ui.action_new_dir)
        self.new_menu.addAction(self.ui.action_new_file)

        self.new_button = QToolButton()
        self.new_button.setMenu(self.new_menu)
        self.new_button.setPopupMode(QToolButton().MenuButtonPopup)
        self.new_button.setDefaultAction(self.ui.action_new_dir)

        self.ui.toolbar.insertWidget(self.ui.action_back, self.new_button)

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
        self.ui.action_delete.setShortcuts(QKeySequence.keyBindings(QKeySequence.Delete))
        self.ui.action_delete.triggered.connect(self.action_delete_event)

        self.ui.action_show_hidden.toggled.connect(self.action_show_hidden_event)

        self.ui.action_new_dir.triggered.connect(self.action_new_dir_event)
        self.ui.action_new_file.triggered.connect(self.action_new_file_event)

        # SETUP ICONS #
        self.ui.action_back.setIcon(QIcon.fromTheme('go-previous'))
        self.ui.action_forward.setIcon(QIcon.fromTheme('go-next'))

        self.ui.action_home.setIcon(QIcon.fromTheme('go-home'))
        self.ui.action_up.setIcon(QIcon.fromTheme('go-up'))

        self.ui.action_new_dir.setIcon(QIcon.fromTheme('folder-new'))
        self.ui.action_new_file.setIcon(QIcon.fromTheme('document-new'))

        self.ui.action_go.setIcon(QIcon.fromTheme('go-jump'))

        self.ui.action_menu.setIcon(QIcon.fromTheme('start-here'))

        self.ui.action_copy.setIcon(QIcon.fromTheme('edit-copy'))
        self.ui.action_cut.setIcon(QIcon.fromTheme('edit-cut'))
        self.ui.action_paste.setIcon(QIcon.fromTheme('edit-paste'))
        self.ui.action_delete.setIcon(QIcon.fromTheme('edit-delete'))


    # ---------------- events ---------------------------------------------- #
    def action_new_dir_event(self):
        dir_name, ok = QInputDialog().getText(self,
                                              'Create new directory',
                                              'Directory name:')
        # TODO: Error handling
        if (dir_name, ok):
            if not QDir().mkpath(os.path.join(self.current_path, dir_name)):
                print('ERROR: could not create directory')

    def action_new_file_event(self):
        file_name, ok = QInputDialog().getText(self,
                                              'Create new file',
                                              'File name:')
        # TODO: Error handling
        if (file_name, ok):
            with open(os.path.join(self.current_path, file_name), 'w') as f:
                pass

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
            path_list = []
            for url in self.clipboard.mimeData().urls():
                if (url.isLocalFile()):
                    path_list.append(url.toLocalFile())
            multiple_paths = (len(path_list) > 1)
            cut = (collections.Counter(path_list)
                    == collections.Counter(self.marked_to_cut))
            paths_to_add = []
            for path in path_list:
                if (os.path.isdir(path)):
                    paths_to_add.extend(self.traverse_dir(path))
            path_list.extend(paths_to_add)
            base_path = ''
            if (multiple_paths):
                base_path = os.path.commonpath(path_list) + '/'
            else:
                base_path = os.path.dirname(os.path.commonpath(path_list)) + '/'
            for path in path_list:
                new_path = os.path.join(self.current_path,
                                        path.replace(base_path, ''))
                if (os.path.isdir(path)
                        and not QDir().exists(new_path)):
                    QDir().mkpath(new_path)
                elif (QFile().exists(path)
                        and not QFile().exists(new_path)):
                    QFile().copy(path, new_path)
            if cut:
                for file_path in file_path_list:
                    QFile().remove(file_path)

    # TODO: visual feedback for cut files
    def action_cut_event(self):
        self.marked_to_cut = self.copy_files(self.ui.table_view.selectionModel().selectedIndexes())

    def action_delete_event(self):
        path_list = self.indexes_to_files(self.ui.table_view.selectionModel().selectedIndexes())
        if len(path_list) < 0:
            return
        paths_to_add = []
        for path in path_list:
            if (os.path.isdir(path)):
                paths_to_add.extend(self.traverse_dir(path))
        path_list.extend(paths_to_add)

        if (len(path_list) == 1):
            confirmation_message = 'Do you want to delete "' + os.path.basename(path_list[0]) + '"?'
        else:
            confirmation_message = 'Do you want to delete the ' + str(len(path_list)) + ' selected items?'
        msg_box = QMessageBox()
        msg_box.setText(confirmation_message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Yes)
        msg_box.setIcon(QMessageBox.Question)
        button_clicked = msg_box.exec()

        if (button_clicked == QMessageBox.Yes):
            dir_list = []
            for path in path_list:
                if (os.path.isfile(path)):
                    QFile().remove(path)
                elif (os.path.isdir(path)):
                    dir_list.append(path)
            for dir in dir_list:
                QDir().rmpath(dir)

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
        files_as_path = self.indexes_to_files(files_as_indexes)
        file_urls = []

        for file in files_as_path:
            file_urls.append(QUrl.fromLocalFile(file))

        mime_data = QMimeData()
        mime_data.setUrls(file_urls)

        self.clipboard.setMimeData(mime_data)
        return files_as_path

    # TODO: proper type hints
    def indexes_to_files(self, files_as_indexes):
        files_as_path = []
        for index in files_as_indexes:
            if (index.column() == 0):
                files_as_path.append(QFileSystemModel().filePath(index))
        return files_as_path

    # TODO: replace with os.walk from python std lib.....
    def traverse_dir(self, path):
        """
        Traverses the given directory and returns all files and dirs inside as
        paths.
        """
        dir = QDir(path)
        path_list = []
        for file_name in dir.entryList(filters=QDir.AllDirs|QDir.NoDotAndDotDot|QDir.Files):
            current_path = os.path.join(path, file_name)
            path_list.append(current_path)
            if (QDir().exists(current_path)):
                path_list.extend(self.traverse_dir(current_path))
        return path_list


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setQuitOnLastWindowClosed(False)
    window = tfm()
    window.ui.show()
    sys.exit(app.exec_())
