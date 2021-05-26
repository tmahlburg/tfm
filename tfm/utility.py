# This file contains misc utility functions. Better structuring is planned in
# the future.
import os
from typing import List, Tuple

from PySide2.QtWidgets import QFileSystemModel, QMessageBox
from PySide2.QtCore import QDir, QFileInfo, QMimeData, QUrl

from prefixed import Float


def indexes_to_paths(files_as_indexes: List) -> List[str]:
    """
    Converts the given indexes to a list of paths.

    :param files_as_indexes: List of indexes of files.
    :type files_as_indexes: List
    :return: List of paths to the given files.
    :rtype: List
    """
    files_as_path = []
    for index in files_as_indexes:
        if (index.column() == 0):
            files_as_path.append(QFileSystemModel().filePath(index))
    return files_as_path


def traverse_dir(path) -> List[str]:
    """
    Traverses the given directory and returns all files and dirs inside as
    paths.

    :param path: Path to traverse.
    :type path: str
    :return: Paths of files and dirs under the given path.
    :rtype: List[str]
    """
    path_list = []
    for root, dirs, files in os.walk(path):
        for item in files:
            path_list.append(os.path.join(root, item))
        for item in dirs:
            path_list.append(os.path.join(root, item))
    return path_list


# TODO: retrieve partition name (/dev/xxxxxxmpn)
def part_info(path: str) -> str:
    """
    Retrieves information about the partition which the path is on.
    :param path: Path on the partition.
    :type path: str
    :return: Decription of the partition.
    :rtype: str
    """
    # get fs statistics using statvfs system call
    part_stats = os.statvfs(path)
    fs_size = '{:!.1j}B'.format(Float(part_stats.f_frsize
                                      * part_stats.f_blocks))
    fs_free = '{:!.1j}B'.format(Float(part_stats.f_frsize
                                      * part_stats.f_bfree))
    return (fs_free + ' of ' + fs_size + ' free')


# TODO: calculate dir sizes
def file_info(paths: List[str]) -> str:
    """
    Retrieves information about the given files.

    :param path: Path to the files.
    :type path: List[str]
    :return: Information of the file.
    :rtype: str
    """
    size = 0
    for path in paths:
        file = QFileInfo(path)
        if (file.isFile()):
            size += file.size()
        elif (len(paths) > 1):
            return str(len(paths)) + ' items selected'
    size = '{:!.2j}B'.format(Float(size))
    if (len(paths) > 1):
        return str(len(paths)) + ' files selected, using ' + size
    file = QFileInfo(paths[0])
    if (file.isFile()):
        return (os.path.basename(path) + ': ' + size)
    return (os.path.basename(path))


def question_dialog(msg: str) -> QMessageBox:
    """
    Creates a default question dialog box.

    :param msg: The question which the user is asked.
    :type msg: str
    :return: The created dialog.
    :rtype: QMessageBox
    """
    msg_box = QMessageBox()
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
    msg_box.setDefaultButton(QMessageBox.Yes)
    msg_box.setIcon(QMessageBox.Question)
    return msg_box


def message_dialog(msg: str, type: QMessageBox.Icon) -> QMessageBox:
    """
    Creates a default message dialog box.

    :param msg: The message which should be communicated to the user.
    :type msg: str
    :param type: The type of the message.
    :type type: QMessageBox.Icon
    :return: The created dialog.
    :rtype: QMessageBox
    """
    msg_box = QMessageBox()
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setDefaultButton(QMessageBox.Ok)
    msg_box.setIcon(type)
    return msg_box


def get_MIME(files_as_indexes: List) -> Tuple[List[str], List[QUrl]]:
    """
    Converts the given files to their MIME data.

    :param files_as_indexes: List of indexes of files.
    :type files_as_indexes: List
    :return: files as str list of path and the MIME data of the given files.
    :rtype: Tuple[List[str], List[QUrl]]
    """
    files_as_path = indexes_to_paths(files_as_indexes)
    file_urls = []

    for file in files_as_path:
        file_urls.append(QUrl.fromLocalFile(file))

    mime_data = QMimeData()
    mime_data.setUrls(file_urls)

    return files_as_path, mime_data


def handle_args(args: List[str]) -> str:
    """
    Handles the given arguments, determining the starting dir.

    :param args: List of arguments given to the application.
    :type args: List[str]
    :return: The directory to start the application with.
    :rtype: str
    """
    if len(args) > 1:
        if os.path.isdir(args[1]):
            return args[1]
        if QUrl(args[1]).isValid() and os.path.isdir(QUrl(args[1]).path()):
            return QUrl(args[1]).path()
    return QDir.homePath()
