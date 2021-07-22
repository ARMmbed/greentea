#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Implements a plugin to flash ST devices using ST-LINK-CLI."""

import os
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_Stlink(HostTestPluginBase):
    """Plugin interface adaptor for the ST-LINK-CLI."""

    # Plugin interface
    name = "HostTestPluginCopyMethod_Stlink"
    type = "CopyMethod"
    capabilities = ["stlink"]
    required_parameters = ["image_path"]

    def __init__(self):
        """Initialise the object."""
        HostTestPluginBase.__init__(self)

    def is_os_supported(self, os_name=None):
        """Check if the OS is supported."""
        # If no OS name provided use host OS name
        if not os_name:
            os_name = self.host_os_support()

        # This plugin only works on Windows
        if os_name and os_name.startswith("Windows"):
            return True
        return False

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        self.ST_LINK_CLI = "ST-LINK_CLI.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy a firmware image to a deice using the ST-LINK-CLI.

        If the "capability" name is not 'stlink' this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the copy succeeded, otherwise False.
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            image_path = os.path.normpath(kwargs["image_path"])
            if capability == "stlink":
                # Example:
                # ST-LINK_CLI.exe -p \
                # "C:\Work\mbed\build\test\DISCO_F429ZI\GCC_ARM\MBED_A1\basic.bin"
                cmd = [self.ST_LINK_CLI, "-p", image_path, "0x08000000", "-V"]
                result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_Stlink()
