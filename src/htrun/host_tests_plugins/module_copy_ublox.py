#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Copy images to ublox devices using FlashErase.exe."""

import os
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_ublox(HostTestPluginBase):
    """Plugin interface adaptor for the FlashErase.exe tool."""

    name = "HostTestPluginCopyMethod_ublox"
    type = "CopyMethod"
    capabilities = ["ublox"]
    required_parameters = ["image_path"]

    def is_os_supported(self, os_name=None):
        """Plugin only works on Windows.

        Args:
            os_name: Name of the current OS.
        """
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
        self.FLASH_ERASE = "FlashErase.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy an image to a ublox device using FlashErase.exe.

        The "capability" name must be "ublox" or this method will just fail.

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
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_ublox()
