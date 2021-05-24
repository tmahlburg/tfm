import os
import collections
import shutil
from typing import List

from PySide2.QtCore import QObject, QDir, QFile, Signal
from PySide2.QtGui import QClipboard

import tfm.utility as utility


class paste_worker(QObject):
    """
    Worker class, that is used to paste files in a different thread.
    """
    # emitted, when the worker is done
    finished = Signal()
    # emitted, when the worker starts and clipboard is not empty
    started = Signal()
    # emitted, when all file paths to paste are collected
    # also emits the number of files to paste
    ready = Signal(int)
    # emits the number of files that are pasted
    progress = Signal(int)

    def __init__(self,
                 *args,
                 clipboard: QClipboard,
                 current_path: str,
                 marked_to_cut: List[str],
                 **kwargs):
        super(paste_worker, self).__init__(*args, **kwargs)
        self.clipboard = clipboard
        self.current_path = current_path
        self.marked_to_cut = marked_to_cut

    def get_paths_from_clipboard(self):
        path_list = []
        for url in self.clipboard.mimeData().urls():
            if (url.isLocalFile()):
                path_list.append(url.toLocalFile())
        return path_list

    def recurse_dirs(self, path_list):
        paths_to_add = []
        for path in path_list:
            if (os.path.isdir(path)):
                paths_to_add.extend(utility.traverse_dir(path))
        path_list.extend(paths_to_add)
        return path_list

    def count_files(self, path_list):
        file_count = 0
        for path in path_list:
            if (QFile().exists(path)):
                file_count += 1
        return file_count

    def get_basepath(self, path_list, multiple_paths):
        if (multiple_paths):
            return os.path.commonpath(path_list) + '/'
        return (os.path.dirname(os.path.commonpath(path_list)) + '/')

    # TODO: handle existing file(s), handle errors related to permissions
    def run(self):
        if self.clipboard.mimeData().hasUrls():
            self.started.emit()

            path_list = self.get_paths_from_clipboard()
            multiple_paths = (len(path_list) > 1)

            cut = (collections.Counter(path_list)
                   == collections.Counter(self.marked_to_cut))

            path_list = self.recurse_dirs(path_list)

            # TODO:
            files_copied = 0
            self.ready.emit(count_files(path_list))
            self.progress.emit(files_copied)

            basepath = get_basepath(self, file_path, multiple_paths)

            # copy files to new location
            for path in path_list:
                print(path)
                new_path = os.path.join(self.current_path,
                                        path.replace(base_path, ''))
                print(new_path)
                if (os.path.isdir(path)
                        and not QDir().exists(new_path)):
                    QDir().mkpath(new_path)
                elif (QFile().exists(path)
                        and not QFile().exists(new_path)):
                    # TODO: handle errors related to permissions
                    err = QFile().copy(path, new_path)
                    print(err)
                    # communicate progress
                    files_copied += 1
                    self.progress.emit(files_copied)
            # removed cut files
            if cut:
                # TODO: handle errors related to permissions
                for file_path in path_list:
                    QFile().remove(file_path)
        self.finished.emit()
