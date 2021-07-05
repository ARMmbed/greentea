#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest

import os
import re
import sys
import platform
from htrun.host_tests_plugins.host_test_plugins import HostTestPluginBase


class HostOSDetectionTestCase(unittest.TestCase):
    def setUp(self):
        self.plugin_base = HostTestPluginBase()
        self.os_names = ["Windows7", "Ubuntu", "LinuxGeneric", "Darwin"]
        self.re_float = re.compile("^\d+\.\d+$")

    def tearDown(self):
        pass

    def test_os_info(self):
        self.assertNotEqual(None, self.plugin_base.host_os_info())

    def test_os_support(self):
        self.assertNotEqual(None, self.plugin_base.host_os_support())

    def test_supported_os_name(self):
        self.assertIn(self.plugin_base.host_os_support(), self.os_names)

    def test_detect_os_support_ext(self):
        os_info = (
            os.name,
            platform.system(),
            platform.release(),
            platform.version(),
            sys.platform,
        )

        self.assertEqual(os_info, self.plugin_base.host_os_info())


if __name__ == "__main__":
    unittest.main()
