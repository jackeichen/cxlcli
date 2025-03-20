import os
import sys
import argparse
from pycxlcli.cxl import CXLMemDevice
from pycxlcli.linux_utils import (
    get_cxl_mem_name,
    get_cxl_dev_bdf_by_name,
    CXLBusInfo,
    PCIBusInfo,
    )
from pycxlcli.linux_cxl_ioctl import cxl_command_names
from pycxlcli.identify_memory_device import cxlmi_cmd_memdev_identify_payload
from pycxlcli.__version__ import version

return_code_table = {
    0: "success",
    1: "NOT_SUPPORTED",
    2: "INVALID_ARGUMENT",
    3: "device_not_found",
    4: "",
    5: "",
    255: "unknown error"
}

def get_human_size(value: int):
    units = ['KB', 'MB', 'GB', 'TB', 'PB']
    target_unit = "B"
    target_value = value
    for unit in units:
        value = value / 1024
        if value < 1:
            break
        else:
            target_unit = unit
            target_value = value
    return "%d %s" % (target_value, target_unit)

def list_cxl_devices(args):
    """
    List all CXL devices on the system"
    """
    print_format = "%-16s %-15s %-20s %s"
    if args.type == "cxl_memdev":
        print_format = "%-16s %-15s %-20s %s"
        print (print_format % ("Node", "Type", "Size(pmem/mem)", "FW Ver"))
        print (print_format % ("-"*16, "-"*15, "-"*20, "-"*20))
        for cxl_dev_name in get_cxl_mem_name():
            cxl_bus_info = CXLBusInfo(cxl_dev_name)
            print (print_format % ("/dev/cxl/%s" % cxl_dev_name, 
                                cxl_bus_info.uevent.get("DEVTYPE") if cxl_bus_info.uevent.get("DEVTYPE") else "unknown", 
                                " %-7s /  %-7s" % (get_human_size(cxl_bus_info.pmem_size), get_human_size(cxl_bus_info.ram_size)), 
                                cxl_bus_info.firmware_version))
    else:
        print ("Only support cxl_memdev type for now")
        return 3
    return 0

def query_commands(args):
    if not os.path.exists(args.device):
        print ("Device %s not exist" % args.device)
        return 3
    cxl_device = CXLMemDevice(args.device)
    n_commands = args.number
    if args.number == 0:
        cmd = cxl_device.cxl_mem_query_commands(0)
        n_commands = cmd.n_commands
    print ("Command support:", n_commands)
    print ("")
    cmd = cxl_device.cxl_mem_query_commands(n_commands)
    print_format = "%-3s %-30s flags(%-12s|%-9s)   %-12s %s"
    print (print_format % ("ID", "Name", "USER_ENABLED", "EXCLUSIVE", "size_in", "size_out"))
    for i in cmd.commands:
        if i.id != 0:
            print (print_format % (i.id,
                                cxl_command_names[i.id],
                                i.flags & 0x01,
                                i.flags & 0x02,
                                "%#x" % i.size_in,
                                "%#x" % i.size_out
                                )
                )

def identify(args):
    if not os.path.exists(args.device):
        print ("Device %s not exist" % args.device)
        return 3
    cxl_device = CXLMemDevice(args.device)
    data_buffer = cxlmi_cmd_memdev_identify_payload()
    cmd = cxl_device.identify(data_buffer)
    if cmd.retval != 0:
        print ("Failed to identify device %s, return code %d" % (args.device, cmd.retval))
        return (cmd.retval+3)
    print ("FW Revision: %s" % data_buffer.fw_revision.decode())
    print ("Total Capacity: %s" % data_buffer.total_capacity)
    print ("Volatile Capacity: %s" % data_buffer.volatile_capacity)
    print ("Persistent Capacity: %s" % data_buffer.persistent_capacity)
    print ("Partition Align: %s" % data_buffer.partition_align)
    print ("Info Event Log Size: %s" % data_buffer.info_event_log_size)
    print ("Warning Event Log Size: %s" % data_buffer.warning_event_log_size)
    print ("Failure Event Log Size: %s" % data_buffer.failure_event_log_size)
    print ("Fatal Event Log Size: %s" % data_buffer.fatal_event_log_size)
    print ("LSA Size: %s" % data_buffer.lsa_size)
    print ("Poison List Max MER: %s" % ','.join(["%#x" % i for i in data_buffer.poison_list_max_mer]))
    print ("Inject Poison Limit: %s" % data_buffer.inject_poison_limit)
    print ("Poison Caps: %s" % data_buffer.poison_caps)
    print ("QoS Telemetry Caps: %#x" % data_buffer.qos_telemetry_caps)
    print ("DC Event Log Size: %s" % data_buffer.dc_event_log_size)
    return 0

    

def get_ver(args):
    print ("pycxl version: %s" % version)
    return 0

def CXLCli():
    # create the top-level parser
    parser = argparse.ArgumentParser(description='CXL CLI to get CXL device information')
    subparsers = parser.add_subparsers(help='The following are all implemented sub-commands:')
    def get_help(args):
        parser.print_help()
        return 0
    # create the parser for the "list" command
    parser_list = subparsers.add_parser('list', help='list all CXL devices on the system')
    parser_list.set_defaults(func=list_cxl_devices)
    parser_list.add_argument("--type", default="cxl_memdev", help="Show devices of specified type")
    parser_list.add_argument("-o", "--output-format", dest="format", help="Output format")
    # create the parser for the "query" command
    parser_query = subparsers.add_parser('query-command', help='query commands for CXL devices')
    parser_query.set_defaults(func=query_commands)
    parser_query.add_argument('device', help='The device path to send command')
    parser_query.add_argument('-n', '--number', type=int, default=0, help='number of support commands should return')
    # create the parser for the "identify" command
    parser_query = subparsers.add_parser('identify', help='identify commands for CXL devices')
    parser_query.set_defaults(func=identify)
    parser_query.add_argument('device', help='The device path to send command')
    # create the parser for the "version" command
    parser_version = subparsers.add_parser('version', help='Shows the program version')
    parser_version.set_defaults(func=get_ver)
    # create the parser for the "help" command
    parser_help = subparsers.add_parser('help', help='Display this help')
    parser_help.set_defaults(func=get_help)
    ##
    args = parser.parse_args()
    if len(sys.argv) > 1:
        sys.exit(args.func(args))
    else:
        sys.exit(get_help(args))
