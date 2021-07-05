#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import six
import sys
import unittest

from greentea import greentea_cli
from greentea.gtea.tests_spec import TestSpec

test_spec_def = {
    "builds": {
        "K64F-ARM": {
            "platform": "K64F",
            "toolchain": "ARM",
            "base_path": "./.build/K64F/ARM",
            "baud_rate": 115200,
            "tests": {
                "mbed-drivers-test-generic_tests": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-generic_tests.bin",
                        }
                    ]
                },
                "mbed-drivers-test-c_strings": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-c_strings.bin",
                        }
                    ]
                },
            },
        }
    }
}


class GreenteaCliFunctionality(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_greentea_version(self):
        version = greentea_cli.get_greentea_version()

        self.assertIs(type(version), str)

        version_list = version.split(".")

        self.assertEqual(version_list[0].isdigit(), True)
        self.assertEqual(version_list[1].isdigit(), True)
        self.assertEqual(version_list[2].isdigit(), True)

    def test_print_version(self):
        version = greentea_cli.get_greentea_version()

        old_stdout = sys.stdout
        sys.stdout = stdout_capture = six.StringIO()
        greentea_cli.print_version()
        sys.stdout = old_stdout

        printed_version = stdout_capture.getvalue().splitlines()[0]
        self.assertEqual(printed_version, version)

    def test_get_hello_string(self):
        version = greentea_cli.get_greentea_version()
        hello_string = greentea_cli.get_hello_string()

        self.assertIs(type(version), str)
        self.assertIs(type(hello_string), str)
        self.assertIn(version, hello_string)

    def test_get_local_host_tests_dir_invalid_path(self):
        test_path = greentea_cli.get_local_host_tests_dir("invalid-path")
        self.assertEqual(test_path, None)

    def test_get_local_host_tests_dir_valid_path(self):
        path = "."
        test_path = greentea_cli.get_local_host_tests_dir(path)
        self.assertEqual(test_path, path)

    def test_get_local_host_tests_dir_default_path(self):
        import os
        import shutil
        import tempfile

        curr_dir = os.getcwd()
        test1_dir = tempfile.mkdtemp()
        test2_dir = os.mkdir(os.path.join(test1_dir, "test"))
        test3_dir = os.mkdir(os.path.join(test1_dir, "test", "host_tests"))

        os.chdir(test1_dir)

        test_path = greentea_cli.get_local_host_tests_dir("")
        self.assertEqual(test_path, "./test/host_tests")

        os.chdir(curr_dir)
        shutil.rmtree(test1_dir)

    def test_create_filtered_test_list(self):
        test_spec = TestSpec()
        test_spec.parse(test_spec_def)
        test_build = test_spec.get_test_builds()[0]

        test_list = greentea_cli.create_filtered_test_list(
            test_build.get_tests(),
            "mbed-drivers-test-generic_*",
            None,
            test_spec=test_spec,
        )
        self.assertEqual(
            set(test_list.keys()), set(["mbed-drivers-test-generic_tests"])
        )

        test_list = greentea_cli.create_filtered_test_list(
            test_build.get_tests(), "*_strings", None, test_spec=test_spec
        )
        self.assertEqual(set(test_list.keys()), set(["mbed-drivers-test-c_strings"]))

        test_list = greentea_cli.create_filtered_test_list(
            test_build.get_tests(), "mbed*s", None, test_spec=test_spec
        )
        expected = set(
            ["mbed-drivers-test-c_strings", "mbed-drivers-test-generic_tests"]
        )
        self.assertEqual(set(test_list.keys()), expected)

        test_list = greentea_cli.create_filtered_test_list(
            test_build.get_tests(), "*-drivers-*", None, test_spec=test_spec
        )
        expected = set(
            ["mbed-drivers-test-c_strings", "mbed-drivers-test-generic_tests"]
        )
        self.assertEqual(set(test_list.keys()), expected)

        # Should be case insensitive
        test_list = greentea_cli.create_filtered_test_list(
            test_build.get_tests(), "*-DRIVERS-*", None, test_spec=test_spec
        )
        expected = set(
            ["mbed-drivers-test-c_strings", "mbed-drivers-test-generic_tests"]
        )
        self.assertEqual(set(test_list.keys()), expected)


if __name__ == "__main__":
    unittest.main()
