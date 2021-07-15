#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Implements reset method for the ARM_MPS2 platform."""

import os
import time

from .host_test_plugins import HostTestPluginBase

# Note: This plugin is not fully functional, needs improvements


class HostTestPluginResetMethod_MPS2(HostTestPluginBase):
    """Plugin used to reset ARM_MPS2 platform.

    Supports reboot.txt startup from standby state, reboots when in run mode.
    """

    # Plugin interface
    name = "HostTestPluginResetMethod_MPS2"
    type = "ResetMethod"
    capabilities = ["reboot.txt"]
    required_parameters = ["disk"]

    def __init__(self):
        """Initialise the plugin."""
        HostTestPluginBase.__init__(self)

    def touch_file(self, path):
        """Touch file and set timestamp to items."""
        with open(path, "a"):
            os.utime(path, None)

    def setup(self, *args, **kwargs):
        """Prepare / configure plugin to work.

        This method can receive plugin specific parameters by kwargs and
        ignore other parameters which may affect other plugins.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """Reboot a device.

        The "capability" name must be 'reboot.txt' or this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the reset succeeded, otherwise False.
        """
        result = False
        if not kwargs["disk"]:
            self.print_plugin_error("Error: disk not specified")
            return False

        destination_disk = kwargs.get("disk", None)

        # This optional parameter can be used if TargetID is provided (-t switch)
        target_id = kwargs.get("target_id", None)
        pooling_timeout = kwargs.get("polling_timeout", 60)
        if self.check_parameters(capability, *args, **kwargs) is True:

            if capability == "reboot.txt":
                reboot_file_path = os.path.join(destination_disk, capability)
                reboot_fh = open(reboot_file_path, "w")
                reboot_fh.close()
                # Make sure the file is written to the board before continuing
                if os.name == "posix":
                    self.run_command("sync -f %s" % reboot_file_path, shell=True)
                time.sleep(3)  # sufficient delay for device to boot up
                result, destination_disk = self.check_mount_point_ready(
                    destination_disk, target_id=target_id, timeout=pooling_timeout
                )
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginResetMethod_MPS2()
