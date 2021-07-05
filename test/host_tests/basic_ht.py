#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest

from htrun import get_plugin_caps


class BasicHostTestsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_plugin_caps(self):
        d = get_plugin_caps()
        self.assertIs(type(d), dict)


if __name__ == "__main__":
    unittest.main()
