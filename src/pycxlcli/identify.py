from ctypes import *

OPCode = 0x0001

class cxlmi_cmd_identify_payload(Structure):
    _fields_ = [
        ("pcie_vendor_id", c_uint16),
        ("pcie_device_id", c_uint16),
        ("pcie_subsystem_vendor_id", c_uint16),
        ("pcie_subsystem_device_id", c_uint16),
        ("serial_number", c_uint8*8),
        ("max_supported_message_size", c_uint8),
        ("component_type", c_uint8),
    ]
    _pack_ = 1
