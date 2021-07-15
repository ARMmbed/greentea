#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Tests for the HostRegistry class."""

import unittest
from htrun.host_tests_registry import HostRegistry
from htrun import BaseHostTest


class HostRegistryTestCase(unittest.TestCase):
    class HostTestClassMock(BaseHostTest):
        def setup(self):
            pass

        def result(self):
            pass

        def teardown(self):
            pass

    def setUp(self):
        self.HOSTREGISTRY = HostRegistry()

    def tearDown(self):
        pass

    def test_register_host_test(self):
        self.HOSTREGISTRY.register_host_test(
            "host_test_mock_auto", self.HostTestClassMock()
        )
        self.assertEqual(True, self.HOSTREGISTRY.is_host_test("host_test_mock_auto"))

    def test_unregister_host_test(self):
        self.HOSTREGISTRY.register_host_test(
            "host_test_mock_2_auto", self.HostTestClassMock()
        )
        self.assertEqual(True, self.HOSTREGISTRY.is_host_test("host_test_mock_2_auto"))
        self.assertNotEqual(
            None, self.HOSTREGISTRY.get_host_test("host_test_mock_2_auto")
        )
        self.HOSTREGISTRY.unregister_host_test("host_test_mock_2_auto")
        self.assertEqual(False, self.HOSTREGISTRY.is_host_test("host_test_mock_2_auto"))

    def test_get_host_test(self):
        self.HOSTREGISTRY.register_host_test(
            "host_test_mock_3_auto", self.HostTestClassMock()
        )
        self.assertEqual(True, self.HOSTREGISTRY.is_host_test("host_test_mock_3_auto"))
        self.assertNotEqual(
            None, self.HOSTREGISTRY.get_host_test("host_test_mock_3_auto")
        )

    def test_is_host_test(self):
        self.assertEqual(False, self.HOSTREGISTRY.is_host_test(""))
        self.assertEqual(False, self.HOSTREGISTRY.is_host_test(None))
        self.assertEqual(False, self.HOSTREGISTRY.is_host_test("xyz"))

    def test_host_test_str_not_empty(self):
        for ht_name in self.HOSTREGISTRY.HOST_TESTS:
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            self.assertNotEqual(None, ht)

    def test_host_test_has_name_attribute(self):
        for ht_name in self.HOSTREGISTRY.HOST_TESTS:
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            self.assertTrue(hasattr(ht, "setup"))
            self.assertTrue(hasattr(ht, "result"))
            self.assertTrue(hasattr(ht, "teardown"))


if __name__ == "__main__":
    unittest.main()
