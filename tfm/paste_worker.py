import os
import collections
from typing import List

from PySide2.QtCore import QObject, QDir, QFile, Signal, QMimeData
from PySide2.QtGui import QClipboard


class paste_worker(QObject):
    """
    Worker class, that is used to paste files in a different thread.
    """
    finished = Signal()
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

    # TODO: progress / status information, support folders, handle existing
    # file(s)
    def run(self):
        if self.clipboard.mimeData().hasUrls():
            # get paths from URLs in clipboard
            path_list = []
            for url in self.clipboard.mimeData().urls():
                if (url.isLocalFile()):
                    path_list.append(url.toLocalFile())

            multiple_paths = (len(path_list) > 1)
            cut = (collections.Counter(path_list)
                   == collections.Counter(self.marked_to_cut))

            # add paths inside of copied dirs
            paths_to_add = []
            for path in path_list:
                if (os.path.isdir(path)):
                    paths_to_add.extend(utility.traverse_dir(path))
            path_list.extend(paths_to_add)

            # determine common base path of the files
            base_path = ''
            if (multiple_paths):
                base_path = os.path.commonpath(path_list) + '/'
            else:
                base_path = (os.path.dirname(os.path.commonpath(path_list))
                             + '/')

            # copy files to new location
            for path in path_list:
                new_path = os.path.join(self.current_path,
                                        path.replace(base_path, ''))
                if (os.path.isdir(path)
                        and not QDir().exists(new_path)):
                    QDir().mkpath(new_path)
                elif (QFile().exists(path)
                        and not QFile().exists(new_path)):
                    QFile().copy(path, new_path)
            # removed cut files
            if cut:
                for file_path in path_list:
                    QFile().remove(file_path)
        self.finished.emit()
