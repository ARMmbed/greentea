#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Wrapper around cp/xcopy/copy."""
import os
from os.path import join, basename
from .host_test_plugins import HostTestPluginBase


class HostTestPluginCopyMethod_Shell(HostTestPluginBase):
    """Plugin interface adaptor for shell copy commands."""

    # Plugin interface
    name = "HostTestPluginCopyMethod_Shell"
    type = "CopyMethod"
    stable = True
    capabilities = ["shell", "cp", "copy", "xcopy"]
    required_parameters = ["image_path", "destination_disk"]

    def __init__(self):
        """Initialise the plugin."""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """Copy an image to a destination disk using a shell copy command.

        "capability" is used to select which command to invoke, valid
        capabilities are "shell", "cp", "copy" and "xcopy".

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

        if not kwargs["destination_disk"]:
            self.print_plugin_error("Error: destination disk not specified")
            return False

        # This optional parameter can be used if TargetID is provided (-t switch)
        target_id = kwargs.get("target_id", None)
        pooling_timeout = kwargs.get("polling_timeout", 60)

        result = False
        if self.check_parameters(capability, *args, **kwargs):
            if kwargs["image_path"] and kwargs["destination_disk"]:
                image_path = os.path.normpath(kwargs["image_path"])
                destination_disk = os.path.normpath(kwargs["destination_disk"])
                # Wait for mount point to be ready
                # if mount point changed according to target_id use new mount point
                # available in result (_, destination_disk) of check_mount_point_ready
                mount_res, destination_disk = self.check_mount_point_ready(
                    destination_disk, target_id=target_id, timeout=pooling_timeout
                )  # Blocking
                if not mount_res:
                    return result  # mount point is not ready return
                # Prepare correct command line parameter values
                image_base_name = basename(image_path)
                destination_path = join(destination_disk, image_base_name)
                if capability == "shell":
                    if os.name == "nt":
                        capability = "copy"
                    elif os.name == "posix":
                        capability = "cp"
                if capability == "cp" or capability == "copy" or capability == "copy":
                    copy_method = capability
                    cmd = [copy_method, image_path, destination_path]
                    if os.name == "posix":
                        result = self.run_command(cmd, shell=False)
                        if os.uname()[0] == "Linux":
                            result = result and self.run_command(
                                ["sync", "-f", destination_path]
                            )
                        else:
                            result = result and self.run_command(["sync"])
                    else:
                        result = self.run_command(cmd)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginCopyMethod_Shell()
