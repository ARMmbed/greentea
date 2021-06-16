#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import io
import os
import sys
import unittest

from greentea.gtea.tests_spec import Test, TestBuild, TestSpec, list_binaries_for_builds

simple_test_spec = {
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
        },
        "K64F-GCC": {
            "platform": "K64F",
            "toolchain": "GCC_ARM",
            "base_path": "./.build/K64F/GCC_ARM",
            "baud_rate": 9600,
            "tests": {
                "mbed-drivers-test-generic_tests": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/GCC_ARM/mbed-drivers-test-generic_tests.bin",
                        }
                    ]
                }
            },
        },
    }
}


class TestsSpecFunctionality(unittest.TestCase):
    def setUp(self):
        self.ts_2_builds = simple_test_spec

    def tearDown(self):
        pass

    def test_example(self):
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)

    def test_initialise_test_spec_with_filename(self):
        root_path = os.path.dirname(os.path.realpath(__file__))
        spec_path = os.path.join(root_path, "resources", "test_spec.json")

        self.test_spec = TestSpec(spec_path)
        test_builds = self.test_spec.get_test_builds()

        build = list(filter(lambda x: x.get_name() == "K64F-ARM", test_builds))[0]
        self.assertEqual(build.get_name(), "K64F-ARM")
        self.assertEqual(build.get_platform(), "K64F")
        self.assertEqual(build.get_baudrate(), 9600)
        self.assertEqual(build.get_path(), "./BUILD/K64F/ARM")

        self.assertEqual(len(build.get_tests()), 2)
        self.assertTrue("tests-example-1" in build.get_tests())
        self.assertTrue("tests-example-2" in build.get_tests())

        test = build.get_tests()["tests-example-1"]
        self.assertEqual(test.get_name(), "tests-example-1")
        self.assertEqual(
            test.get_binary().get_path(),
            "./BUILD/K64F/ARM/tests-mbedmicro-rtos-mbed-mail.bin",
        )

        self.assertIs(type(test_builds), list)
        self.assertEqual(len(test_builds), 2)

    def test_initialise_test_spec_with_invalid_filename(self):
        root_path = os.path.dirname(os.path.realpath(__file__))
        spec_path = os.path.join(root_path, "resources", "null.json")

        self.test_spec = TestSpec(spec_path)
        test_builds = self.test_spec.get_test_builds()

    def test_manually_add_test_binary(self):
        test_name = "example-test"
        test_path = "test-path"
        test = Test(test_name)
        self.assertEqual(test.get_name(), test_name)
        self.assertEqual(test.get_binary(), None)

        test.add_binary(test_path, "bootable")
        self.assertEqual(test.get_binary().get_path(), test_path)

    def test_manually_add_test_to_build(self):
        name = "example-test"
        test = Test(name)
        test_build = TestBuild("build", "K64F", "ARM", 9600, "./")

        self.assertEqual(len(test_build.get_tests()), 0)
        test_build.add_test(name, test)
        self.assertEqual(len(test_build.get_tests()), 1)
        self.assertTrue(name in test_build.get_tests())

    def test_manually_add_test_build_to_test_spec(self):
        test_name = "example-test"
        test = Test(test_name)
        test_spec = TestSpec(None)
        build_name = "example-build"
        test_build = TestBuild(build_name, "K64F", "ARM", 9600, "./")
        test_build.add_test(test_name, test)

        self.assertEqual(len(test_spec.get_test_builds()), 0)
        test_spec.add_test_builds(build_name, test_build)
        self.assertEqual(len(test_spec.get_test_builds()), 1)
        self.assertTrue(build_name in test_spec.get_test_builds()[0].get_name())

    def test_get_test_builds(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()

        self.assertIs(type(test_builds), list)
        self.assertEqual(len(test_builds), 2)

    def test_get_test_builds_names(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertEqual(len(test_builds_names), 2)
        self.assertIs(type(test_builds_names), list)

        self.assertIn("K64F-ARM", test_builds_names)
        self.assertIn("K64F-GCC", test_builds_names)

    def test_get_test_build(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertEqual(len(test_builds_names), 2)
        self.assertIs(type(test_builds_names), list)

        self.assertNotEqual(None, self.test_spec.get_test_build("K64F-ARM"))
        self.assertNotEqual(None, self.test_spec.get_test_build("K64F-GCC"))

    def test_get_build_properties(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertEqual(len(test_builds_names), 2)
        self.assertIs(type(test_builds_names), list)

        k64f_arm = self.test_spec.get_test_build("K64F-ARM")
        k64f_gcc = self.test_spec.get_test_build("K64F-GCC")

        self.assertNotEqual(None, k64f_arm)
        self.assertNotEqual(None, k64f_gcc)

        self.assertEqual("K64F", k64f_arm.get_platform())
        self.assertEqual("ARM", k64f_arm.get_toolchain())
        self.assertEqual(115200, k64f_arm.get_baudrate())

        self.assertEqual("K64F", k64f_gcc.get_platform())
        self.assertEqual("GCC_ARM", k64f_gcc.get_toolchain())
        self.assertEqual(9600, k64f_gcc.get_baudrate())

    def test_get_test_builds_properties(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)
        test_builds = self.test_spec.get_test_builds()
        test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

        self.assertIn("K64F-ARM", test_builds_names)
        self.assertIn("K64F-GCC", test_builds_names)

    def test_get_test_builds_names_filter_by_names(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.ts_2_builds)

        filter_by_names = ["K64F-ARM"]
        test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
        test_builds_names = [x.get_name() for x in test_builds]
        self.assertEqual(len(test_builds_names), 1)
        self.assertIn("K64F-ARM", test_builds_names)

        filter_by_names = ["K64F-GCC"]
        test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
        test_builds_names = [x.get_name() for x in test_builds]
        self.assertEqual(len(test_builds_names), 1)
        self.assertIn("K64F-GCC", test_builds_names)

        filter_by_names = ["SOME-PLATFORM-NAME"]
        test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
        test_builds_names = [x.get_name() for x in test_builds]
        self.assertEqual(len(test_builds_names), 0)


class TestListBinaries(unittest.TestCase):
    def test_list_binaries_for_builds(self):
        root_path = os.path.dirname(os.path.realpath(__file__))
        spec_path = os.path.join(root_path, "resources", "test_spec.json")

        spec = TestSpec(spec_path)

        for verbose in [True, False]:
            # Capture logging output
            old_stdout = sys.stdout
            sys.stdout = stdout_capture = io.StringIO()
            list_binaries_for_builds(spec, verbose_footer=verbose)
            sys.stdout = old_stdout

            output = stdout_capture.getvalue()
            self.assertTrue("available tests for build 'K64F-ARM'" in output)
            self.assertTrue("available tests for build 'K64F-GCC'" in output)
            self.assertTrue("tests-example-1" in output)
            self.assertTrue("tests-example-2" in output)
            self.assertTrue("tests-example-7" in output)

            if verbose == True:
                self.assertTrue("Example: execute" in output)


if __name__ == "__main__":
    unittest.main()
