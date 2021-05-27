import os
import collections
from typing import List

from PySide2.QtCore import QObject, QDir, QFile, Signal
from PySide2.QtGui import QClipboard

import tfm.utility as utility


class paste_worker(QObject):
    """
    Worker class, that is used to paste files in a different thread.

    Signals:
    **finished**: is emitted, when the worker is done
    **started**: is emitted, when the worker starts and the clipboard is not
    empty
    **ready**: is emitted, when all file paths to paste are collected,
    contains the number of files to paste as int
    **progress**: is emitted, whenever a file is done being pasted,
    contains the number of files pasted so far
    """
    finished = Signal()
    started = Signal()
    ready = Signal(int)
    progress = Signal(int)

    def __init__(self,
                 *args,
                 clipboard: QClipboard,
                 target_path: str,
                 marked_to_cut: List[str],
                 **kwargs):
        """
        Calls QObject constructor and initializes the clipboard, the current
        path and the list of files, that are marked to cut. It also initializes
        the is_canceld property to False.

        :param clipboard: The clipboard containing the file URLs that will be
                          pasted.
        :type clipboard: QClipboard
        :param target_path: Path, where the files should be pasted to.
        :type target_path: str
        :param marked_to_cut: A list of file paths, which shold be deleted
                              after pasting.
        :type marked_to_cut: List[str]
        """
        super(paste_worker, self).__init__(*args, **kwargs)
        self.clipboard = clipboard
        self.target_path = target_path
        self.marked_to_cut = marked_to_cut

        self.is_canceled = False

    def get_paths_from_clipboard(self) -> List[str]:
        """
        Extracts file paths from file URLs in the clipboard.

        :return: List of file paths
        :rtype: List[str]
        """
        path_list = []
        for url in self.clipboard.mimeData().urls():
            if (url.isLocalFile()):
                path_list.append(url.toLocalFile())
        return path_list

    def recurse_dirs(self, path_list: List[str]) -> List[str]:
        """
        Recurses all directories in the given list of paths and adds the
        files and directories found there to the given list.

        :param path_list: List of file paths
        :type path_list: List[str]
        :return: The original list of file paths extended by the contents
                 of any directory in the original list
        :rtype: List[str]
        """
        paths_to_add = []
        for path in path_list:
            if (os.path.isdir(path)):
                paths_to_add.extend(utility.traverse_dir(path))
        path_list.extend(paths_to_add)
        return path_list

    def count_files(self, path_list: List[str]):
        """
        Counts all files (and not directories) in the give list of paths.

        :param path_list: List of file paths
        :type path_list: List[str]
        """
        file_count = 0
        for path in path_list:
            if os.path.isfile(path):
                file_count += 1
        return file_count

    def get_base_path(self, path_list: List[str]):
        """
        Determines the largest common path of the files in the given list of
        paths.

        :param path_list: List of file paths
        :type path_list: List[str]
        """
        if (len(path_list) > 1):
            return os.path.commonpath(path_list) + '/'
        return (os.path.dirname(os.path.commonpath(path_list)) + '/')

    # Handle existing files better -> skip, overwrite, rename
    def run(self):
        """
        Main logic. Pastes the files from the clipboard to the target path.
        """
        if self.clipboard.mimeData().hasUrls():
            self.started.emit()

            path_list = self.get_paths_from_clipboard()

            cut = (collections.Counter(path_list)
                   == collections.Counter(self.marked_to_cut))

            path_list = self.recurse_dirs(path_list)

            files_copied = 0
            self.ready.emit(self.count_files(path_list))

            base_path = self.get_base_path(path_list)

            # copy files to new location
            for path in path_list:
                if self.is_canceled:
                    break

                new_path = os.path.join(self.target_path,
                                        path.replace(base_path, ''))
                if (os.path.isdir(path)
                        and not QDir().exists(new_path)):
                    QDir().mkpath(new_path)
                elif (QFile().exists(path)
                        and not QFile().exists(new_path)):
                    if (QFile().copy(path, new_path)):
                        files_copied += 1
                        self.progress.emit(files_copied)
                    else:
                        raise OSError
            # removed cut files
            if cut:
                for file_path in path_list:
                    if (not QFile().remove(file_path)):
                        raise OSError
        self.finished.emit()
