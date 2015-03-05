#!/usr/bin/env python

"""
mbed SDK
Copyright (c) 2011-2014 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

import os
import re
import sys
import json
import optparse

from mbed_test_api import run_host_test
from mbed_test_api import process_stdin
from mbed_test_api import run_cli_command
from cmake_handlers import load_ctest_testsuite
from mbed_target_info import get_mbed_clasic_target_info
from mbed_target_info import get_mbed_supported_test

try:
    import mbed_lstools
    import mbed_host_tests
except:
    pass

MBED_LMTOOLS = 'mbed_lstools' in sys.modules
MBED_HOST_TESTS = 'mbed_host_tests' in sys.modules


# git clone repository
# cd repo
# yotta target frdm-....
# yt build
#
# yt --target=frdm-XXXX,* build
#

def main():

    if not MBED_LMTOOLS:
        print "Error: mbed-lstools mbed proprietary module not installed"
        exit(-1)

    if not MBED_HOST_TESTS:
        print "Error: mbed-host-tests mbed proprietary module not installed"
        exit(-1)

    parser = optparse.OptionParser()

    parser.add_option('', '--target',
                    dest='list_of_targets',
                    help='You can specify list of targets you want to build. Use comma to sepatate them')

    #parser.add_option('-n', '--test-by-names',
    #                dest='test_by_names',
    #                help='Runs only test enumerated it this switch')

    parser.add_option("-O", "--only-build",
                    action="store_true",
                    dest="only_build_tests",
                    default=False,
                    help="Only build repository and tests, skips actual test procedures (flashing etc.)")

    parser.add_option('', '--config',
                    dest='verbose_test_configuration_only',
                    default=False,
                    action="store_true",
                    help='Displays full test specification and MUTs configration and exits')

    parser.add_option('', '--loops',
                    dest='test_loops_list',
                    help='Set no. of loops per test. Format: TEST_1=1,TEST_2=2,TEST_3=3')

    parser.add_option('', '--global-loops',
                    dest='test_global_loops_value',
                    help='Set global number of test loops per test. Default value is set 1')

    parser.add_option('-W', '--waterfall',
                    dest='waterfall_test',
                    default=False,
                    action="store_true",
                    help='Used with --loops or --global-loops options. Tests until OK result occurs and assumes test passed.')

    parser.add_option('-V', '--verbose-test-result',
                      dest='verbose_test_result_only',
                      default=False,
                      action="store_true",
                      help='Prints test serial output')

    parser.add_option('-v', '--verbose',
                    dest='verbose',
                    default=False,
                    action="store_true",
                    help='Verbose mode (prints some extra information)')

    parser.add_option('-r', '--read-stdin',
                    dest='read_stdin',
                    default=False,
                    action="store_true",
                    help='Process output from stdin, instead of from connected microcontrollers.')

    parser.description = """This automated test script is used to test mbed SDK 3.0 on mbed-enabled deviecs with support from yotta build tool"""
    parser.epilog = """Example: mbedgt --auto --target frdm-k64f-gcc"""

    (opts, args) = parser.parse_args()

    if opts.read_stdin:
        # if we're being piped test output, process a single test then return
        # its exit status
        status = process_stdin(duration=10, verbose=opts.verbose)
        sys.exit(status)

    # mbed-enabled devices auto-detection procedures
    mbeds = mbed_lstools.create()
    mbeds_list = mbeds.list_mbeds()

    print "mbed-ls: detecting connected mbed-enabled devices... %s"% ("no devices detected" if not len(mbeds_list) else "")
    list_of_targets = opts.list_of_targets.split(',') if opts.list_of_targets is not None else None

    for mut in mbeds_list:
        print "mbed-ls: detected %s, console at: %s, mounted at: %s"% (mut['platform_name'],
            mut['serial_port'],
            mut['mount_point'])

        # Check if mbed classic target name can be translated to yotta target name
        mut_info = get_mbed_clasic_target_info(mut['platform_name'])
        if mut_info is None:
            print "mbed-ls: mbed classic target name %s is not in target database"% (mut['platform_name'])
        else:
            for yotta_target in mut_info['yotta_targets']:
                yotta_target_name = yotta_target['yotta_target']
                yotta_target_toolchain = yotta_target['mbed_toolchain']
                print "\tgot yotta target '%s'"% (yotta_target_name)

                if opts.verbose_test_configuration_only:
                    continue

                # Building sources for given target
                if list_of_targets is None or yotta_target_name in list_of_targets:
                    print "mbed-ls: calling yotta to build your sources and tests"
                    yotta_verbose = '-v' if opts.verbose is not None else ''
                    yotta_result = run_cli_command("yotta %s --target=%s,* build"% (yotta_verbose, yotta_target_name))

                    # Build phase will be followed by test execution for each target
                    if yotta_result and not opts.only_build_tests:
                        binary_type = mut_info['properties']['binary_type']
                        ctest_test_list = load_ctest_testsuite(os.path.join('.', 'build', yotta_target_name),
                            binary_type=binary_type)

                        print "mbedgt: running tests..."
                        for test_bin, image_path in ctest_test_list.iteritems():
                            test_result = 'SKIPPED'
                            if get_mbed_supported_test(test_bin):
                                disk =  mut['mount_point']
                                port =  mut['serial_port']
                                duration = 10
                                micro = mut['platform_name']
                                program_cycle_s = mut_info['properties']['program_cycle_s']
                                copy_method = mut_info['properties']['copy_method']
                                verbose = opts.verbose_test_result_only

                                host_test_result = run_host_test(image_path, disk, port, duration,
                                    micro=micro,
                                    copy_method=copy_method,
                                    program_cycle_s=program_cycle_s,
                                    verbose=verbose)
                                single_test_result, single_test_output, single_testduration, single_timeout = host_test_result
                                test_result = single_test_result
                            print "\ttest '%s' %s"% (test_bin, '.' * (70 - len(test_bin))),
                            print "%s"% (test_result)
