#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest

from htrun.host_tests_plugins.module_reset_target import (
    HostTestPluginResetMethod_Target,
)


class HostOSDetectionTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin_reset_target = HostTestPluginResetMethod_Target()

    def tearDown(self):
        pass

    def test_examle(self):
        pass

    def test_pyserial_version_detect(self):
        self.assertEqual(1.0, self.plugin_reset_target.get_pyserial_version("1.0"))
        self.assertEqual(1.0, self.plugin_reset_target.get_pyserial_version("1.0.0"))
        self.assertEqual(2.7, self.plugin_reset_target.get_pyserial_version("2.7"))
        self.assertEqual(2.7, self.plugin_reset_target.get_pyserial_version("2.7.1"))
        self.assertEqual(3.0, self.plugin_reset_target.get_pyserial_version("3.0"))
        self.assertEqual(3.0, self.plugin_reset_target.get_pyserial_version("3.0.1"))


if __name__ == "__main__":
    unittest.main()
