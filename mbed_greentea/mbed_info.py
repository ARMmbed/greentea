"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

import os
import sys
import json
import platform
import pkg_resources  # part of setuptools


packages = ['mbed-greentea', 'mbed-host-tests', 'mbed-ls', 'pyserial']

def mbed_os_info():
    """! Returns information about host OS
    @return Returns tuple with information about OS and host platform
    """
    result = (os.name,
              platform.system(),
              platform.release(),
              platform.version(),
              sys.platform)
    return result


def mbed_get_global_info():
    info_dict = dict()

    info_dict['os'] = dict()
    info_dict['mbed-tools'] = dict()
    info_dict['python'] = dict()

    info_dict['os']['os_info'] = mbed_os_info()
    info_dict['os']['uname'] = platform.uname()

    info_dict['os']['details'] = dict()
    info_dict['os']['details']['os_mac'] = platform.mac_ver()
    info_dict['os']['details']['os_linux'] = platform.linux_distribution()
    info_dict['os']['details']['os_win'] = platform.win32_ver()

    info_dict['python']['version_info'] = str(sys.version_info)
    info_dict['python']['version'] =  platform.python_version()

    info_dict['mbed-tools']['packages'] = dict()
    info_dict['mbed-tools']['details'] = dict()

    for pkg in packages:
        version = pkg_resources.require(pkg)[0].version
        info_dict['mbed-tools']['packages'][pkg] = version
        info_dict['mbed-tools']['details'][pkg] = [str(x) for x in pkg_resources.require(pkg)]

    #print json.dumps(info_dict, indent=4)
    return json.dumps(info_dict, indent=4)
