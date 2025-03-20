from ctypes import *

OPCode = 0x0400

class cxlmi_cmd_memdev_identify_payload(Structure):
    _fields_ = [
        ("fw_revision", c_char * 0x10),
        ("total_capacity", c_uint64),
        ("volatile_capacity", c_uint64),
        ("persistent_capacity", c_uint64),
        ("partition_align", c_uint64),
        ("info_event_log_size", c_uint16),
        ("warning_event_log_size", c_uint16),
        ("failure_event_log_size", c_uint16),
        ("fatal_event_log_size", c_uint16),
        ("lsa_size", c_uint32),
        ("poison_list_max_mer", c_uint8 * 3),
        ("inject_poison_limit", c_uint16),
        ("poison_caps", c_uint8),
        ("qos_telemetry_caps", c_uint8),
        ("dc_event_log_size", c_uint16),  
    ]
    _pack_ = 1
