#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""MPS2 specific flashing / binary setup functions."""

import os
from shutil import copy
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_MPS2(HostTestPluginBase):
    """Plugin interface adapter for a shell 'copy' command."""

    name = "HostTestPluginCopyMethod_MPS2"
    type = "CopyMethod"
    stable = True
    capabilities = ["mps2"]
    required_parameters = ["image_path", "destination_disk"]

    def __init__(self):
        """Initialise plugin."""
        HostTestPluginBase.__init__(self)

    def mps2_copy(self, image_path, destination_disk):
        """mps2 copy method for "mbed enabled" devices.

        Copies the file to the MPS2, using shutil.copy. Prepends the file
        extension with 'mbed'.

        Args:
            image_path: Path to file to be copied.
            destination_disk: Path to destination (mbed mount point).

        Returns;
            True if copy (flashing) was successful, otherwise False.
        """
        result = True
        # Keep the same extension in the test spec and on the MPS2
        _, extension = os.path.splitext(image_path)
        destination_path = os.path.join(destination_disk, "mbed" + extension)
        try:
            copy(image_path, destination_path)
            # sync command on mac ignores command line arguments.
            if os.name == "posix":
                result = self.run_command("sync -f %s" % destination_path, shell=True)
        except Exception as e:
            self.print_plugin_error(
                "shutil.copy('%s', '%s')" % (image_path, destination_path)
            )
            self.print_plugin_error("Error: %s" % str(e))
            result = False

        return result

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy a firmware image to a device using the mps2_copy method.

        If the "capability" name is not 'mps2' this method will just fail.

        Returns:
            True if copy operation succeeded, otherwise False.
        """
        if not kwargs["image_path"]:
            self.print_plugin_error("Error: image path not specified")
            return False

        if not kwargs["destination_disk"]:
            self.print_plugin_error("Error: destination disk not specified")
            return False

        # This optional parameter can be used if TargetID is provided (-t switch)
        target_id = kwargs.get("target_id", None)
        pooling_timeout = kwargs.get("polling_timeout", 60)
        result = False

        if self.check_parameters(capability, *args, **kwargs):
            # Capability 'default' is a dummy capability
            if kwargs["image_path"] and kwargs["destination_disk"]:
                if capability == "mps2":
                    image_path = os.path.normpath(kwargs["image_path"])
                    destination_disk = os.path.normpath(kwargs["destination_disk"])
                    # Wait for mount point to be ready
                    # if mount point changed according to target_id use new mount point
                    # available in result (_, destination_disk) of
                    # check_mount_point_ready
                    result, destination_disk = self.check_mount_point_ready(
                        destination_disk, target_id=target_id, timeout=pooling_timeout
                    )  # Blocking
                    if result:
                        result = self.mps2_copy(image_path, destination_disk)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_MPS2()
