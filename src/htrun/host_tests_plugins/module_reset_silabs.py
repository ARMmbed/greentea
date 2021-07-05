#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from .host_test_plugins import HostTestPluginBase


class HostTestPluginResetMethod_SiLabs(HostTestPluginBase):

    # Plugin interface
    name = "HostTestPluginResetMethod_SiLabs"
    type = "ResetMethod"
    capabilities = ["eACommander", "eACommander-usb"]
    required_parameters = ["disk"]
    stable = True

    def __init__(self):
        """ctor"""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin, this function should be called before plugin execute() method is used."""
        # Note you need to have eACommander.exe on your system path!
        self.EACOMMANDER_CMD = "eACommander.exe"
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
            disk = kwargs["disk"].rstrip("/\\")

            if capability == "eACommander":
                # For this copy method 'disk' will be 'serialno' for eACommander command line parameters
                # Note: Commands are executed in the order they are specified on the command line
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
                # For this copy method 'disk' will be 'usb address' for eACommander command line parameters
                # Note: Commands are executed in the order they are specified on the command line
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
    """Returns plugin available in this module"""
    return HostTestPluginResetMethod_SiLabs()
