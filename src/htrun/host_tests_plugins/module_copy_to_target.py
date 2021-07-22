#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Copy to DAPLink enabled devices using file operations."""

import os
from shutil import copy
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_Target(HostTestPluginBase):
    """Generic flashing method for DAPLink enabled platforms using file copy."""

    def __init__(self):
        """Initialise the plugin."""
        HostTestPluginBase.__init__(self)

    def generic_target_copy(self, image_path, destination_disk):
        """Target copy method for "Mbed enabled" devices.

        Args:
            image_path: Path to binary file to be flashed.
            destination_disk: Path to destination (target mount point).

        Returns:
            True if copy (flashing) was successful, otherwise False.
        """
        result = True
        if not destination_disk.endswith("/") and not destination_disk.endswith("\\"):
            destination_disk += "/"
        try:
            copy(image_path, destination_disk)
        except Exception as e:
            self.print_plugin_error(
                "shutil.copy('%s', '%s')" % (image_path, destination_disk)
            )
            self.print_plugin_error("Error: %s" % str(e))
            result = False
        return result

    name = "HostTestPluginCopyMethod_Target"
    type = "CopyMethod"
    stable = True
    capabilities = ["shutil", "default"]
    required_parameters = ["image_path", "destination_disk"]

    def setup(self, *args, **kwargs):
        """Configure plugin."""
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy a firmware image to a DAPLink compatible device's filesystem.

        The "capability" name must be "shutil" or this function will just fail.

        Returns:
            True if copy was successful, otherwise False.
        """
        if not kwargs["image_path"]:
            self.print_plugin_error("Error: image path not specified")
            return False

        if not kwargs["destination_disk"]:
            self.print_plugin_error("Error: destination disk not specified")
            return False

        pooling_timeout = kwargs.get("polling_timeout", 60)

        result = False
        if self.check_parameters(capability, *args, **kwargs):
            # Capability 'default' is a dummy capability
            if kwargs["image_path"] and kwargs["destination_disk"]:
                if capability == "shutil":
                    image_path = os.path.normpath(kwargs["image_path"])
                    destination_disk = os.path.normpath(kwargs["destination_disk"])
                    # Wait for mount point to be ready
                    # if mount point changed according to target_id use new mount point
                    # available in result (_, destination_disk) of
                    # check_mount_point_ready
                    mount_res, destination_disk = self.check_mount_point_ready(
                        destination_disk,
                        target_id=self.target_id,
                        timeout=pooling_timeout,
                    )  # Blocking
                    if mount_res:
                        result = self.generic_target_copy(image_path, destination_disk)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_Target()
