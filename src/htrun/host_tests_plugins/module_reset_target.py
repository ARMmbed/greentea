#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Serial reset plugin."""

import re
import pkg_resources
from .host_test_plugins import HostTestPluginBase


class HostTestPluginResetMethod_Target(HostTestPluginBase):
    """Plugin interface adapter for serial reset."""

    # Plugin interface
    name = "HostTestPluginResetMethod_Target"
    type = "ResetMethod"
    stable = True
    capabilities = ["default"]
    required_parameters = ["serial"]

    def __init__(self):
        """Initialise plugin."""
        HostTestPluginBase.__init__(self)
        self.re_float = re.compile(r"^\d+\.\d+")
        pyserial_version = pkg_resources.require("pyserial")[0].version
        self.pyserial_version = self.get_pyserial_version(pyserial_version)
        self.is_pyserial_v3 = float(self.pyserial_version) >= 3.0

    def get_pyserial_version(self, pyserial_version):
        """Retrieve pyserial module version.

        Returns:
            Float with pyserial module number.
        """
        version = 3.0
        m = self.re_float.search(pyserial_version)
        if m:
            try:
                version = float(m.group(0))
            except ValueError:
                version = 3.0  # We will assume you've got latest (3.0+)
        return version

    def safe_sendBreak(self, serial):
        """Closure for pyserial version dependent API calls."""
        if self.is_pyserial_v3:
            return self._safe_sendBreak_v3_0(serial)
        return self._safe_sendBreak_v2_7(serial)

    def _safe_sendBreak_v2_7(self, serial):
        """Pyserial 2.7 API implementation of sendBreak/setBreak.

        Below API is deprecated for pyserial 3.x versions!
        http://pyserial.readthedocs.org/en/latest/pyserial_api.html#serial.Serial.sendBreak
        http://pyserial.readthedocs.org/en/latest/pyserial_api.html#serial.Serial.setBreak
        """
        result = True
        try:
            serial.sendBreak()
        except Exception:
            # In Linux a termios.error is raised in sendBreak and in setBreak.
            # The following setBreak() is needed to release the reset signal on the
            # target mcu.
            try:
                serial.setBreak(False)
            except Exception:
                result = False
        return result

    def _safe_sendBreak_v3_0(self, serial):
        """Pyserial 3.x API implementation of send_break / break_condition.

        http://pyserial.readthedocs.org/en/latest/pyserial_api.html#serial.Serial.send_break
        http://pyserial.readthedocs.org/en/latest/pyserial_api.html#serial.Serial.break_condition
        """
        result = True
        try:
            serial.send_break()
        except Exception:
            # In Linux a termios.error is raised in sendBreak and in setBreak.
            # The following break_condition = False is needed to release the reset
            # signal on the target mcu.
            try:
                serial.break_condition = False
            except Exception as e:
                self.print_plugin_error(
                    "Error while doing 'serial.break_condition = False' : %s" % str(e)
                )
                result = False
        return result

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """Reset a device using serial break.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the reset succeeded, otherwise False.
        """
        if not kwargs["serial"]:
            self.print_plugin_error("Error: serial port not set (not opened?)")
            return False

        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            if kwargs["serial"]:
                if capability == "default":
                    serial = kwargs["serial"]
                    result = self.safe_sendBreak(serial)
        return result


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginResetMethod_Target()
