#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Copy firmware images to silab devices using the eACommander.exe tool."""

import os
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_Silabs(HostTestPluginBase):
    """Plugin interface adapter for eACommander.exe."""

    name = "HostTestPluginCopyMethod_Silabs"
    type = "CopyMethod"
    capabilities = ["eACommander", "eACommander-usb"]
    required_parameters = ["image_path", "destination_disk"]
    stable = True

    def __init__(self):
        """Initialise plugin."""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        self.EACOMMANDER_CMD = "eACommander.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy a firmware image to a silab device using eACommander.exe.

        The "capability" name must be eACommander or this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
         True if the copy was successful, otherwise False.
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            image_path = os.path.normpath(kwargs["image_path"])
            destination_disk = os.path.normpath(kwargs["destination_disk"])
            if capability == "eACommander":
                cmd = [
                    self.EACOMMANDER_CMD,
                    "--serialno",
                    destination_disk,
                    "--flash",
                    image_path,
                    "--resettype",
                    "2",
                    "--reset",
                ]
                result = self.run_command(cmd)
            elif capability == "eACommander-usb":
                cmd = [
                    self.EACOMMANDER_CMD,
                    "--usb",
                    destination_disk,
                    "--flash",
                    image_path,
                ]
                result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_Silabs()
