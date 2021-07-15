#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""'Hello world' test case."""
from .. import BaseHostTest


class HelloTest(BaseHostTest):
    """'Hello world' test case."""

    HELLO_WORLD = "Hello World"

    __result = None

    def _callback_hello_world(self, key, value, timestamp):
        self.__result = value == self.HELLO_WORLD
        self.notify_complete()

    def setup(self):
        """Set up the test."""
        self.register_callback("hello_world", self._callback_hello_world)

    def result(self):
        """Return the test result."""
        return self.__result

    def teardown(self):
        """Tear down the test case."""
        pass
