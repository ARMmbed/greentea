#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Reset ublox devices using the jlink.exe tool."""

from .host_test_plugins import HostTestPluginBase


class HostTestPluginResetMethod_ublox(HostTestPluginBase):
    """Plugin interface adapter for jlink.exe."""

    name = "HostTestPluginResetMethod_ublox"
    type = "ResetMethod"
    capabilities = ["ublox"]
    required_parameters = []
    stable = False

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

        Note: you need to have jlink.exe on your system path!
        """
        self.JLINK = "jlink.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """Reset a ublox device using jlink.exe.

        The "capability" name must be "ublox" or this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the reset was successful, otherwise False.
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            if capability == "ublox":
                # Example:
                # JLINK.exe --CommanderScript aCommandFile
                cmd = [self.JLINK, "-CommanderScript", r"reset.jlink"]
                result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginResetMethod_ublox()
