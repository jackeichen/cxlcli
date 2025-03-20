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


class CXLMemDevice(object):
    dev_path_prefix = "/dev/cxl/"
    def __init__(self, dev_name: str):
        self._dev_name = dev_name
        self.cxl_bus_info = CXLBusInfo(self._dev_name)
        #
        self.open_device()

    def __del__(self):
        if self._cxl_device is not None:
            self._cxl_device.close()
            self._cxl_device = None

    def open_device(self):
        self._cxl_device = LinIOCTLDevice(self.dev_path)

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
