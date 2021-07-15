#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Implements STLINK_CLI copy method."""

import os
import sys
import tempfile
from .host_test_plugins import HostTestPluginBase

FIX_FILE_NAME = "enter_file.txt"


class HostTestPluginResetMethod_Stlink(HostTestPluginBase):
    """Plugin interface adaptor for STLINK_CLI."""

    # Plugin interface
    name = "HostTestPluginResetMethod_Stlink"
    type = "ResetMethod"
    capabilities = ["stlink"]
    required_parameters = []
    stable = False

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
        # Note you need to have eACommander.exe on your system path!
        self.ST_LINK_CLI = "ST-LINK_CLI.exe"
        return True

    def create_stlink_fix_file(self, file_path):
        """Create a file with a line separator.

        This is to work around a bug in ST-LINK CLI that does not let the target run
        after burning it.
        See https://github.com/ARMmbed/mbed-os-tools/issues/147 for the details.

        Note:
            This method will exit the python interpreter if it encounters an OSError.

        Args:
            file_path: A path to write into this file.
        """
        try:
            with open(file_path, "w") as fix_file:
                fix_file.write(os.linesep)
        except (OSError, IOError):
            self.print_plugin_error("Error opening STLINK-PRESS-ENTER-BUG file")
            sys.exit(1)

    def execute(self, capability, *args, **kwargs):
        """Reset a device using the ST-LINK-CLI.

        Note:
            This method will exit the python interpreter if it encounters an OSError.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.


        Returns:
            True if the reset succeeded, otherwise False.
        """
        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            if capability == "stlink":
                # Example:
                # ST-LINK_CLI.exe -Rst -Run
                cmd = [self.ST_LINK_CLI, "-Rst", "-Run"]

                # Due to the ST-LINK bug, we must press enter after burning the target
                # We do this here automatically by passing a file which contains an
                # `ENTER` (line separator) to the ST-LINK CLI as `stdin` for the running
                # process
                enter_file_path = os.path.join(tempfile.gettempdir(), FIX_FILE_NAME)
                self.create_stlink_fix_file(enter_file_path)
                try:
                    with open(enter_file_path, "r") as fix_file:
                        stdin_arg = kwargs.get("stdin", fix_file)
                        result = self.run_command(cmd, stdin=stdin_arg)
                except (OSError, IOError):
                    self.print_plugin_error("Error opening STLINK-PRESS-ENTER-BUG file")
                    sys.exit(1)

        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginResetMethod_Stlink()
