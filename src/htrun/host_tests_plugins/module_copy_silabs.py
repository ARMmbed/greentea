#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_Silabs(HostTestPluginBase):

    # Plugin interface
    name = "HostTestPluginCopyMethod_Silabs"
    type = "CopyMethod"
    capabilities = ["eACommander", "eACommander-usb"]
    required_parameters = ["image_path", "destination_disk"]
    stable = True

    def __init__(self):
        """ctor"""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin, this function should be called before plugin execute() method is used."""
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
    """Returns plugin available in this module"""
    return HostTestPluginCopyMethod_Silabs()
