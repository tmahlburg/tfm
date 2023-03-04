import os
import tarfile
import zipfile
import rarfile

from PySide6.QtCore import QRunnable, QObject, QFileInfo, Signal, Slot


class extract_signals(QObject):
    """
    QObject class to hold the signals for the extract worker, which can't do
    that, because it a subclass of QRunnable.

    Signals:
    **finished**: is emitted, when the worker is done.
    **started**: is emitted, when the worker starts.
    **ready**: is emitted, when the archive is opened and contains the number
               of files in it are known.
    **progress**: is emitted, whenever a file is done being extracted from the
                  archive, contains the number of files extracted so far.
    **progress_message**: is emitted, whenever **progress** is emitted, but is
                          a formatted string containing the information about
                          what is happening.
    """

    finished = Signal()
    started = Signal()
    ready = Signal(int)
    progress_message = Signal(str)
    progress = Signal(int)


class extract_worker(QRunnable):
    """
    Worker class, that is used to extract archives in a different thread.
    """

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
        self.signals = extract_signals()

        self.is_canceled = False
        self.maximum = 0

    def progress_str(self, file_count: int) -> str:
        return ('Extracting file ' + str(file_count) + ' of ' +
                str(self.maximum) + '...')

    @Slot()
    def cancel(self):
        self.is_canceled = True

    @Slot()
    def run(self):
        """
        Main logic. Extracts the archive to a directory with the same name.
        """
        self.signals.started.emit()

        # define target directory
        target_dir = QFileInfo(self.archive_path)
        target_dir = os.path.join(target_dir.path(),
                                  target_dir.completeBaseName())

        while (os.path.isdir(target_dir)):
            target_dir += '_'

        if tarfile.is_tarfile(self.archive_path):
            with tarfile.TarFile(self.archive_path, 'r') as archive:
                self.maximum = len(archive.getnames())
                self.signals.ready.emit(self.maximum)
                file_count = 0
                self.signals.progress.emit(file_count)
                self.signals.progress_message.emit(self.progress_str(
                                                   file_count))
                for file in archive.get_members():
                    if self.is_canceled:
                        break
                    archive.extract(file, target_dir)
                    file_count += 1
                    self.signals.progress.emit(file_count)
                    self.signals.progress_message.emit(self.progress_str(
                                                       file_count))

        elif zipfile.is_zipfile(self.archive_path):
            with zipfile.ZipFile(self.archive_path, 'r') as archive:
                self.maximum = len(archive.namelist())
                self.signals.ready.emit(self.maximum)
                file_count = 0
                self.signals.progress.emit(file_count)
                self.signals.progress_message.emit(self.progress_str(
                                                   file_count))
                for file in archive.infolist():
                    if self.is_canceled:
                        break
                    archive.extract(file, target_dir)
                    file_count += 1
                    self.signals.progress.emit(file_count)
                    self.signals.progress_message.emit(self.progress_str(
                                                       file_count))

        elif rarfile.is_rarfile(self.archive_path):
            with rarfile.RarFile(self.archive_path, 'r') as archive:
                self.maximum = len(archive.namelist())
                self.signals.ready.emit(self.maximum)
                file_count = 0
                self.signals.progress.emit(file_count)
                self.signals.progress_message.emit(self.progress_str(
                                                   file_count))
                for file in archive.infolist():
                    if self.is_canceled:
                        break
                    archive.extract(file, target_dir)
                    file_count += 1
                    self.signals.progress.emit(file_count)
                    self.signals.progress_message.emit(self.progress_str(
                                                       file_count))

        self.signals.finished.emit()
