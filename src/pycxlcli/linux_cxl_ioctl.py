from enum import Enum

class cxl_mem_command_ioctl(Enum):
    CXL_MEM_QUERY_COMMANDS = 0x8008ce01
    CXL_MEM_SEND_COMMAND = 0xc030ce02  

cxl_command_names = ("Invalid Command",
                     "Identify Command",
                     "Raw device command",
                     "Get Supported Logs",
                     "Get FW Info",
                     "Get Partition Information",
                     "Get Label Storage Area",
                     "Get Health Info",
                     "Get Log",
                     "Set Partition Information",
                     "Set Label Storage Area",
                     "Get Alert Configuration",
                     "Set Alert Configuration",
                     "Get Shutdown State",
                     "Set Shutdown State",
                     "Get Poison List",
                     "Inject Poison",
                     "Clear Poison",
                     "Get Scan Media Capabilities",
                     "Scan Media",
                     "Get Scan Media Results",
                     "Get timestamp",
                     "Set timestamp",
                     "Get event log",
                     "Clear event log",
                     "Transfer FW Package",
                     "Activate FW",
                     "Sanitize Memdev",
                     "Get SLD QoS Control",
                     "Set SLD QoS Control",
                     "Get SLD QoS Status",
                     "invalid / last command",
                     )
