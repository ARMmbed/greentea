#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest
import os

from htrun.host_tests_plugins.module_copy_mps2 import HostTestPluginCopyMethod_MPS2


class MPS2CopyTestCase(unittest.TestCase):
    def setUp(self):
        self.mps2_copy_plugin = HostTestPluginCopyMethod_MPS2()
        self.filename = "toto.bin"
        # Create the empty file named self.filename
        open(self.filename, "w+").close()

    def tearDown(self):
        os.remove(self.filename)

    def test_copy_bin(self):
        # Check that file has been copied as "mbed.bin"
        self.mps2_copy_plugin.mps2_copy(self.filename, ".")
        self.assertTrue(os.path.isfile("mbed.bin"))
        os.remove("mbed.bin")

    def test_copy_elf(self):
        # Check that file has been copied as "mbed.elf"
        os.rename(self.filename, "toto.elf")
        self.filename = "toto.elf"
        self.mps2_copy_plugin.mps2_copy(self.filename, ".")
        self.assertTrue(os.path.isfile("mbed.elf"))
        os.remove("mbed.elf")


if __name__ == "__main__":
    unittest.main()
