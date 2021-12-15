#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Implements a plugin to flash ST devices using STM32CubeProgrammer.

https://www.st.com/en/development-tools/stm32cubeprog.html
"""

import os
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_STProgrammer(HostTestPluginBase):
    """Plugin interface adaptor for STM32CubeProgrammer."""

    # Plugin interface
    name = "HostTestPluginCopyMethod_STProgrammer"
    type = "CopyMethod"
    capabilities = ["stprog"]
    required_parameters = ["image_path"]

    def __init__(self):
        """Initialise the object."""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        self.CLI = "STM32_Programmer_CLI"
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy a firmware image to a device using STM32CubeProgrammer.

        If the "capability" name is not 'stprog' this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the copy succeeded, otherwise False.
        """
        from shutil import which

        if which(self.CLI) is None:
            print("%s is not part of environment PATH" % self.CLI)
            return False

        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            image_path = os.path.normpath(kwargs["image_path"])
            if capability == "stprog":
                cmd = [
                    self.CLI,
                    "-c",
                    "port=SWD",
                    "mode=UR",
                    "-w",
                    image_path,
                    "0x08000000",
                    "-v",
                    "-rst",
                ]
                result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_STProgrammer()
