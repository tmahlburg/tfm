import os
import tarfile
import zipfile

from PySide6.QtCore import QObject, QFileInfo, Signal, Slot


class extract_worker(QObject):
    """
    Worker class, that is used to extract archives in a different thread.

    Signals:
    **finished**: is emitted, when the worker is done.
    **started**: is emitted, when the worker starts.
    **ready**: is emitted, when the archive is opened and contains the number
               of files in it are known.
    **progress**: is emitted, whenever a file is done being extracted from the
                  archive, contains the number of files extracted so far.
    """
    finished = Signal()
    started = Signal()
    ready = Signal(int)
    progress = Signal(int)

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

        self.is_canceled = False

    @Slot()
    def cancel(self):
        self.is_canceled = True

    def run(self):
        """
        Main logic. Extracts the archive to a directory with the same name.
        """
        self.started.emit()

        # define target directory
        target_dir = QFileInfo(self.archive_path)
        target_dir = os.path.join(target_dir.path(),
                                  target_dir.baseName())

        while (os.path.isdir(target_dir)):
            target_dir += '_'

        if tarfile.is_tarfile(self.archive_path):
            with tarfile.TarFile(self.archive_path, 'r') as archive:
                self.ready.emit(len(archive.getnames()))
                file_count = 0
                self.progress.emit(file_count)
                for file in archive.get_members():
                    if self.is_canceled:
                        break
                    archive.extract(file, target_dir)
                    file_count += 1
                    self.progress.emit(file_count)

        elif zipfile.is_zipfile(self.archive_path):
            with zipfile.ZipFile(self.archive_path, 'r') as archive:
                self.ready.emit(len(archive.namelist()))
                file_count = 0
                self.progress.emit(file_count)
                for file in archive.infolist():
                    if self.is_canceled:
                        break
                    archive.extract(file, target_dir)
                    file_count += 1
                    self.progress.emit(file_count)

        self.finished.emit()
