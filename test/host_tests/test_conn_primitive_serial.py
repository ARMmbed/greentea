#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest
import mock

from htrun.host_tests_conn_proxy.conn_primitive_serial import SerialConnectorPrimitive
from htrun.host_tests_conn_proxy.conn_primitive import ConnectorPrimitiveException


@mock.patch("htrun.host_tests_conn_proxy.conn_primitive_serial.Serial")
@mock.patch("htrun.host_tests_plugins.host_test_plugins.create")
class ConnPrimitiveSerialTestCase(unittest.TestCase):
    def test_provided_serial_port_used_with_target_id(self, mock_create, mock_serial):
        platform_name = "irrelevant"
        target_id = "1234"
        port = "COM256"
        baudrate = "9600"

        # The mock list_mbeds() call needs to return a list of dictionaries,
        # and each dictionary must have a "serial_port", or else the
        # check_serial_port_ready() function we are testing will sleep waiting
        # for the serial port to become ready.
        mock_create().list_mbeds.return_value = [
            {
                "target_id": target_id,
                "serial_port": port,
                "platform_name": platform_name,
            },
        ]

        # Set skip_reset to avoid the use of a physical serial port.
        config = {
            "port": port,
            "baudrate": baudrate,
            "image_path": "test.bin",
            "platform_name": "kaysixtyfoureff",
            "target_id": "9900",
            "skip_reset": True,
        }
        connector = SerialConnectorPrimitive("SERI", port, baudrate, config=config)

        mock_create().list_mbeds.assert_not_called()

    def test_discovers_serial_port_with_target_id(self, mock_create, mock_serial):
        platform_name = "kaysixtyfoureff"
        target_id = "9900"
        port = "COM256"
        baudrate = "9600"

        mock_create().list_mbeds.return_value = [
            {
                "target_id": target_id,
                "serial_port": port,
                "platform_name": platform_name,
            },
        ]

        # Set skip_reset to avoid the use of a physical serial port. Don't pass
        # in a port, so that auto-detection based on target_id will find the
        # port for us (using our mock list_mbeds data).
        config = {
            "port": None,
            "baudrate": baudrate,
            "image_path": "test.bin",
            "platform_name": platform_name,
            "target_id": target_id,
            "skip_reset": True,
        }
        try:
            connector = SerialConnectorPrimitive("SERI", None, baudrate, config=config)
        except ConnectorPrimitiveException:
            # lol bad
            pass

        mock_create().list_mbeds.assert_called_once()


if __name__ == "__main__":
    unittest.main()
