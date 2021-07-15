#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Copy to devices using JN51xxProgrammer.exe."""

import os
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_JN51xx(HostTestPluginBase):
    """Plugin interface adaptor for the JN51xxProgrammer tool."""

    name = "HostTestPluginCopyMethod_JN51xx"
    type = "CopyMethod"
    capabilities = ["jn51xx"]
    required_parameters = ["image_path", "serial"]

    def __init__(self):
        """Initialise plugin."""
        HostTestPluginBase.__init__(self)

    def is_os_supported(self, os_name=None):
        """Plugin only supported on Windows."""
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
        self.JN51XX_PROGRAMMER = "JN51xxProgrammer.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy a firmware image to a JN51xx target using JN51xxProgrammer.exe.

        If the "capability" name is not 'jn51xx' this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the copy succeeded, otherwise False.
        """
        if not kwargs["image_path"]:
            self.print_plugin_error("Error: image path not specified")
            return False

        if not kwargs["serial"]:
            self.print_plugin_error("Error: serial port not set (not opened?)")
            return False

        result = False
        if self.check_parameters(capability, *args, **kwargs):
            if kwargs["image_path"] and kwargs["serial"]:
                image_path = os.path.normpath(kwargs["image_path"])
                serial_port = kwargs["serial"]
                if capability == "jn51xx":
                    # Example:
                    # JN51xxProgrammer.exe -s COM15 -f <file> -V0
                    cmd = [
                        self.JN51XX_PROGRAMMER,
                        "-s",
                        serial_port,
                        "-f",
                        image_path,
                        "-V0",
                    ]
                    result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_JN51xx()
