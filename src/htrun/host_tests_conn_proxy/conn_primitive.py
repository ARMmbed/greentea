#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Module defines ConnectorPrimitive base class for device connection and comms."""
from ..host_tests_logger import HtrunLogger


class ConnectorPrimitiveException(Exception):
    """Exception in connector primitive module."""

    pass


class ConnectorPrimitive(object):
    """Base class for communicating with DUT."""

    def __init__(self, name):
        """Initialise object.

        Args:
            name: Name to display in the log.
        """
        self.LAST_ERROR = None
        self.logger = HtrunLogger(name)
        self.polling_timeout = 60

    def write_kv(self, key, value):
        """Write a Key-Value protocol message.

        A Key-Value protocol message is in the form '{{key;value}}'. The greentea tests
        running on the DUT recognise messages in this format and act according to the
        given commands.

        Args:
            key: Key part of the Key-Value protocol message.
            value: Value part of the Key-Value message.

        Returns:
            Buffer containing the K-V message on success, None on failure.
        """
        # All Key-Value messages ends with newline character
        kv_buff = "{{%s;%s}}" % (key, value) + "\n"

        if self.write(kv_buff):
            self.logger.prn_txd(kv_buff.rstrip())
            return kv_buff
        else:
            return None

    def read(self, count):
        """Read data from DUT.

        Args:
            count: Number of bytes to read.

        Returns:
            Bytes read.
        """
        raise NotImplementedError

    def write(self, payload, log=False):
        """Write data to the DUT.

        Args:
            payload: Buffer with data to send.
            log: Set to True to enable logging for this function.

        Returns:
            Payload (what was actually sent - if possible to establish that).
        """
        raise NotImplementedError

    def flush(self):
        """Flush read/write channels of the DUT."""
        raise NotImplementedError

    def reset(self):
        """Reset the DUT."""
        raise NotImplementedError

    def connected(self):
        """Check if there is a connection to the DUT.

        Returns:
            True if there is connection to the DUT (read/write/flush API works).
        """
        raise NotImplementedError

    def error(self):
        """LAST_ERROR value.

        Returns:
            Value of self.LAST_ERROR
        """
        return self.LAST_ERROR

    def finish(self):
        """Close the connection to the DUT and perform any clean up operations."""
        raise NotImplementedError
