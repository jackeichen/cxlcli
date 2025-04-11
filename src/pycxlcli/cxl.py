import os
from .linux_device import LinIOCTLDevice
from .command_structure import (
    get_cxl_mem_query_commands,
    cxl_send_command,
    sizeof,
    addressof)
from .linux_utils import CXLBusInfo
from .linux_cxl_ioctl import cxl_mem_command_ioctl
from .identify_memory_device import cxlmi_cmd_memdev_identify_payload
from pycxlcli.linux_cxl_ioctl import cxl_command_names


class cxl_command_info(object):
    def __init__(self, command_info):
        self.__command_info = command_info

    @property
    def id(self):
        return self.__command_info.id

    @property
    def flags(self):
        return self.__command_info.flags

    @property
    def size_in(self):
        return self.__command_info.size_in

    @property
    def size_out(self):
        return self.__command_info.size_out

    @property
    def name(self):
        return cxl_command_names.get(self.id)

def format_structure(structure):
    return ' '.join(["%X" % i for i in bytes(structure)])


class CXLMemDevice(object):
    dev_path_prefix = "/dev/cxl/"
    def __init__(self, dev_name: str):
        self._dev_name = dev_name
        self.cxl_bus_info = CXLBusInfo(self._dev_name)
        #
        self.open_device()
        ##
        self._mailbox_support_cmds = {}

    def __del__(self):
        if self._cxl_device is not None:
            self._cxl_device.close()
            self._cxl_device = None

    def open_device(self):
        self._cxl_device = LinIOCTLDevice(self.dev_path)

    def execute(self, op_code, cmd, check_retval=False, raise_on_error=False):
        if self._cxl_device:
            ret = self._cxl_device.execute(op_code, cmd)
            if ret < 0 and raise_on_error:
                raise OSError("execute command %s failed, return code %d" % (format_structure(cmd), ret))
            if op_code == cxl_mem_command_ioctl.CXL_MEM_SEND_COMMAND.value and check_retval and cmd.retval != 0 and raise_on_error:
                raise RuntimeError("execute command %s failed, return retval %d" % (format_structure(cmd), cmd.retval))
            return ret
        else:
            raise RuntimeError("Open device firstly")

    def _device_query_commands(self):
        cmd = self.cxl_mem_query_commands(0)
        if cmd.n_commands > 0:
            n_commands = cmd.n_commands
            cmd = self.cxl_mem_query_commands(n_commands)
            for i in cmd.commands:
                if i.id != 0:
                    self._mailbox_support_cmds[i.id] = cxl_command_info(i)

    @property
    def dev_path(self):
        return os.path.join(CXLMemDevice.dev_path_prefix, self._dev_name)

    def cxl_mem_query_commands(self, n_commands):
        cmd = get_cxl_mem_query_commands(n_commands)
        self._cxl_device.execute(cxl_mem_command_ioctl.CXL_MEM_QUERY_COMMANDS.value, cmd)
        return cmd

    def identify(self, data_buffer):
        cmd = cxl_send_command()
        cmd.id = 0x0001
        cmd.flags = 0x0001
        cmd.out.size = sizeof(data_buffer)
        cmd.out.payload = addressof(data_buffer)
        self._cxl_device.execute(cxl_mem_command_ioctl.CXL_MEM_SEND_COMMAND.value, cmd)
        return cmd
