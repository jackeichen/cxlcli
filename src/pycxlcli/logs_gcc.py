from ctypes import *

class cxlmi_supported_log_entry(Structure):
    _fields_ = [
        ("uuid", c_uint8 * 0x10),
        ("log_size", c_uint32),
    ]
    _pack_ = 1


LogUUIDTable = {
    "0da9c0b5bf414b788f7996b1623b3f17": "Command Effects Log (CEL)",
    "5e1819d911a9400c811fd60719403d86": "Vendor Debug Log",
    "b3fab4cf01b64332943e5e9962f23567": "Component State Dump Log",
    "f1720d60a7a94306a00311948f9e077c": "DDR5 Error Check Scrub (ECS) Log",
    "e6dfa32cd13e4a5c8ca899bebbf731a4": "Media Test Capability Log",
    "2c2555228ce411ecb9090242ac120002": "Media Test Results Short Log",
    "c1fe0b3e7a00448ea24ea6aabbfe587a": "Media Test Results Long Log",
}


class GetSupportedLogsPayload(Structure):
    _fields_ = [
        ("num_supported_log_entries", c_uint16),
        ("reserved", c_uint8 * 6),
        ("entries", cxlmi_supported_log_entry * 1), 
    ]
    _pack_ = 1


def get_supported_logs_payload(log_entry_num):
    class GetSupportedLogsPayload(Structure):
        _fields_ = [
            ("num_supported_log_entries", c_uint16),
            ("reserved", c_uint8 * 6),
            ("entries", cxlmi_supported_log_entry * log_entry_num), 
        ]
        _pack_ = 1
    return GetSupportedLogsPayload()
