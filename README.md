pycxlcli
========
Communicate with CXL device using Linux's inbox device driver.


License
=======
pydiskcmd is distributed under MIT.
Please see the LICENSE file for the full license text.


Getting the sources
===================
The module(source) is hosted at https://github.com/jackeichen/cxlcli

You can use git to checkout the latest version of the source code using:

    $ git clone git@github.com:jackeichen/pydiskcmd.git

It is also available as a downloadable zip archive from:

   https://github.com/jackeichen/cxlcli/archive/master.zip


Building and installing
=======================

Sofware Requirements:

    * python3(Required)

Python3 Module Requirements:

    * Cython(Required)

Online build and install from the repository:

    $ git clone git@github.com:jackeichen/cxlcli.git
    $ pip install .


Usage
=====

```
# pycxl -h
usage: pycxl [-h] {list,query-command,version,help} ...

CXL CLI to get CXL device information

positional arguments:
  {list,query-command,identify,version,help}
                        The following are all implemented sub-commands:
    list                list all CXL devices on the system
    query-command       query commands for CXL devices
    identify            identify commands for CXL devices
    version             Shows the program version
    help                Display this help

optional arguments:
  -h, --help            show this help message and exit
```