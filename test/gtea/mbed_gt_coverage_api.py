#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import unittest
from mbed_os_tools.test import mbed_coverage_api


class GreenteaCoverageAPI(unittest.TestCase):
    def setUp(self):
        pass

    def test_x(self):
        pass

    def test_coverage_pack_hex_payload(self):
        # This function takesstring as input
        r = mbed_coverage_api.coverage_pack_hex_payload("")
        self.assertEqual(bytearray(b""), r)

        r = mbed_coverage_api.coverage_pack_hex_payload("6164636772")
        self.assertEqual(bytearray(b"adcgr"), r)

        r = mbed_coverage_api.coverage_pack_hex_payload(".")  # '.' -> 0x00
        self.assertEqual(bytearray(b"\x00"), r)

        r = mbed_coverage_api.coverage_pack_hex_payload("...")  # '.' -> 0x00
        self.assertEqual(bytearray(b"\x00\x00\x00"), r)

        r = mbed_coverage_api.coverage_pack_hex_payload(".6164636772.")  # '.' -> 0x00
        self.assertEqual(bytearray(b"\x00adcgr\x00"), r)

    def test_coverage_dump_file_valid(self):
        import tempfile

        payload = bytearray(b"PAYLOAD")
        handle, path = tempfile.mkstemp("test_file")
        mbed_coverage_api.coverage_dump_file(".", path, payload)

        with open(path, "r") as f:
            read_data = f.read()

        self.assertEqual(read_data, payload.decode("utf-8", "ignore"))
        os.close(handle)
        os.remove(path)


if __name__ == "__main__":
    unittest.main()
