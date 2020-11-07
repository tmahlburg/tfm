# This file contains misc utility functions. Better structuring is planned in
# the future.
import os
from typing import List

from PySide2.QtWidgets import QFileSystemModel
from PySide2.QtCore import QDir, QFileInfo

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


# TODO: replace with os.walk from python std lib.....
def traverse_dir(path) -> List[str]:
    """
    Traverses the given directory and returns all files and dirs inside as
    paths.
    :param path: Path to traverse.
    :type path: str
    :return: Paths of files and dirs under the given path.
    :rtype: List[str]
    """
    dir = (path)
    path_list = []
    for file_name in dir.entryList(filters=QDir.AllDirs
                                   | QDir.NoDotAndDotDot
                                   | QDir.Files
                                   | QDir.Hidden):
        current_path = os.path.join(path, file_name)
        path_list.append(current_path)
        if (QDir().exists(current_path)):
            path_list.extend(traverse_dir(current_path))
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


# TODO: handle multiple paths and calculate dir sizes
def item_info(path: str) -> str:
    """
    Retrieves information about the given file.
    :param path: Path to the file.
    :type path: str
    :return: Information of the file.
    :rtype: str
    """
    file = QFileInfo(path)
    if (file.isFile()):
        size = '{:!.2j}B'.format(Float(file.size()))
        return (os.path.basename(path) + ': ' + size)
    return (os.path.basename(path))
