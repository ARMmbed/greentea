#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_ublox(HostTestPluginBase):

    # Plugin interface
    name = "HostTestPluginCopyMethod_ublox"
    type = "CopyMethod"
    capabilities = ["ublox"]
    required_parameters = ["image_path"]

    def is_os_supported(self, os_name=None):
        """! In this implementation this plugin only is supporeted under Windows machines"""
        # If no OS name provided use host OS name
        if not os_name:
            os_name = self.host_os_support()

        # This plugin only works on Windows
        if os_name and os_name.startswith("Windows"):
            return True
        return False

    def setup(self, *args, **kwargs):
        """! Configure plugin, this function should be called before plugin execute() method is used."""
        self.FLASH_ERASE = "FlashErase.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """! Executes capability by name

        @param capability Capability name
        @param args Additional arguments
        @param kwargs Additional arguments

        @details Each capability e.g. may directly just call some command line program or execute building pythonic function

        @return Capability call return value
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            image_path = os.path.normpath(kwargs["image_path"])
            if capability == "ublox":
                # Example:
                # FLASH_ERASE -c 2 -s 0xD7000 -l 0x20000 -f "binary_file.bin"
                cmd = [
                    self.FLASH_ERASE,
                    "-c",
                    "A",
                    "-s",
                    "0xD7000",
                    "-l",
                    "0x20000",
                    "-f",
                    image_path,
                ]
                result = self.run_command(cmd)
        return result


def load_plugin():
    """Returns plugin available in this module"""
    return HostTestPluginCopyMethod_ublox()
