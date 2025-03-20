from ctypes import *
##
# struct cxl_command_info {
#     __u32 id;
#     __u32 flags;
# #define CXL_MEM_COMMAND_FLAG_MASK               GENMASK(1, 0);
# #define CXL_MEM_COMMAND_FLAG_ENABLED            BIT(0);
# #define CXL_MEM_COMMAND_FLAG_EXCLUSIVE          BIT(1);
#     __u32 size_in;
#     __u32 size_out;
# };

class cxl_command_info(Structure):
    """
    Command information returned from a query.

    id: ID number for the command.

    flags: Flags that specify command behavior.

    CXL_MEM_COMMAND_FLAG_USER_ENABLED: The given command id is supported by the driver 
    and is supported by a related opcode on the device.

    CXL_MEM_COMMAND_FLAG_EXCLUSIVE: Requests with the given command id will terminate 
    with EBUSY as the kernel actively owns management of the given resource. For example, 
    the label-storage-area can not be written while the kernel is actively managing that space.

    size_in: Expected input size, or ~0 if variable length.

    size_out: Expected output size, or ~0 if variable length.

    Description:
    Represents a single command that is supported by both the driver and the hardware. 
    This is returned as part of an array from the query ioctl. The following would be a command that takes a 
    variable length input and returns 0 bytes of output.
    """
    _fields_ = [
        ("id", c_uint32),        # ID number for the command.
        ("flags", c_uint32),     #
        ("size_in", c_uint32), 
        ("size_out", c_uint32),
    ]
    _pack_ = 1


# struct cxl_mem_query_commands {
#     __u32 n_commands;
#     __u32 rsvd;
#     struct cxl_command_info __user commands[];
# };
def get_cxl_mem_query_commands(n_commands):
    class cxl_mem_query_commands(Structure):
        """
        n_commands:
        Number of commands in the commands array."
        """
        _fields_ = [
            ("n_commands", c_uint32),
            ("rsvd", c_uint32),
            ("commands", cxl_command_info * n_commands),
        ]
        _pack_ = 1
    command = cxl_mem_query_commands()
    command.n_commands = n_commands
    return command


# struct cxl_send_command {
#     __u32 id;
#     __u32 flags;
#     union {
#         struct {
#             __u16 opcode;
#             __u16 rsvd;
#         } raw;
#         __u32 rsvd;
#     };
#     __u32 retval;
#     struct {
#         __u32 size;
#         __u32 rsvd;
#         __u64 payload;
#     } in;
#     struct {
#         __u32 size;
#         __u32 rsvd;
#         __u64 payload;
#     } out;
# };
class cxl_send_command_union_raw(Structure):
    _fields_ = [
        ("opcode", c_uint16),
        ("rsvd", c_uint16),
    ]
    _pack_ = 1


class cxl_send_command_union(Union):
    _fields_ = [
        ("raw", cxl_send_command_union_raw),
        ("rsvd", c_uint32),
    ]
    _pack_ = 1


class cxl_send_command_in(Structure):
    """
    size: Size of the payload in bytes.

    rsvd: Reserved.

    payload: Pointer to the payload data.
    """
    _fields_ = [
        ("size", c_uint32),
        ("rsvd", c_uint32),
        ("payload", c_uint64),
    ]
    _pack_ = 1


class cxl_send_command_out(Structure):
    """
    size: Size of the payload out bytes.

    rsvd: Reserved.

    payload: Pointer to the payload data.
    """
    _fields_ = [
        ("size", c_uint32),
        ("rsvd", c_uint32),
        ("payload", c_uint64),
    ]
    _pack_ = 1


class cxl_send_command(Structure):
    """
    Send a command to a memory device.

    id: The command to send to the memory device. This must be one of the commands returned 
    by the query command.

    flags: Flags for the command (input).

    {unnamed_union}
    raw: Special fields for raw commands

    raw.opcode: Opcode passed to hardware when using the RAW command.

    raw.rsvd: Must be zero.

    rsvd: Must be zero.

    retval: Return value from the memory device (output).

    in: Parameters associated with input payload.

    in.size: Size of the payload to provide to the device (input).

    in.rsvd: Must be zero.

    in.payload: Pointer to memory for payload input, payload is little endian.

    out: Parameters associated with output payload.

    out.size: Size of the payload received from the device (input/output). This field 
    is filled in by userspace to let the driver know how much space was allocated for 
    output. It is populated by the driver to let userspace know how large the output 
    payload actually was.

    out.rsvd: Must be zero.

    out.payload: Pointer to memory for payload output, payload is little endian.

    Description:
    Mechanism for userspace to send a command to the hardware for processing. The driver 
    will do basic validation on the command sizes. In some cases even the payload may be 
    introspected. Userspace is required to allocate large enough buffers for size_out 
    which can be variable length in certain situations.
    """
    _fields_ = [
        ("id", c_uint32),        # ID number for the command.
        ("flags", c_uint32),     #
        ("union", cxl_send_command_union),  
        ("retval", c_uint32),    #
        ("in", cxl_send_command_in), 
        ("out", cxl_send_command_out),       #  
    ]
    _pack_ = 1
