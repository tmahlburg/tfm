import os
import logging
from typing import List
from subprocess import CalledProcessError

from PySide2.QtWidgets import (QApplication, QFileSystemModel, QLineEdit,
                               QLabel, QMenu, QToolButton, QInputDialog,
                               QMessageBox, QMainWindow, QProgressDialog)
from PySide2.QtCore import (QFile, QDir, QFileInfo, QProcess, QStandardPaths,
                            QThread)
from PySide2.QtGui import QKeySequence, QIcon

from .form import Ui_tfm

from .stack import stack
from .bookmarks import bookmarks as bm
from .mounts_model import mounts_model
from .paste_worker import paste_worker as pw
import tfm.utility as utility

from send2trash import send2trash
from pyudev import Context, Device, Monitor, MonitorObserver


class tfm(QMainWindow, Ui_tfm):
    """
    The main window class, setting up the application and implementing the
    needed events.
    """

    def __init__(self, args: List[str]):
        """
        At the moment the very, very long initialization of the main window,
        setting up everything.

        :param default_path: Use a user defined path as entrypoint. If it's
                             empty, the home directory of the current user will
                             be used.
        :type default_path: str
        """
        super(tfm, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon.fromTheme('system-file-manager'))

        self.clipboard = QApplication.clipboard()
        self.marked_to_cut = []
        self.progress_dialog = None
        self.paste_worker = None
        self.files_to_paste_count = 0

        self.back_stack = stack()
        self.forward_stack = stack()

        self.config_dir = os.path.join(
            QStandardPaths.writableLocation(
                QStandardPaths().ConfigLocation),
            type(self).__name__)

        self.current_path = utility.handle_args(args)
        self.default_path = self.current_path

        # MAIN VIEW #
        # set up QFileSystemModel
        self.filesystem = QFileSystemModel()
        self.filesystem.setRootPath(self.current_path)
        self.filesystem.setReadOnly(False)

        # connect QFileSystemModel to View
        self.table_view.setModel(self.filesystem)
        self.table_view.setRootIndex(
            self.filesystem.index(self.current_path))

        # set up header
        self.horizontal_header = self.table_view.horizontalHeader()
        self.horizontal_header.setSectionsMovable(True)
        # name
        self.horizontal_header.resizeSection(0, 200)
        # size
        self.horizontal_header.resizeSection(1, 100)
        # type
        self.horizontal_header.resizeSection(2, 100)

        # FS TREE #
        # create seperate FileSystemModel for the fs tree
        self.fs_tree_model = QFileSystemModel()
        self.fs_tree_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.fs_tree_model.setRootPath(QDir.rootPath())

        # connect model to view
        self.fs_tree.setModel(self.fs_tree_model)
        # hide unneeded columns
        for column in range(1, self.fs_tree.header().count()):
            self.fs_tree.hideColumn(column)
        # expand root item
        self.fs_tree.expand(self.fs_tree_model.index(0, 0))

        # BOOKMARKS #
        self.bookmarks = bm(os.path.join(self.config_dir, 'bookmarks'))
        for bookmark in self.bookmarks.get_all():
            self.bookmark_view.addItem(bookmark['name'])

        # MOUNTS #
        self.udev_context = Context()
        self.mounts = mounts_model(context=self.udev_context)
        self.mounts_view.setModel(self.mounts)
        udev_monitor = Monitor.from_netlink(self.udev_context)
        udev_monitor.filter_by(subsystem='block', device_type='partition')
        udev_observer = MonitorObserver(udev_monitor,
                                        self.devices_changed)
        udev_observer.start()

        # STATUSBAR #
        # TODO: dir info
        self.item_info = QLabel()
        # self.dir_info = QLabel()
        self.part_info = QLabel()
        self.statusbar.addPermanentWidget(self.item_info)
        # self.statusbar.addPermanentWidget(self.dir_info)
        self.statusbar.addPermanentWidget(self.part_info)

        self.part_info.setText(utility.part_info(self.current_path))

        # TOOLBAR #
        # initially disable back/forward navigation
        self.action_back.setEnabled(False)
        self.action_forward.setEnabled(False)

        # main menu
        self.main_menu = QMenu()
        self.main_menu.addAction(self.action_show_hidden)

        self.menu_button = QToolButton()
        self.menu_button.setMenu(self.main_menu)
        self.menu_button.setPopupMode(QToolButton().InstantPopup)
        self.menu_button.setDefaultAction(self.action_menu)

        self.toolbar.insertWidget(self.action_back, self.menu_button)

        # adress bar
        self.adressbar = QLineEdit()
        self.adressbar.setText(self.current_path)
        self.toolbar.insertWidget(self.action_go, self.adressbar)

        # menu for new file or directory
        self.new_menu = QMenu()
        self.new_menu.addAction(self.action_new_dir)
        self.new_menu.addAction(self.action_new_file)

        self.new_button = QToolButton()
        self.new_button.setMenu(self.new_menu)
        self.new_button.setPopupMode(QToolButton().MenuButtonPopup)
        self.new_button.setDefaultAction(self.action_new_dir)

        self.toolbar.insertWidget(self.action_back, self.new_button)

        self.connect_actions_to_events()
        self.set_shortcuts()
        self.set_icons()
        self.set_context_menus()

    # ---------------- setup ----------------------------------------------- #
    def set_icons(self):
        """
        Adds icons to all applicable actions.
        """
        self.action_back.setIcon(QIcon.fromTheme('go-previous'))
        self.action_forward.setIcon(QIcon.fromTheme('go-next'))
        self.action_home.setIcon(QIcon.fromTheme('go-home'))
        self.action_up.setIcon(QIcon.fromTheme('go-up'))
        self.action_go.setIcon(QIcon.fromTheme('go-jump'))

        self.action_new_dir.setIcon(QIcon.fromTheme('folder-new'))
        self.action_new_file.setIcon(QIcon.fromTheme('document-new'))

        self.action_menu.setIcon(QIcon.fromTheme('start-here'))

        self.action_copy.setIcon(QIcon.fromTheme('edit-copy'))
        self.action_cut.setIcon(QIcon.fromTheme('edit-cut'))
        self.action_paste.setIcon(QIcon.fromTheme('edit-paste'))
        self.action_delete.setIcon(QIcon.fromTheme('edit-delete'))

        self.action_add_to_bookmarks.setIcon(QIcon.fromTheme('list-add'))
        self.action_remove_bookmark.setIcon(QIcon.fromTheme('list-remove'))

    def connect_actions_to_events(self):
        """
        Connects actions to their event functions.
        """
        self.adressbar.returnPressed.connect(self.action_go_event)
        self.action_go.triggered.connect(self.action_go_event)

        self.action_home.triggered.connect(self.action_home_event)
        self.action_up.triggered.connect(self.action_up_event)

        self.action_back.triggered.connect(self.action_back_event)
        self.action_forward.triggered.connect(self.action_forward_event)

        self.action_copy.triggered.connect(self.action_copy_event)
        self.action_copy_path.triggered.connect(self.action_copy_path_event)
        self.action_paste.triggered.connect(self.action_paste_event)
        self.action_cut.triggered.connect(self.action_cut_event)
        self.action_delete.triggered.connect(self.action_delete_event)
        self.action_rename.triggered.connect(self.action_rename_event)

        self.action_show_hidden.toggled.connect(self.action_show_hidden_event)

        self.action_new_dir.triggered.connect(self.action_new_dir_event)
        self.action_new_file.triggered.connect(self.action_new_file_event)

        self.action_add_to_bookmarks.triggered.connect(
            self.action_add_to_bookmarks_event)
        self.action_remove_bookmark.triggered.connect(
            self.action_remove_bookmark_event)
        self.bookmark_view.clicked.connect(self.bookmark_selected_event)

        self.fs_tree.clicked.connect(self.fs_tree_event)

        self.mounts_view.clicked.connect(self.mount_selected_event)
        self.mounts_view.doubleClicked.connect(self.mount_toggle_event)

        # TODO: enable open item on return pressed
        # self.table_view.returnPressed.connect(self.item_open_event)
        self.table_view.doubleClicked.connect(self.item_open_event)
        self.table_view.clicked.connect(self.item_selected_event)

    def set_shortcuts(self):
        """
        Set shortcuts for actions.
        """
        self.action_copy.setShortcuts(
            QKeySequence.keyBindings(QKeySequence.Copy))
        self.action_paste.setShortcuts(
            QKeySequence.keyBindings(QKeySequence.Paste))
        self.action_cut.setShortcuts(
            QKeySequence.keyBindings(QKeySequence.Cut))
        self.action_delete.setShortcuts(
            QKeySequence.keyBindings(QKeySequence.Delete))

    def set_context_menus(self):
        """
        Setup context menus.
        """
        self.table_view.addAction(self.action_copy)
        self.table_view.addAction(self.action_copy_path)
        self.table_view.addAction(self.action_paste)
        self.table_view.addAction(self.action_cut)
        self.table_view.addAction(self.action_rename)
        self.table_view.addAction(self.action_delete)
        # TODO: only show, if selected item is a folder
        self.table_view.addAction(self.action_add_to_bookmarks)
        self.table_view.addAction(self.action_show_hidden)

        self.bookmark_view.addAction(self.action_remove_bookmark)

    # ---------------- events ---------------------------------------------- #
    def action_new_dir_event(self):
        """
        Prompts the user for a dir name and creates one with that name in the
        current directory.
        """
        dir_name, ok = QInputDialog().getText(self,
                                              'Create new directory',
                                              'Directory name:')
        if (ok):
            if (dir_name):
                if not QDir().mkpath(os.path.join(self.current_path,
                                                  dir_name)):
                    dialog = utility.message_dialog('Directory could not be'
                                                    + ' created.',
                                                    QMessageBox.Critical)
                    dialog.exec()
            else:
                dialog = utility.message_dialog('Please enter a name for the '
                                                + 'new directory.',
                                                QMessageBox.Warning)
                dialog.exec()

    def action_new_file_event(self):
        """
        Prompts the user for a file name and creates one with that name in the
        current directory.
        """
        file_name, ok = QInputDialog().getText(self,
                                               'Create new file',
                                               'File name:')
        if (ok):
            if (file_name):
                try:
                    with open(os.path.join(self.current_path, file_name), 'a'):
                        pass
                except OSError:
                    dialog = utility.message_dialog('File cannot be created.',
                                                    QMessageBox.Warning)
                    dialog.exec()
            else:
                dialog = utility.message_dialog('Please enter a name for the'
                                                + ' new file.',
                                                QMessageBox.Warning)
                dialog.exec()

    def action_go_event(self):
        """
        Changes the current dir to the one, that is given in the adress bar.
        """
        next_dir = QDir(self.adressbar.text())
        if (next_dir.isAbsolute() and next_dir.exists()):
            next_path = next_dir.path()
            self.update_current_path(next_path)
        else:
            dialog = utility.message_dialog('The path entered does not exist.',
                                            QMessageBox.Warning)
            dialog.exec()

    def action_home_event(self):
        """
        Changes the current dir to the users $HOME.
        """
        next_path = QDir().homePath()
        self.update_current_path(next_path)

    def action_up_event(self):
        """
        Changes the current dir to one dir up in the hierarchy
        """
        dir_up = QDir(self.current_path)
        if (dir_up.cdUp()):
            next_path = dir_up.path()
            self.update_current_path(next_path)
        else:
            logging.warning('There is no directory above the one you are in.'
                            + ' This message should not occur, because the'
                            + ' button triggering this should be deactivated'
                            + ' Please report this issue.')

    def action_back_event(self):
        """
        Goes back one step in the navigation history. If after this, there are
        no more steps, it disables it's button.
        """
        next_path = self.back_stack.pop()
        self.forward_stack.push(self.current_path)
        self.action_forward.setEnabled(True)
        if (self.back_stack.empty()):
            self.action_back.setEnabled(False)
        self.update_current_path(next_path,
                                 skip_stack=True,
                                 reset_forward_stack=False)

    def action_forward_event(self):
        """
        Goes forward one step in the navigation history. If after this, there
        are no more steps, it disables it's button.
        """
        if (not self.forward_stack.empty()):
            next_path = self.forward_stack.pop()
            self.update_current_path(next_path, reset_forward_stack=False)
            # disable forward action if there are no more forward actions
            if (self.forward_stack.empty()):
                self.action_forward.setEnabled(False)
        else:
            logging.warning('Forward stack unexpectedly empty. This should not'
                            + ' happen, because the button triggering this'
                            + ' message should be deactivated. Please report'
                            + ' this issue.')

    def item_open_event(self):
        """
        Opens a file using xdg-open, runs it, if it is executeble or
        changes the current dir if it's dir.
        """
        selected_item = QFileInfo(
            os.path.join(self.current_path,
                         self.table_view.currentIndex().
                         siblingAtColumn(0).data()))
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
        else:
            dialog = utility.message_dialog('The type of the selected file can'
                                            + ' not be detected.',
                                            QMessageBox.Warning)
            dialog.exec()

    def item_selected_event(self):
        """
        Updates statusbar info, depending on the selected file.
        """
        selected_items = self.table_view.selectedIndexes()
        files = []
        if len(selected_items) > 1:
            for item in selected_items:
                files.append(os.path.join(self.current_path,
                                          item.siblingAtColumn(0).data()))
        else:
            # Update item_info in the statusbar
            path = os.path.join(self.current_path,
                                self.table_view.currentIndex().
                                siblingAtColumn(0).data())
            files.append(path)
        files = list(set(files))
        self.item_info.setText(utility.file_info(files))

    def fs_tree_event(self):
        """
        Changes the current dir to the dir selected in the fs_tree view.
        """
        next_path = self.fs_tree_model.filePath(self.fs_tree.currentIndex())
        self.update_current_path(next_path)

    def action_copy_event(self):
        """
        Copies the currently selected files to the clipboard.
        """
        # get current selection
        _, mime_data = utility.get_MIME(
            self.table_view.selectionModel().selectedIndexes())
        self.clipboard.setMimeData(mime_data)

    # TODO: allow multiple pastes at the same time
    def action_paste_event(self):
        """
        Pastes the files currently in the clipboard to the current dir.
        """
        # setup QProgressDialog
        self.progress_dialog = QProgressDialog(parent=self)
        self.progress_dialog.reset()
        self.progress_dialog.setMinimumDuration(1000)
        self.progress_dialog.setLabelText('Pasting...')
        self.progress_dialog.setValue(0)
        # setup paste_worker
        self.paste_thread = QThread()
        self.paste_worker = pw(clipboard=self.clipboard,
                               target_path=self.current_path,
                               marked_to_cut=self.marked_to_cut)
        self.paste_worker.moveToThread(self.paste_thread)
        self.paste_worker.is_canceled = False

        # canceled
        self.progress_dialog.canceled.connect(self.progress_dialog_cancel)
        # started
        self.paste_thread.started.connect(self.paste_worker.run)
        # ready
        self.paste_worker.ready.connect(self.progress_dialog_init)
        # progress
        self.paste_worker.progress.connect(self.progress_dialog_update)
        # finished
        self.paste_worker.finished.connect(self.paste_thread.quit)
        self.paste_worker.finished.connect(self.paste_worker.deleteLater)
        self.paste_worker.finished.connect(self.progress_dialog.reset)
        self.paste_thread.finished.connect(self.paste_thread.deleteLater)
        self.paste_thread.start()

    # TODO: visual feedback for cut files
    def action_cut_event(self):
        """
        Copies the current selection to the clipboard and marks them as cut.
        """
        self.marked_to_cut, mime_data = utility.get_MIME(
            self.table_view.selectionModel().selectedIndexes())
        self.clipboard.setMimeData(mime_data)

    def action_delete_event(self):
        """
        Throws the current selection in the trash after asking for
        confirmation.
        """
        path_list = utility.indexes_to_paths(
            self.table_view.selectionModel().selectedIndexes())
        if len(path_list) < 0:
            return

        if (len(path_list) == 1):
            confirmation_msg = ('Do you want to throw "'
                                + os.path.basename(path_list[0])
                                + '" in the trash?')
        else:
            confirmation_msg = ('Do you want to throw the '
                                + str(len(path_list))
                                + ' selected items and all the items contained'
                                + ' in them in the trash?')

        dialog = utility.question_dialog(confirmation_msg)
        button_clicked = dialog.exec()

        if (button_clicked == QMessageBox.Yes):
            for item in path_list:
                send2trash(item)

    # TODO: warn, if extension gets changed
    def action_rename_event(self):
        """
        Prompts the user to enter a new name and changes the selected file's
        name.
        """
        file_name = self.table_view.currentIndex().data()
        new_file_name, ok = QInputDialog().getText(self,
                                                   'Rename ' + file_name,
                                                   'New name:')
        if (ok):
            if (new_file_name):
                QFile().rename(os.path.join(self.current_path, file_name),
                               os.path.join(self.current_path, new_file_name))
            else:
                dialog = utility.message_dialog('Please enter the new name '
                                                + 'for the file.',
                                                QMessageBox.Warning)
                dialog.exec()

    def action_show_hidden_event(self):
        """
        Shows hidden files and dirs in the main view.
        """
        if self.action_show_hidden.isChecked():
            self.filesystem.setFilter(QDir.AllEntries
                                      | QDir.NoDotAndDotDot
                                      | QDir.AllDirs
                                      | QDir.Hidden)
        else:
            self.filesystem.setFilter(QDir.AllEntries
                                      | QDir.NoDotAndDotDot
                                      | QDir.AllDirs)

    def action_copy_path_event(self):
        """
        Copy path of currently selected item to clipboard.
        """
        path = os.path.join(self.current_path,
                            self.table_view.currentIndex().siblingAtColumn(0)
                            .data())
        self.clipboard.setText(path)

    def action_add_to_bookmarks_event(self):
        """
        Adds the selected dir to the bookmark by the name the user gave it via
        a dialog.
        """
        path = os.path.join(self.current_path,
                            self.table_view.currentIndex().data())
        if (os.path.isdir(path)):
            name, ok = QInputDialog().getText(self,
                                              'Create new bookmark',
                                              'Bookmark name:',
                                              text=self.table_view.
                                              currentIndex().data())
            if (ok):
                if (name):
                    self.bookmarks.add_bookmark(name, path)
                    self.bookmark_view.addItem(name)
                else:
                    dialog = utility.message_dialog('Please enter name for'
                                                    + ' the bookmark.',
                                                    QMessageBox.Warning)
                    dialog.exec()
        else:
            dialog = utility.message_dialog('Please select a directory, not'
                                            + ' a file, to create a bookmark.',
                                            QMessageBox.Warning)
            dialog.exec()

    def action_remove_bookmark_event(self):
        """
        Removes the selected bookmark after asking the user for confirmation.
        """
        name = self.bookmark_view.currentIndex().data()
        dialog = utility.question_dialog('Do you really want to delete this '
                                         + 'bookmark ('
                                         + name
                                         + ')?')
        button_clicked = dialog.exec()

        if (button_clicked == QMessageBox.Yes):
            self.bookmark_view.takeItem(
                self.bookmark_view.row(
                    self.bookmark_view.itemFromIndex(
                        self.bookmark_view.currentIndex())))
            self.bookmarks.remove_bookmark(name)

    def bookmark_selected_event(self):
        """
        Changes the current dir to the one associated with the selected
        bookmark.
        """
        next_path = self.bookmarks.get_path_from_name(
            self.bookmark_view.currentIndex().data())
        self.update_current_path(next_path)

    def mount_selected_event(self):
        """
        Checks the mount point of the selected drive and makes it the current
        path.
        """
        try:
            device = self.mounts.get_device_at(
                self.mounts_view.currentIndex().row())
        except IndexError:
            logging.critical('Device index out of range. This should never '
                             + 'happen, please report this error.')
            exit(1)
        mount_point = self.mounts.get_mount_point(device)
        if mount_point != '':
            self.update_current_path(mount_point)

    # TODO: handle performance better
    def mount_toggle_event(self):
        """
        Tries to mount or unmount the selected drive.
        """
        try:
            device = self.mounts.get_device_at(
                self.mounts_view.currentIndex().row())
        except IndexError:
            logging.critical('Device index out of range. This should never '
                             + 'happen, please report this error.')
            exit(1)
        former_mount_point = self.mounts.get_mount_point(device)
        try:
            self.mounts.toggle_mount(device)
        except CalledProcessError:
            dialog = utility.message_dialog('udevil was unable to mount or'
                                            + ' unmount this devices. Please'
                                            + ' check, if it is installed'
                                            + ' correctly and report this'
                                            + ' error, if the problem'
                                            + ' presists.',
                                            QMessageBox.Critical)
            dialog.exec()
            return
        mount_point = self.mounts.get_mount_point(device)
        if mount_point != '':
            self.mount_selected_event()
        elif former_mount_point == self.current_path:
            self.update_current_path(self.default_path)

    # ---------------- functions ------------------------------------------- #
    # TODO: Performance
    def update_current_path(self,
                            next_path: str,
                            skip_stack=False,
                            reset_forward_stack=True):
        """
        Updates the current path to the value given in next_path. It also
        updates the UI accordingly and changes the forward an backward
        stacks, if needed.

        :param next_path: The path to the directory that should become the next
                          dir.
        :type next_path: str
        :param skip_stack: This determines wether the stack handling should be
                           skipped. Default value is False.
        :type skip_stack: bool
        :param reset_forward_stack: This determines wether the forward stack
                                    should be reset or not. Default is True
        :type reset_forward_stack: bool
        """
        self.filesystem.setRootPath(next_path)
        self.table_view.setRootIndex(
            self.filesystem.index(next_path))
        self.adressbar.setText(next_path)
        # update directory and partition information
        # self.update_dir_info(next_path)
        self.part_info.setText(utility.part_info(next_path))
        # disable up navigation if in fs root
        if (next_path == QDir().rootPath()):
            self.action_up.setEnabled(False)
        else:
            self.action_up.setEnabled(True)
        # handle back stack
        if (not skip_stack):
            if (self.back_stack.empty()
                    or self.back_stack.top() != self.current_path):
                self.back_stack.push(self.current_path)
                # reenable back navigation
                self.action_back.setEnabled(True)
        if (reset_forward_stack):
            self.forward_stack.drop()
            self.action_forward.setEnabled(False)
        self.current_path = next_path

    def devices_changed(self, action: str, device: Device):
        """
        Updates the mountable devices. Is run, when udev detects a change in
        the block device subsystem.

        :param action: Action that happened to the block device.
        :type action: str
        :param device: Device that changed it's status.
        :type device: Device
        """
        if action == 'add':
            self.mounts.add(device)
        elif action == 'remove':
            self.mounts.remove(device)

    def progress_dialog_init(self, maximum: int):
        """
        Initializes the progress dialog and sets its maximum value.

        :param maximum: The total amount of files to be pasted.
        :type maximum: int
        """
        self.progress_dialog.setMaximum(maximum)
        self.files_to_paste_count = maximum

    def progress_dialog_update(self, value: int):
        """
        Updates the progress dialog.

        :param value: Amount of files already pasted.
        :type value: int
        """
        self.progress_dialog.setValue(value)
        self.progress_dialog.setLabelText('Pasting file '
                                          + str(value)
                                          + ' of '
                                          + str(self.files_to_paste_count)
                                          + '...')

    def progress_dialog_cancel(self):
        """
        Tells the paste worker to cancel its work
        """
        self.paste_worker.is_canceled = True
