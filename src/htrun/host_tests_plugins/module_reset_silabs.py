#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Implements a reset method using the eACommander tool."""

from .host_test_plugins import HostTestPluginBase


class HostTestPluginResetMethod_SiLabs(HostTestPluginBase):
    """Plugin interface adaptor for the eACommander tool."""

    # Plugin interface
    name = "HostTestPluginResetMethod_SiLabs"
    type = "ResetMethod"
    capabilities = ["eACommander", "eACommander-usb"]
    required_parameters = ["disk"]
    stable = True

    def __init__(self):
        """Initialise the plugin."""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        # Note you need to have eACommander.exe on your system path!
        self.EACOMMANDER_CMD = "eACommander.exe"
        return True

    def execute(self, capability, *args, **kwargs):
        """Reset a device using eACommander.exe.

        "capability" is used to select the reset method used by eACommander,
        either serial or USB.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the reset succeeded, otherwise False.
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            disk = kwargs["disk"].rstrip("/\\")

            if capability == "eACommander":
                # For this copy method 'disk' will be 'serialno' for eACommander command
                # line parameters.
                # Note: Commands are executed in the order they are specified on the
                # command line
                cmd = [
                    self.EACOMMANDER_CMD,
                    "--serialno",
                    disk,
                    "--resettype",
                    "2",
                    "--reset",
                ]
                result = self.run_command(cmd)
            elif capability == "eACommander-usb":
                # For this copy method 'disk' will be 'usb address' for eACommander
                # command line parameters
                # Note: Commands are executed in the order they are specified on the
                # command line
                cmd = [
                    self.EACOMMANDER_CMD,
                    "--usb",
                    disk,
                    "--resettype",
                    "2",
                    "--reset",
                ]
                result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginResetMethod_SiLabs()
