#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest

from htrun.host_tests_registry import HostRegistry


class BaseHostTestTestCase(unittest.TestCase):
    def setUp(self):
        self.HOSTREGISTRY = HostRegistry()

    def tearDown(self):
        pass

    def test_host_test_has_setup_teardown_attribute(self):
        for ht_name in self.HOSTREGISTRY.HOST_TESTS:
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            self.assertTrue(hasattr(ht, "setup"))
            self.assertTrue(hasattr(ht, "teardown"))

    def test_host_test_has_no_rampUpDown_attribute(self):
        for ht_name in self.HOSTREGISTRY.HOST_TESTS:
            ht = self.HOSTREGISTRY.HOST_TESTS[ht_name]
            self.assertFalse(hasattr(ht, "rampUp"))
            self.assertFalse(hasattr(ht, "rampDown"))


if __name__ == "__main__":
    unittest.main()
