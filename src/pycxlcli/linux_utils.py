import os
import re

class CXLBusInfo(object):
    """
    Class to hold CXL bus information by retirving the information in
    /sys/bus/cxl/devices/<dev_name>/*
    """
    bus_info_prefix = "/sys/bus/cxl/devices/"
    def __init__(self, dev_name):
        self._dev_name = dev_name

    @property
    def bus_info_path(self):
        return os.path.join(CXLBusInfo.bus_info_prefix, self._dev_name)

    @property
    def dev_node(self):
        with open(os.path.join(self.bus_info_path, 'dev'), "r") as f:
            return f.read().strip()

    @property
    def firmware_version(self):
        with open(os.path.join(self.bus_info_path, 'firmware_version'), "r") as f:
            return f.read().strip()

    @property
    def label_storage_size(self):
        with open(os.path.join(self.bus_info_path, 'label_storage_size'), "r") as f:
            return int(f.read().strip())

    @property
    def numa_node(self):
        with open(os.path.join(self.bus_info_path, 'numa_node'), "r") as f:
            return f.read().strip()

    @property
    def payload_max(self):
        with open(os.path.join(self.bus_info_path, 'payload_max'), "r") as f:
            return int(f.read().strip())

    @property
    def serial(self):
        with open(os.path.join(self.bus_info_path, 'serial'), "r") as f:
            return f.read().strip()

    @property
    def security_state(self):
        with open(os.path.join(self.bus_info_path, 'security', 'state'), "r") as f:
            return f.read().strip()

    @property
    def ram_size(self):
        with open(os.path.join(self.bus_info_path,'ram', 'size'), "r") as f:
            return int(f.read().strip(), 16)

    @property
    def pmem_size(self):
        with open(os.path.join(self.bus_info_path,'pmem','size'), "r") as f:
            return int(f.read().strip(), 16)

    @property
    def uevent(self):
        result = {}
        file_path = os.path.join(self.bus_info_path, 'uevent')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                temp = f.read()
            for i in temp.split('\n'):
                i_list = i.split('=')
                if len(i_list) == 2:
                    result[i_list[0].strip()] = i_list[1].strip()
        return result


def get_cxl_mem_name():
    """
    Return a list of CXLBusInfo objects for all CXL devices"
    """
    cxl_dev_name = []
    for dev_name in os.listdir("/dev/cxl/"):
        if dev_name.startswith("mem"):
            cxl_dev_name.append(dev_name)
    return cxl_dev_name

def get_cxl_dev_bdf_by_name(dev_name:str, pci_class=(0x050210,)):
    """
    Return the BDF of the CXL device

    Args:
        dev_name (str): The name of the CXL device.
        pci_class (tuple): A tuple of PCI class codes to match. Default is (0x050210,).

    Returns:
        str: The BDF (Bus:Device.Function) of the CXL device if found, otherwise None.
    """
    # Iterate over all PCI devices in the system
    for bdf in os.listdir("/sys/bus/pci/devices/"):
        # Construct the path to the class file for the current PCI device
        class_file = os.path.join("/sys/bus/pci/devices/", bdf, "class")
        # Check if the class file exists
        if os.path.isfile(class_file):
            # Open the class file and read its contents
            with open(class_file, "r") as f:
                class_str = f.read().strip()
            # Convert the class string to an integer and check if it matches any of the specified PCI classes
            if int(class_str, 16) in pci_class:
                # Iterate over all files and directories under the current PCI device
                for dev in os.listdir(os.path.join("/sys/bus/pci/devices/", bdf)):
                    # Check if the device name matches the specified device name
                    if dev == dev_name:
                        # If a match is found, return the BDF of the PCI device
                        return bdf


class PCIBusInfo(object):
    """
    Class to hold PCI bus information by retirving the information in
    /sys/bus/pci/devices/<dev_name>/*
    """
    bus_info_prefix = "/sys/bus/pci/devices/"
    def __init__(self, bdf):
        self._bdf = bdf
        self.bus_info_path = os.path.join(PCIBusInfo.bus_info_prefix, self._bdf)

    def _get_value_form_file(self, file, base=10):
        file_path = os.path.join(self.bus_info_path, file)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return int(f.read().strip(), base)

    def _echo_to_file(self, file, value):
        ret = 255
        file_path = os.path.join(self.bus_info_path, file)
        if os.path.isfile(file_path):
            try:
                ret = os.system("echo %s > %s" % (value, file_path))
                # with open(file_path, "w") as f:
                #     f.write(value)
            except Exception as e:
                pass
        return ret

    @property
    def aer_dev_correctable(self):
        result = {}
        file_path = os.path.join(self.bus_info_path, 'aer_dev_correctable')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                temp = f.read()
            for i in temp.split('\n'):
                i_list = i.split()
                if len(i_list) == 2:
                    result[i_list[0].strip()] = int(i_list[1])
        return result

    @property
    def aer_dev_fatal(self):
        result = {}
        file_path = os.path.join(self.bus_info_path, 'aer_dev_fatal')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                temp = f.read()
            for i in temp.split('\n'):
                i_list = i.split()
                if len(i_list) == 2:
                    result[i_list[0].strip()] = int(i_list[1])
        return result

    @property
    def aer_dev_nonfatal(self):
        result = {}
        file_path = os.path.join(self.bus_info_path, 'aer_dev_nonfatal')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                temp = f.read()
            for i in temp.split('\n'):
                i_list = i.split()
                if len(i_list) == 2:
                    result[i_list[0].strip()] = int(i_list[1].strip())
        return result

    @property
    def ari_enabled(self):
        return self._get_value_form_file('ari_enabled')

    @property
    def broken_parity_status(self):
        return self._get_value_form_file('broken_parity_status')

    @property
    def class_code(self):
        return self._get_value_form_file('class', 16)

    @property
    def config(self):
        file_path = os.path.join(self.bus_info_path, 'config')
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()

    @property
    def consistent_dma_mask_bits(self):
        return self._get_value_form_file('consistent_dma_mask_bits')

    @property
    def max_link_speed(self):
        file_path = os.path.join(self.bus_info_path, 'max_link_speed')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                temp = f.read()
            g = re.match(r'\d+\.?\d*', temp)
            if g:
                return float(g.group())

    @property
    def max_link_width(self):
        return self._get_value_form_file('max_link_width')

    @property
    def current_link_speed(self):
        file_path = os.path.join(self.bus_info_path, 'current_link_speed')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                temp = f.read()
            g = re.match(r'\d+\.?\d*', temp)
            if g:
                return float(g.group())

    @property
    def current_link_width(self):
        return self._get_value_form_file('current_link_width')

    @property
    def d3cold_allowed(self):
        return self._get_value_form_file('d3cold_allowed')

    @property
    def vendor_id(self):
        return self._get_value_form_file('vendor', 16)

    @property
    def device_id(self):
        return self._get_value_form_file('device', 16)

    @property
    def subvendor_id(self):
        return self._get_value_form_file('subsystem_vendor', 16)

    @property
    def subdevice_id(self):
        return self._get_value_form_file('subsystem_device', 16)

    @property
    def dma_mask_bits(self):
        return self._get_value_form_file('dma_mask_bits')

    @property
    def enable(self):
        return self._get_value_form_file('enable')

    @property
    def irq(self):
        return self._get_value_form_file('irq')

    @property
    def local_cpulist(self):
        file_path = os.path.join(self.bus_info_path, 'local_cpulist')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read().strip()

    @property
    def local_cpus(self):
        file_path = os.path.join(self.bus_info_path, 'local_cpus')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read().strip()

    @property
    def numa_node(self):
        return self._get_value_form_file('numa_node')

    @property
    def revision(self):
        return self._get_value_form_file('revision', 16)

    @property
    def power_state(self):
        file_path = os.path.join(self.bus_info_path, 'power_state')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read().strip()

    def set_remove(self):
        self._echo_to_file('remove', '1')

    def set_rescan(self):
        self._echo_to_file('rescan', '1')

    @property
    def reset_method(self):
        file_path = os.path.join(self.bus_info_path, 'reset_method')
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read().strip()

    def set_reset(self):
        self._echo_to_file('reset', '1')

    def get_mem_bus_info(self):
        result = []
        for f in os.listdir(self.bus_info_path):
            if re.fullmatch(r'mem\d+', f):
                result.append(CXLBusInfo(f))
        return result

    def decode_pci_config(self):
        # TODO
        pass

    def decode_pci_bar(self):
        # TODO
        pass
