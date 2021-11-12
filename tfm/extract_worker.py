import os
from tarfile import is_tarfile
from zipfile import is_zipfile
from shutil import unpack_archive

from PySide6.QtCore import QObject, QFileInfo, Signal


class extract_worker(QObject):
    """
    Worker class, that is used to extract archives in a different thread.

    Signals:
    **finished**: is emitted, when the worker is done
    **started**: is emitted, when the worker starts and the given path is
                 actually an archive.
    """
    finished = Signal()
    started = Signal()

    def __init__(self,
                 *args,
                 archive_path: str,
                 **kwargs):
        """
        Calls QObject constructor and takes the path of the archive.

        :param archive_path: Path, where the archive is located at.
        :type archive_path: str
        """
        super(extract_worker, self).__init__(*args, **kwargs)
        self.archive_path = archive_path

    # Handle existing files better -> skip, overwrite, rename
    def run(self):
        """
        Main logic. Extracts the archive to a directory with the same name.
        """
        if is_tarfile(self.archive_path) or is_zipfile(self.archive_path):
            self.started.emit()

            target_dir = QFileInfo(self.archive_path)
            target_dir = os.path.join(target_dir.path(),
                                      target_dir.baseName())

            while (os.path.isdir(target_dir)):
                target_dir += '_'
            unpack_archive(self.archive_path, target_dir)

        self.finished.emit()
