#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Reset method using the JN51xxProgrammer.exe."""

from .host_test_plugins import HostTestPluginBase


class HostTestPluginResetMethod_JN51xx(HostTestPluginBase):
    """Plugin interface adaptor for JN51xxProgrammer.exe."""

    name = "HostTestPluginResetMethod_JN51xx"
    type = "ResetMethod"
    capabilities = ["jn51xx"]
    required_parameters = ["serial"]
    stable = False

    def __init__(self):
        """Initialise the plugin."""
        HostTestPluginBase.__init__(self)

    def is_os_supported(self, os_name=None):
        """Plugin is only supported on Windows."""
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
        # Note you need to have eACommander.exe on your system path!
        self.JN51XX_PROGRAMMER = "JN51xxProgrammer.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """Reset a device using the JN51xxProgrammer.exe.

        If the "capability" name is not 'jn51xx' this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the reset succeeded, otherwise False.
        """
        if not kwargs["serial"]:
            self.print_plugin_error("Error: serial port not set (not opened?)")
            return False

        result = False
        if self.check_parameters(capability, *args, **kwargs):
            if kwargs["serial"]:
                if capability == "jn51xx":
                    # Example: The device should be automatically reset before the
                    # programmer disconnects.  Issuing a command with no file to program
                    # or read will put the device into programming mode and then reset
                    # it. E.g.  $ JN51xxProgrammer.exe -s COM5 -V0 COM5: Detected JN5179
                    # with MAC address 00:15:8D:00:01:24:E0:37
                    serial_port = kwargs["serial"]
                    cmd = [self.JN51XX_PROGRAMMER, "-s", serial_port, "-V0"]
                    result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginResetMethod_JN51xx()
