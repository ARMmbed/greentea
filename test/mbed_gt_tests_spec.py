#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from mbed_greentea.tests_spec import TestSpec

simple_test_spec = {
    "builds": {
        "K64F-ARM": {
            "platform": "K64F",
            "toolchain": "ARM",
            "base_path": "./.build/K64F/ARM",
            "baud_rate": 115200,
            "tests": {
                "mbed-drivers-test-generic_tests":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-generic_tests.bin"
                        }
                    ]
                },
                "mbed-drivers-test-c_strings":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/ARM/mbed-drivers-test-c_strings.bin"
                        }
                    ]
                }
            }
        },
        "K64F-GCC": {
            "platform": "K64F",
            "toolchain": "GCC_ARM",
            "base_path": "./.build/K64F/GCC_ARM",
            "baud_rate": 9600,
            "tests": {
                "mbed-drivers-test-generic_tests":{
                    "binaries":[
                        {
                            "binary_type": "bootable",
                            "path": "./.build/K64F/GCC_ARM/mbed-drivers-test-generic_tests.bin"
                        }
                    ]
                }

            }
        }

    }
}

test_case_test_spec = {
    "builds": {
        "K64F-ARM": {
            "platform": "K64F",
            "toolchain": "ARM",
            "base_path": "./.build/K64F/ARM",
            "baud_rate": 115200,
            "tests": {
                "tests-mbed_drivers-generic_tests": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": ".build/tests/K64F/ARM/TESTS/mbed_drivers/generic_tests/tests-mbed_drivers-generic_tests.bin"
                        }
                    ],
                    "testcases": [
                        "Blinky", 
                        "C++ stack", 
                        "C++ heap", 
                        "Basic"
                    ]
                },
                "tests-mbed_drivers-c_strings": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": ".build/tests/K64F/ARM/TESTS/mbed_drivers/c_strings/tests-mbed_drivers-c_strings.bin"
                        }
                    ],
                    "testcases": [
                        "C strings: strpbrk", 
                        "C strings: %g %g float formatting", 
                        "C strings: %f %f float formatting", 
                        "C strings: %u %d integer formatting", 
                        "C strings: strtok", 
                        "C strings: %i %d integer formatting", 
                        "C strings: %e %E float formatting", 
                        "C strings: %x %E integer formatting"
                    ]
                }
            }
        },
        "K64F-GCC": {
            "platform": "K64F",
            "toolchain": "GCC_ARM",
            "base_path": "./.build/K64F/GCC_ARM",
            "baud_rate": 9600,
            "tests": {
                "tests-mbed_drivers-generic_tests": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": ".build/tests/K64F/GCC_ARM/TESTS/mbed_drivers/generic_tests/tests-mbed_drivers-generic_tests.bin", 
                            "testcases": [
                                "Blinky", 
                                "C++ stack", 
                                "C++ heap", 
                                "Basic"
                            ]
                        }
                    ]
                },
                "tests-mbed_drivers-c_strings": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": ".build/tests/K64F/ARM/TESTS/mbed_drivers/c_strings/tests-mbed_drivers-c_strings.bin", 
                            "testcases": [
                                "Blinky"
                            ]
                        }
                    ]
                }
            }
        }

    }
}


class TestsSpecFunctionality(unittest.TestCase):

    def setUp(self):
        self.test_specs = [simple_test_spec, test_case_test_spec]
        self.tc_ts = test_case_test_spec

    def tearDown(self):
        pass

    def test_example(self):
        self.assertEqual(True, True)
        self.assertNotEqual(True, False)

    def test_get_test_builds(self):
        # Test compatibility with old and new format
        for test_spec in self.test_specs:
            self.test_spec = TestSpec()
            self.test_spec.parse(test_spec)
            test_builds = self.test_spec.get_test_builds()

            self.assertIs(type(test_builds), list)
            self.assertEqual(len(test_builds), 2)

    def test_get_test_builds_names(self):
        for test_spec in self.test_specs:
            self.test_spec = TestSpec()
            self.test_spec.parse(test_spec)
            test_builds = self.test_spec.get_test_builds()
            test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

            self.assertEqual(len(test_builds_names), 2)
            self.assertIs(type(test_builds_names), list)

            self.assertIn('K64F-ARM', test_builds_names)
            self.assertIn('K64F-GCC', test_builds_names)

    def test_get_test_build(self):
        for test_spec in self.test_specs:
            self.test_spec = TestSpec()
            self.test_spec.parse(test_spec)
            test_builds = self.test_spec.get_test_builds()
            test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

            self.assertEqual(len(test_builds_names), 2)
            self.assertIs(type(test_builds_names), list)

            self.assertNotEqual(None, self.test_spec.get_test_build('K64F-ARM'))
            self.assertNotEqual(None, self.test_spec.get_test_build('K64F-GCC'))

    def test_get_build_properties(self):
        for test_spec in self.test_specs:
            self.test_spec = TestSpec()
            self.test_spec.parse(test_spec)
            test_builds = self.test_spec.get_test_builds()
            test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

            self.assertEqual(len(test_builds_names), 2)
            self.assertIs(type(test_builds_names), list)

            k64f_arm = self.test_spec.get_test_build('K64F-ARM')
            k64f_gcc = self.test_spec.get_test_build('K64F-GCC')

            self.assertNotEqual(None, k64f_arm)
            self.assertNotEqual(None, k64f_gcc)

            self.assertEqual('K64F', k64f_arm.get_platform())
            self.assertEqual('ARM', k64f_arm.get_toolchain())
            self.assertEqual(115200, k64f_arm.get_baudrate())

            self.assertEqual('K64F', k64f_gcc.get_platform())
            self.assertEqual('GCC_ARM', k64f_gcc.get_toolchain())
            self.assertEqual(9600, k64f_gcc.get_baudrate())

    def test_get_test_builds_properties(self):
        for test_spec in self.test_specs:
            self.test_spec = TestSpec()
            self.test_spec.parse(test_spec)
            test_builds = self.test_spec.get_test_builds()
            test_builds_names = [x.get_name() for x in self.test_spec.get_test_builds()]

            self.assertIn('K64F-ARM', test_builds_names)
            self.assertIn('K64F-GCC', test_builds_names)

    def test_get_test_builds_names_filter_by_names(self):
        for test_spec in self.test_specs:
            self.test_spec = TestSpec()
            self.test_spec.parse(test_spec)

            filter_by_names = ['K64F-ARM']
            test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
            test_builds_names = [x.get_name() for x in test_builds]
            self.assertEqual(len(test_builds_names), 1)
            self.assertIn('K64F-ARM', test_builds_names)

            filter_by_names = ['K64F-GCC']
            test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
            test_builds_names = [x.get_name() for x in test_builds]
            self.assertEqual(len(test_builds_names), 1)
            self.assertIn('K64F-GCC', test_builds_names)

            filter_by_names = ['SOME-PLATFORM-NAME']
            test_builds = self.test_spec.get_test_builds(filter_by_names=filter_by_names)
            test_builds_names = [x.get_name() for x in test_builds]
            self.assertEqual(len(test_builds_names), 0)

    def test_get_test_cases(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.tc_ts)
        test_cases = self.test_spec.get_test_cases()

        self.assertIs(type(test_cases), set)
        self.assertEqual(len(test_cases), 12)
        self.assertIn('C strings: %g %g float formatting', test_cases)
        self.assertIn('C++ stack', test_cases)

    def test_get_test_cases_by_name(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.tc_ts)
        test_cases = self.test_spec.get_test_cases_by_test_name()

        self.assertIs(type(test_cases), dict)
        self.assertEqual(len(test_cases), 2)
        self.assertIn("tests-mbed_drivers-c_strings", test_cases)
        self.assertEqual(len(test_cases["tests-mbed_drivers-c_strings"]), 8)

    def test_get_test_cases_by_test_name(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.tc_ts)
        test_builds = self.test_spec.get_test_builds(filter_by_names=['K64F-ARM'])
        
        self.assertEqual(len(test_builds), 1)

        test_case_test_names = test_builds[0].get_test_cases_test_name()

        self.assertEqual(len(test_case_test_names), 12)
        self.assertIn('Blinky', test_case_test_names)
        self.assertEqual('tests-mbed_drivers-generic_tests', test_case_test_names['Blinky'])
        self.assertIn('C strings: %g %g float formatting', test_case_test_names)
        self.assertEqual('tests-mbed_drivers-c_strings', test_case_test_names['C strings: %g %g float formatting'])

    def test_get_test_cases_by_test_name_conflict(self):
        self.test_spec = TestSpec()
        self.test_spec.parse(self.tc_ts)
        test_builds = self.test_spec.get_test_builds(filter_by_names=['K64F-GCC'])
        
        self.assertEqual(len(test_builds), 1)

        test_case_test_names = test_builds[0].get_test_cases_test_name()

        self.assertEqual(len(test_case_test_names), 0)

if __name__ == '__main__':
    unittest.main()
