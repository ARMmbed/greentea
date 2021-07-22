#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Test device echo."""

import uuid
from .. import BaseHostTest


class EchoTest(BaseHostTest):
    """EchoTest."""

    __result = None
    echo_count = 0
    count = 0
    uuid_sent = []
    uuid_recv = []

    def __send_echo_uuid(self):
        if self.echo_count:
            str_uuid = str(uuid.uuid4())
            self.send_kv("echo", str_uuid)
            self.uuid_sent.append(str_uuid)
            self.echo_count -= 1

    def _callback_echo(self, key, value, timestamp):
        self.uuid_recv.append(value)
        self.__send_echo_uuid()

    def _callback_echo_count(self, key, value, timestamp):
        # Handshake
        self.echo_count = int(value)
        self.send_kv(key, value)
        # Send first echo to echo server on DUT
        self.__send_echo_uuid()

    def setup(self):
        """Set up the test."""
        self.register_callback("echo", self._callback_echo)
        self.register_callback("echo_count", self._callback_echo_count)

    def result(self):
        """Report test result."""
        self.__result = self.uuid_sent == self.uuid_recv
        return self.__result

    def teardown(self):
        """Tear down test resources."""
        pass
