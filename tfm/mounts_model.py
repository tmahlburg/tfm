from typing import List
from subprocess import run, PIPE

from pyudev import Device, Context

from PySide2.QtCore import QAbstractListModel, Qt
from PySide2.QtGui import QIcon


class mounts_model(QAbstractListModel):
    """
    Provides a Qt-compatible data model, handling the listing and mounting of
    devices.
    """

    def __init__(self, *args, context: Context, **kwargs):
        """
        Finds available mounts using udev and the given context.

        :param context: The udev context this class is used in.
        :type context: Context
        """
        super(mounts_model, self).__init__(*args, **kwargs)
        self.context = context
        self.devices = self.get_available_mounts()

    def data(self, index: int, role: int):
        """
        Returns the data of the object in a Qt-conforming way. If the given
        role is DisplayRole it returns the name of the device as a string, if
        it's DecorationRole it returns an icon according to it's mount state.

        :param index: Index of the item in the data structure.
        :type index: int
        :param role: Item role according to Qt.
        :type role: int
        :return: Device name or icon according to mount state.
        """
        if role == Qt.DisplayRole:
            return self.devices[index.row()].sys_name
        if role == Qt.DecorationRole:
            if (self.get_mount_point(self.devices[index.row()]) != ''):
                return QIcon.fromTheme('media-eject')
            else:
                return QIcon.fromTheme('drive-harddisk')

    def rowCount(self, index: int) -> int:
        """
        Returns the number of mountable devices in a Qt-conforming way.

        :param index: unused, but needed by Qt.
        :type index: int
        :return: Number of mountable devices.
        :rtype: int
        """
        return len(self.devices)

    def get_device_at(self, index: int) -> Device:
        """
        Returns the device at the given index.

        :param index: Index of the wanted device.
        :type index: int
        :return: The device at the index in the model.
        :rtype: Device
        """
        if (index >= 0 and index < len(self.devices)):
            return self.devices[index]
        else:
            raise IndexError

    def add(self, device: Device):
        """
        Adds a device to the model, if it's not already a part of it.

        :param device: The device to add.
        :type device: Device
        """
        if device not in self.devices:
            self.devices.append(device)

    def remove(self, device: Device):
        """
        Removes a device out of the model, if it exists.

        :param device: The device to remove.
        :type device: Device
        """
        if device in self.devices:
            self.devices.remove(device)

    def get_mount_point(self, device: Device) -> str:
        """
        Looks for a mount point of the given device, using the findmnt
        command. Returns an empty string, if there is none.

        :param device: The device, of which the mount point is needed.
        :type device: Device
        :return: The mount point or an empty string, if it doesn't exists
        :rtype: str
        """
        return run(['findmnt',
                    '-n',
                    '-o',
                    'target',
                    '/dev/' + device.sys_name],
                   text=True,
                   stdout=PIPE,
                   stderr=PIPE,
                   universal_newlines=True).stdout.strip()

    def toggle_mount(self, device: Device):
        """
        Mounts an unmounted device or unmounts a mounted device using the
        udevil command.

        :param device: The device to mount or unmount.
        :type device: Device
        """
        mount_point = self.get_mount_point(device)
        if (mount_point != ''):
            run(['udevil', '--quiet', 'umount', mount_point], check=True)
        else:
            run(['udevil', '--quiet', 'mount', '/dev/' + device.sys_name],
                check=True)

    def get_available_mounts(self) -> List[Device]:
        """
        Returns a list of mountable partitions.

        :return: List of mountable partitions
        :rtype: List[Device]
        """
        mountable_devices = []
        for dev in self.context.list_devices(subsystem='block',
                                             DEVTYPE='partition'):
            mountable_devices.append(dev)
        return mountable_devices
