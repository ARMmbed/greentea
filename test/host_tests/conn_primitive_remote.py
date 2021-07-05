#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from unittest.mock import MagicMock

from htrun.host_tests_conn_proxy.conn_primitive_remote import RemoteConnectorPrimitive


class RemoteResourceMock(object):
    def __init__(self, requirements):
        self._is_allocated = True
        self._is_connected = True
        self.requirements = requirements
        self.open_connection = MagicMock()
        self.close_connection = MagicMock()
        self.write = MagicMock()
        self.read = MagicMock()
        self.read.return_value = "abc"
        self.disconnect = MagicMock()
        self.flash = MagicMock()
        self.reset = MagicMock()
        self.release = MagicMock()

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def is_allocated(self):
        return self._is_allocated


class RemoteModuleMock(object):
    class SerialParameters(object):
        def __init__(self, baudrate):
            self.baudrate = baudrate

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.is_allocated_mock = MagicMock()
        self.allocate = MagicMock()
        self.allocate.side_effect = lambda req: RemoteResourceMock(req)
        self.get_resources = MagicMock()
        self.get_resources.return_value = [1]

    @staticmethod
    def create(host, port):
        return RemoteModuleMock(host, port)


class ConnPrimitiveRemoteTestCase(unittest.TestCase):
    def setUp(self):
        self.config = {
            "grm_module": "RemoteModuleMock",
            "tags": "a,b",
            "image_path": "test.bin",
            "platform_name": "my_platform",
        }
        self.importer = MagicMock()
        self.importer.side_effect = lambda x: RemoteModuleMock
        self.remote = RemoteConnectorPrimitive("remote", self.config, self.importer)

    def test_constructor(self):
        self.importer.assert_called_once_with("RemoteModuleMock")

        self.remote.client.get_resources.called_once()
        self.assertEqual(self.remote.remote_module, RemoteModuleMock)
        self.assertIsInstance(self.remote.client, RemoteModuleMock)
        self.assertIsInstance(self.remote.selected_resource, RemoteResourceMock)

        # allocate is called
        self.remote.client.allocate.assert_called_once_with(
            {
                "platform_name": self.config.get("platform_name"),
                "power_on": True,
                "connected": True,
                "tags": {"a": True, "b": True},
            }
        )

        # flash is called
        self.remote.selected_resource.open_connection.called_once_with("test.bin")

        # open_connection is called
        self.remote.selected_resource.open_connection.called_once()
        connect = self.remote.selected_resource.open_connection.call_args[1]
        self.assertEqual(connect["parameters"].baudrate, 9600)

        # reset once
        self.remote.selected_resource.reset.assert_called_once_with()

    def test_write(self):
        self.remote.write("abc")
        self.remote.selected_resource.write.assert_called_once_with("abc")

    def test_read(self):
        data = self.remote.read(6)
        self.remote.selected_resource.read.assert_called_once_with(6)
        self.assertEqual(data, "abc")

    def test_reset(self):
        self.remote.reset()
        self.assertEqual(self.remote.selected_resource.reset.call_count, 2)

    def test_finish(self):
        resource = self.remote.selected_resource
        self.remote.finish()
        self.assertEqual(self.remote.selected_resource, None)
        resource.close_connection.assert_called_once()
        resource.release.assert_called_once()


if __name__ == "__main__":
    unittest.main()
