from abc import ABCMeta, abstractmethod
import os

def get_inode(file):
    #  type: (str) -> int
    return os.stat(file).st_ino

class DeviceBase(object):
    """
    This Class define the function that must be implemented by device function.
    """
    def __init__(self,
                 device: str,
                 readwrite: bool,
                 detect_replugged: bool):
        """
        initialize a  new instance of a DeviceBase
        :param device: the file descriptor
        :param readwrite: access type
        :param detect_replugged: detects device unplugged and plugged events and ensure executions will not fail
        silently due to replugged events
        """
        self._file_name = device
        self._read_write = readwrite
        self._detect_replugged = detect_replugged
        # The devcie type
        self._devicetype = None

    def __del__(self):
        self.close() 

    def __enter__(self):
        """
        :return: return the class itself
        """
        return self

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        """

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()

    def __repr__(self):
        """

        :return:
        """
        return self.__class__.__name__

    @abstractmethod
    def _is_replugged(self):
        """ Methmod to detect if a devcie plugged. """

    @abstractmethod
    def open(self):
        """ Methmod to open a devcie. """

    @abstractmethod
    def close(self):
        """ Methmod to close a devcie. """

    @abstractmethod
    def execute(self, cmd):
        """ Methmod to execute a command to the devcie. """

    @property
    def opcodes(self):
        """
        This maybe unnecessary sometimes, to maintain consistency with pyscsi.pyscsi.scsi_device

        :return: the opcode used by command
        """
        return self._opcodes

    @opcodes.setter
    def opcodes(self, value):
        """
        Setting opcodes, maybe unnecessary sometimes, to maintain consistency with 
        pyscsi.pyscsi.scsi_device
        :param value: opcode instance that used by command

        :return:
        """
        self._opcodes = value

    @property
    def devicetype(self):
        """
        This maybe unnecessary sometimes, to maintain consistency with pyscsi.pyscsi.scsi_device

        :return: the devicetype of the device
        """
        return self._devicetype

    @devicetype.setter
    def devicetype(self, value):
        """
        Setting devicetype, maybe unnecessary sometimes, to maintain consistency with 
        pyscsi.pyscsi.scsi_device
        :param value: devicetype instance that used by device

        :return:
        """
        self._devicetype = value



class LinIOCTLDevice(DeviceBase):
    """
    The IOCTL device class for Linux
    A basic workflow for using a device would be:
        - try to open the device passed by the device arg
        - before execute the command, check the replugge event, reopen the device if necessary.
        - execute the command
        - close the device after all the commands.
    """
    def __init__(self, 
                 device,
                 readwrite=True,
                 detect_replugged=True):
        """
        initialize a new instance of a LinIOCTLDevice
        :param device: the file descriptor
        :param readwrite: access type
        :param detect_replugged: detects device unplugged and plugged events and ensure executions will not fail
        silently due to replugged events
        """
        super(LinIOCTLDevice, self).__init__(device, readwrite, detect_replugged)
        ## init the ioctl engine
        from fcntl import ioctl
        self._ioctl = ioctl
        ##
        self._file = None
        self._ino = None
        ## open device
        self.open()

    def _is_replugged(self):
        """
        check if the devide is replugged

        :return: True or False
        """
        ino = get_inode(self._file_name)
        return ino != self._ino

    @property
    def device_name(self):
        """
        get the device name

        :return: device name, string like sdb or nvme1
        """
        return self._file_name.replace("/dev/", "")

    def open(self):
        """
        open the device, it will close the device if the device is opened.

        :return: None
        """
        if self._file:
            self.close()
        self._file = open(self._file_name,
                          'w+b' if self._read_write else 'rb')
        self._ino = get_inode(self._file_name)

    def close(self):
        """
        close the device if the device is opened.

        :return: None
        """
        if self._file:
            self._file.close()
            self._file = None
            self._ino = None

    def execute(self, op: int, cdb):
        """
        execute a command (admin, IO)

        :param op: a operation code used by cdb
        :param cdb: a 
        :return: a ioctl return code
        """
        if self._detect_replugged and self._is_replugged():
            try:
                self.close()
            finally:
                self.open()

        ##
        result = None
        result = self._ioctl(self._file.fileno(), 
                             op, 
                             cdb if cdb else 0)
        return result
