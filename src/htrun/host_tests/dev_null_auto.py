#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Test dev null."""
from .. import BaseHostTest


class DevNullTest(BaseHostTest):
    """DevNullTest."""

    __result = None

    def _callback_result(self, key, value, timestamp):
        # We should not see result data in this test
        self.__result = False

    def _callback_to_stdout(self, key, value, timestamp):
        self.__result = True
        self.log("_callback_to_stdout !")

    def setup(self):
        """Set up test."""
        self.register_callback("end", self._callback_result)
        self.register_callback("to_null", self._callback_result)
        self.register_callback("to_stdout", self._callback_to_stdout)

    def result(self):
        """Return test result."""
        return self.__result
