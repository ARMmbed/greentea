#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Use PyOCD to reset a target."""

from .host_test_plugins import HostTestPluginBase

try:
    from pyocd.core.helpers import ConnectHelper

    PYOCD_PRESENT = True
except ImportError:
    PYOCD_PRESENT = False


class HostTestPluginResetMethod_pyOCD(HostTestPluginBase):
    """Plugin interface."""

    name = "HostTestPluginResetMethod_pyOCD"
    type = "ResetMethod"
    stable = True
    capabilities = ["pyocd"]
    required_parameters = ["target_id"]

    def __init__(self):
        """Initialise plugin."""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This is a no-op for this plugin.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """Reset a target using pyOCD.

        The "capability" name must be "pyocd". If it isn't this method will just fail.

        Args:
            capability: Capability name.

        Returns:
            True if the reset was successful, otherwise False.
        """
        if not PYOCD_PRESENT:
            self.print_plugin_error(
                'The "pyocd" feature is not installed. Please run '
                '"pip install mbed-os-tools[pyocd]" to enable the "pyocd" reset plugin.'
            )
            return False

        if not kwargs["target_id"]:
            self.print_plugin_error("Error: target_id not set")
            return False

        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            if kwargs["target_id"]:
                if capability == "pyocd":
                    target_id = kwargs["target_id"]
                    with ConnectHelper.session_with_chosen_probe(
                        unique_id=target_id, resume_on_disconnect=False
                    ) as session:
                        session.target.reset()
                        session.target.resume()
                        result = True
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginResetMethod_pyOCD()
