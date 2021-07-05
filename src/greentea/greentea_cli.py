#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""CLI implementation for Greentea."""
import os
import random
import argparse
import imp
import io
from time import time

from queue import Queue
from threading import Thread


from greentea.gtea.test_api import (
    get_test_build_properties,
    get_test_spec,
    log_devices_in_table,
    TEST_RESULT_OK,
    TEST_RESULT_FAIL,
    parse_global_resource_mgr,
    parse_fast_model_connection,
)

from greentea.gtea.report_api import (
    exporter_text,
    exporter_testcase_text,
    exporter_json,
    exporter_testcase_junit,
    exporter_html,
    exporter_memory_metrics_csv,
)

from greentea.gtea.greentea_log import gt_logger

from greentea.gtea.greentea_hooks import GreenteaHooks
from greentea.gtea.tests_spec import TestBinary
from greentea.gtea.target_info import get_platform_property

from .test_api import run_host_test

from mbed_lstools.main import create as mbedls_create
from htrun import host_tests_plugins as host_tests_plugins

from greentea.gtea.greentea_cli import (
    RET_NO_DEVICES,
    get_local_host_tests_dir,
    create_filtered_test_list,
)

LOCAL_HOST_TESTS_DIR = "./test/host_tests"  # Used by htrun -e <dir>


def get_greentea_version():
    """Get Greentea (mbed-greentea) Python module version.

    Returns:
        String representation of the Greentea version.
    """
    import pkg_resources  # part of setuptools

    version = pkg_resources.require("mbed-greentea")[0].version
    return version


def print_version():
    """Print current Greentea package version."""
    print(get_greentea_version())


def get_hello_string():
    """Get hello string indicating Greentea version.

    Returns:
        Hello string with Greentea version.
    """
    version = get_greentea_version()
    return "greentea test automation tool ver. " + version


def main():
    """Closure for main_cli() function."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--target",
        dest="list_of_targets",
        help=(
            "Specify a list of targets to build, using commas to separate them. "
            "If --test-spec is used, this will filter builds from the given test spec."
        ),
    )

    parser.add_argument(
        "-n",
        "--test-by-names",
        dest="test_by_names",
        help=(
            "Specify a list of tests to run, using commas to separate test case names."
        ),
    )

    parser.add_argument(
        "-i",
        "--skip-test",
        dest="skip_test",
        help=(
            "Specify a list of tests to skip, using commas to separate test case names."
        ),
    )

    parser.add_argument(
        "-O",
        "--only-build",
        action="store_true",
        dest="only_build_tests",
        default=False,
        help=(
            "Skip printing results and creating reports. Useful when only return code "
            "is needed."
        ),
    )

    copy_methods_str = "Plugin support: " + ", ".join(
        host_tests_plugins.get_plugin_caps("CopyMethod")
    )
    parser.add_argument(
        "-c",
        "--copy",
        dest="copy_method",
        help=f"Copy method selector. {copy_methods_str}",
        metavar="COPY_METHOD",
    )

    reset_methods_str = "Plugin support: " + ", ".join(
        host_tests_plugins.get_plugin_caps("ResetMethod")
    )
    parser.add_argument(
        "-r",
        "--reset",
        dest="reset_method",
        help=f"Reset method selector. {reset_methods_str}",
        metavar="RESET_METHOD",
    )

    parser.add_argument(
        "--parallel",
        dest="parallel_test_exec",
        default=1,
        help=(
            "Experimental: execute test runners to your host DUTs in parallel. "
            "Speeds up test result collection."
        ),
    )

    parser.add_argument(
        "-e",
        "--enum-host-tests",
        dest="enum_host_tests",
        help="Define directory with local host tests. Default: ./test/host_tests.",
    )

    parser.add_argument(
        "--config",
        dest="verbose_test_configuration_only",
        default=False,
        action="store_true",
        help="Displays connected boards and detected targets and exits.",
    )

    parser.add_argument(
        "-l",
        "--list",
        dest="list_binaries",
        default=False,
        action="store_true",
        help="List available binaries.",
    )

    parser.add_argument(
        "-g",
        "--grm",
        dest="global_resource_mgr",
        help=(
            'Global resource manager: "<platform name>: '
            '<remote mgr module>:<host url or IP address>[:<port>]", '
            'Ex. "K64F:module_name:10.2.123.43:3334", '
            '"K64F:module_name:https://example.com".'
        ),
    )

    # Show --fm option only if "fm_agent" module installed
    try:
        imp.find_module("fm_agent")
    except ImportError:
        fm_help = argparse.SUPPRESS
    else:
        fm_help = (
            "Use a Fast Model Connection in format fastmodel name:config name. "
            "Example: FVP_MPS2_M3:DEFAULT."
        )
    parser.add_argument("--fm", dest="fast_model_connection", help=fm_help)

    parser.add_argument(
        "--use-tids",
        dest="use_target_ids",
        help=(
            "Specify explicitly which devices can be used by Greentea. Format as a "
            "comma-separated list of allowed Target IDs (use comma separated list)."
        ),
    )

    parser.add_argument(
        "-u",
        "--shuffle",
        dest="shuffle_test_order",
        default=False,
        action="store_true",
        help="Shuffle test execution order",
    )

    parser.add_argument(
        "--shuffle-seed",
        dest="shuffle_test_seed",
        default=None,
        help=(
            "Shuffle seed. "
            "To reproduce previous shuffle order, use seed from test summary"
        ),
    )

    parser.add_argument(
        "--sync",
        dest="num_sync_packets",
        default=5,
        help=(
            "Define how many times __sync packet will be sent to device: 0: none; -1: "
            "forever; 1,2,3... - number of  times. Default: 5 packets."
        ),
    )

    parser.add_argument(
        "-P",
        "--polling-timeout",
        dest="polling_timeout",
        default=60,
        metavar="NUMBER",
        type=int,
        help=(
            "Timeout in sec for readiness of mount point and serial port of local or "
            "remote device. Default: 60 sec."
        ),
    )

    parser.add_argument(
        "--tag-filters",
        dest="tags",
        default=None,
        help=(
            "Specify comma-separated list of tags required for DUTs. "
            "Available devices without these tags will be filtered out."
        ),
    )

    parser.add_argument(
        "-H",
        "--hooks",
        dest="hooks_json",
        help="Load hooks used drive extra functionality.",
    )

    parser.add_argument(
        "--test-spec",
        dest="test_spec",
        help="Specify test specification generated by build system to use.",
    )

    parser.add_argument(
        "--test-cfg",
        dest="json_test_configuration",
        help="Pass to host test data with host test configuration.",
    )

    parser.add_argument(
        "--run",
        dest="run_app",
        help="Flash, reset and dump serial from selected binary application.",
    )

    parser.add_argument(
        "--report-junit",
        dest="report_junit_file_name",
        help=(
            "Specify file to log test suite results to, as a JUnit compliant XML report"
        ),
    )

    parser.add_argument(
        "--report-text",
        dest="report_text_file_name",
        help="Specify a text file to log test suite results to.",
    )

    parser.add_argument(
        "--report-json",
        dest="report_json_file_name",
        help="Specify a JSON formatted file to log test suite results to.",
    )

    parser.add_argument(
        "--report-html",
        dest="report_html_file_name",
        help="Specify file to log test suite results to, as a HTML page.",
    )

    parser.add_argument(
        "--report-fails",
        dest="report_fails",
        default=False,
        action="store_true",
        help="Print console outputs for failed tests.",
    )

    parser.add_argument(
        "--retry-count",
        dest="retry_count",
        default=1,
        type=int,
        help="Retry count for individual test failure. By default, there is no retry.",
    )

    parser.add_argument(
        "--report-memory-metrics-csv",
        dest="report_memory_metrics_csv_file_name",
        help="Specify CSV file to log test suite memory metrics.",
    )

    parser.add_argument(
        "-V",
        "--verbose-test-result",
        dest="verbose_test_result_only",
        default=False,
        action="store_true",
        help="Print test serial output.",
    )

    parser.add_argument(
        "--plain",
        dest="plain",
        default=False,
        action="store_true",
        help="Do not use colours while logging.",
    )

    parser.add_argument(
        "--version",
        dest="version",
        default=False,
        action="store_true",
        help="Prints package version and exits.",
    )

    parser.description = (
        """This automated test script is used to test devices using greentea tests."""
    )
    parser.epilog = """Example: gtea --target frdm-k64f-gcc"""

    args = parser.parse_args()

    cli_ret = 0

    if not args.version:
        # This string should not appear when fetching plain version string
        gt_logger.gt_log(get_hello_string())

    start = time()
    # Standard mode of operation
    # Must provide mutually exclusive access control to platforms and targets
    try:
        cli_ret = main_cli(args)
    except KeyboardInterrupt:
        gt_logger.gt_log_err("ctrl+c keyboard interrupt!")
        return 1  # Keyboard interrupt
    except Exception as e:
        gt_logger.gt_log_err("unexpected error:")
        gt_logger.gt_log_tab(str(e))
        raise

    if not any([args.list_binaries, args.version]):
        delta = time() - start  # Test execution time delta
        gt_logger.gt_log("completed in %.2f sec" % delta)

    if cli_ret:
        if cli_ret < 0 or cli_ret > 255:
            cli_ret = 1
        gt_logger.gt_log_err("exited with code %d" % cli_ret)

    return cli_ret


def run_test_thread(
    test_result_queue, test_queue, args, dut, build, build_path, greentea_hooks
):
    """Run all tests in queue.

    Args:
        test_result_queue: Queue for test results to be put into.
        test_queue: Queue of tests to be ran on the DUT.
        args: Arguments from the CLI.
        dut: Device under test to execute tests on.
        build: Name of the build in progress.
        build_path: Path to the build directory.
        greentea_hooks: GreenteaHook specifying hook to execute after completion.
    """
    test_exec_retcode = 0
    test_platforms_match = 0
    test_report = {}

    disk = dut["mount_point"]
    # Set format used by htrun: 'serial_port' = '<serial_port_name>:<baudrate>'
    port = "{}:{}".format(dut["serial_port"], dut["baud_rate"])
    micro = dut["platform_name"]
    program_cycle_s = get_platform_property(micro, "program_cycle_s")
    forced_reset_timeout = get_platform_property(micro, "forced_reset_timeout")
    copy_method = get_platform_property(micro, "copy_method")
    reset_method = get_platform_property(micro, "reset_method")

    while not test_queue.empty():
        try:
            test = test_queue.get(False)
        except Exception as e:
            gt_logger.gt_log_err(str(e))
            break

        test_result = "SKIPPED"

        if args.copy_method:
            copy_method = args.copy_method
        elif not copy_method:
            copy_method = "shell"

        if args.reset_method:
            reset_method = args.reset_method

        verbose = args.verbose_test_result_only
        enum_host_tests_path = get_local_host_tests_dir(args.enum_host_tests)

        test_platforms_match += 1
        host_test_result = run_host_test(
            test["image_path"],
            disk,
            port,
            build_path,
            dut["target_id"],
            micro=micro,
            copy_method=copy_method,
            reset=reset_method,
            program_cycle_s=program_cycle_s,
            forced_reset_timeout=forced_reset_timeout,
            json_test_cfg=args.json_test_configuration,
            enum_host_tests_path=enum_host_tests_path,
            global_resource_mgr=args.global_resource_mgr,
            fast_model_connection=args.fast_model_connection,
            compare_log=test["compare_log"],
            num_sync_packets=args.num_sync_packets,
            tags=args.tags,
            retry_count=args.retry_count,
            polling_timeout=args.polling_timeout,
            verbose=verbose,
        )

        # Some error in htrun, abort test execution
        if isinstance(host_test_result, int):
            # int(host_test_result) > 0 - Call to htrun failed
            # int(host_test_result) < 0 - Something went wrong while executing htrun
            gt_logger.gt_log_err("run_test_thread.run_host_test() failed, aborting...")
            break

        # If execution was successful 'run_host_test' return tuple with results
        (
            single_test_result,
            single_test_output,
            single_testduration,
            single_timeout,
            result_test_cases,
            test_cases_summary,
            memory_metrics,
        ) = host_test_result
        test_result = single_test_result

        build_path_abs = os.path.abspath(build_path)

        if single_test_result != TEST_RESULT_OK:
            test_exec_retcode += 1

        if single_test_result in [TEST_RESULT_OK, TEST_RESULT_FAIL]:
            if greentea_hooks:
                # Test was successful
                # We can execute test hook just after test is finished ('hook_test_end')
                format = {
                    "test_name": test["test_bin"],
                    "test_bin_name": os.path.basename(test["image_path"]),
                    "image_path": test["image_path"],
                    "build_path": build_path,
                    "build_path_abs": build_path_abs,
                    "build_name": build,
                }
                greentea_hooks.run_hook("hook_test_end", format)

        # Update report for optional reporting feature
        test_suite_name = test["test_bin"].lower()
        if build not in test_report:
            test_report[build] = {}

        if test_suite_name not in test_report[build]:
            test_report[build][test_suite_name] = {}

        if not test_cases_summary and not result_test_cases:
            gt_logger.gt_log_warn("test case summary event not found")
            gt_logger.gt_log_tab(
                "no test case report present, "
                "assuming test suite to be a single test case!"
            )

            # We will map test suite result to test case to
            # output valid test case in report

            # Generate "artificial" test case name from test suite name#
            # E.g:
            #   mbed-drivers-test-dev_null -> dev_null
            test_case_name = test_suite_name
            test_str_idx = test_suite_name.find("-test-")
            if test_str_idx != -1:
                test_case_name = test_case_name[test_str_idx + 6 :]

            gt_logger.gt_log_tab("test suite: %s" % test_suite_name)
            gt_logger.gt_log_tab("test case: %s" % test_case_name)

            # Test case result: OK, FAIL or ERROR
            tc_result_text = {"OK": "OK", "FAIL": "FAIL"}.get(
                single_test_result, "ERROR"
            )

            # Test case integer success code OK, FAIL and ERROR: (0, >0, <0)
            tc_result = {"OK": 0, "FAIL": 1024, "ERROR": -1024}.get(tc_result_text)

            # Test case passes and failures: (1 pass, 0 failures)
            # or (0 passes, 1 failure)
            tc_passed, tc_failed = {0: (1, 0)}.get(tc_result, (0, 1))

            # Test case report build for whole binary
            # Add test case made from test suite result to test case report
            result_test_cases = {
                test_case_name: {
                    "duration": single_testduration,
                    "time_start": 0.0,
                    "time_end": 0.0,
                    "utest_log": single_test_output.splitlines(),
                    "result_text": tc_result_text,
                    "passed": tc_passed,
                    "failed": tc_failed,
                    "result": tc_result,
                }
            }

            # Test summary build for whole binary (as a test case)
            test_cases_summary = (
                tc_passed,
                tc_failed,
            )

        gt_logger.gt_log("test on hardware with target id: %s" % (dut["target_id"]))
        gt_logger.gt_log(
            "test suite '%s' %s %s in %.2f sec"
            % (
                test["test_bin"],
                "." * (80 - len(test["test_bin"])),
                test_result,
                single_testduration,
            )
        )

        # Test report build for whole binary
        test_report[build][test_suite_name]["single_test_result"] = single_test_result
        test_report[build][test_suite_name]["single_test_output"] = single_test_output
        test_report[build][test_suite_name]["elapsed_time"] = single_testduration
        test_report[build][test_suite_name]["platform_name"] = micro
        test_report[build][test_suite_name]["copy_method"] = copy_method
        test_report[build][test_suite_name]["testcase_result"] = result_test_cases
        test_report[build][test_suite_name]["memory_metrics"] = memory_metrics

        test_report[build][test_suite_name]["build_path"] = build_path
        test_report[build][test_suite_name]["build_path_abs"] = build_path_abs
        test_report[build][test_suite_name]["image_path"] = test["image_path"]
        test_report[build][test_suite_name]["test_bin_name"] = os.path.basename(
            test["image_path"]
        )

        passes_cnt, failures_cnt = 0, 0
        for tc_name in sorted(result_test_cases.keys()):
            gt_logger.gt_log_tab(
                "test case: '%s' %s %s in %.2f sec"
                % (
                    tc_name,
                    "." * (80 - len(tc_name)),
                    result_test_cases[tc_name].get("result_text", "_"),
                    result_test_cases[tc_name].get("duration", 0.0),
                )
            )
            if result_test_cases[tc_name].get("result_text", "_") == "OK":
                passes_cnt += 1
            else:
                failures_cnt += 1

        if test_cases_summary:
            passes, failures = test_cases_summary
            gt_logger.gt_log(
                "test case summary: %d pass%s, %d failur%s"
                % (
                    passes,
                    "" if passes == 1 else "es",
                    failures,
                    "e" if failures == 1 else "es",
                )
            )
            if passes != passes_cnt or failures != failures_cnt:
                gt_logger.gt_log_err(
                    "utest test case summary mismatch: "
                    "utest reported passes and failures miscount!"
                )
                gt_logger.gt_log_tab(
                    "reported by utest: passes = %d, failures %d)" % (passes, failures)
                )
                gt_logger.gt_log_tab(
                    "test case result count: passes = %d, failures %d)"
                    % (passes_cnt, failures_cnt)
                )

        if single_test_result != "OK" and not verbose and args.report_fails:
            # In some cases we want to print console to see why test failed
            # even if we are not in verbose mode
            gt_logger.gt_log_tab(
                "test failed, reporting console output "
                "(specified with --report-fails option)"
            )
            print()
            print(single_test_output)

    # greentea_release_target_id(dut['target_id'], gt_instance_uuid)
    test_result_queue.put(
        {
            "test_platforms_match": test_platforms_match,
            "test_exec_retcode": test_exec_retcode,
            "test_report": test_report,
        }
    )
    return


def main_cli(args, gt_instance_uuid=None):
    """Run main CLI function with all command line parameters.

    Implements CLI workflow depending on inputed arguments.

    Returns:
        None, exits to environment with success code.
    """

    def filter_ready_devices(duts_list):
        """Filter list of DUTs to check if correctly detected.

        Args:
            duts_list List of DUTs to verify

        Returns:
            Tuple of DUTs detected correctly, DUTs not detected fully.
        """
        ready_devices = []
        not_ready_devices = []

        required_dut_props = [
            "target_id",
            "platform_name",
            "serial_port",
            "mount_point",
        ]

        gt_logger.gt_log(
            "detected %d device%s"
            % (len(duts_list), "s" if len(duts_list) != 1 else "")
        )
        for dut in duts_list:
            for prop in required_dut_props:
                if not dut[prop]:
                    if dut not in not_ready_devices:
                        not_ready_devices.append(dut)
                        gt_logger.gt_log_err(
                            "mbed-ls was unable to enumerate correctly all properties "
                            "of the device!"
                        )
                        gt_logger.gt_log_tab(
                            "check with 'mbedls -j' command if all properties of your "
                            "device are enumerated properly"
                        )

                    gt_logger.gt_log_err(
                        "mbed-ls property '%s' is '%s'" % (prop, str(dut[prop]))
                    )
                    if prop == "serial_port":
                        gt_logger.gt_log_tab(
                            "check if your serial port driver is correctly installed!"
                        )
                    if prop == "mount_point":
                        gt_logger.gt_log_tab(
                            "check if your OS can detect and "
                            "mount the device's mount point!"
                        )
            else:
                ready_devices.append(dut)
        return (ready_devices, not_ready_devices)

    def get_parallel_value(value):
        """Get allowed value for --parallel.

        Args:
            value: String with number of executions in parallel allowed.

        Returns:
            Value as int, or 1 if value was not valid.
        """
        try:
            parallel_test_exec = int(value)
            if parallel_test_exec < 1:
                parallel_test_exec = 1
        except ValueError:
            gt_logger.gt_log_err(
                "argument of mode --parallel is not a int, disabled parallel mode"
            )
            parallel_test_exec = 1
        return parallel_test_exec

    # This is how you magically control colours in this piece of art software
    gt_logger.colorful(not args.plain)

    # Prints version and exits
    if args.version:
        print_version()
        return 0

    # Load test specification or print warnings / info messages and exit CLI mode
    test_spec, ret = get_test_spec(args)
    if not test_spec:
        return ret

    # Verbose flag
    verbose = args.verbose_test_result_only

    # We will load hooks from JSON file to support extra behaviour during test execution
    greentea_hooks = GreenteaHooks(args.hooks_json) if args.hooks_json else None

    # Query with mbedls for available mbed-enabled devices
    gt_logger.gt_log("detecting connected mbed-enabled devices...")

    # check if argument of --parallel mode is a integer and greater or equal 1
    parallel_test_exec = get_parallel_value(args.parallel_test_exec)

    # Detect devices connected to system
    mbeds = mbedls_create()
    mbeds_list = mbeds.list_mbeds(unique_names=True, read_details_txt=True)

    if args.global_resource_mgr:
        # Mocking available platform requested by --grm switch
        grm_values = parse_global_resource_mgr(args.global_resource_mgr)
        if grm_values:
            gt_logger.gt_log_warn(
                "entering global resource manager mbed-ls dummy mode!"
            )
            grm_platform_name, grm_module_name, grm_ip_name, grm_port_name = grm_values
            mbeds_list = []
            if grm_platform_name == "*":
                required_devices = [
                    tb.get_platform() for tb in test_spec.get_test_builds()
                ]
                for _ in range(parallel_test_exec):
                    for device in required_devices:
                        mbeds_list.append(mbeds.get_dummy_platform(device))
            else:
                for _ in range(parallel_test_exec):
                    mbeds_list.append(mbeds.get_dummy_platform(grm_platform_name))
            args.global_resource_mgr = ":".join([v for v in grm_values[1:] if v])
            gt_logger.gt_log_tab("adding dummy platform '%s'" % grm_platform_name)
        else:
            gt_logger.gt_log(
                "global resource manager switch '--grm %s' in wrong format!"
                % args.global_resource_mgr
            )
            return -1

    if args.fast_model_connection:
        # Mocking available platform requested by --fm switch
        fm_values = parse_fast_model_connection(args.fast_model_connection)
        if fm_values:
            gt_logger.gt_log_warn(
                "entering fastmodel connection, mbed-ls dummy simulator mode!"
            )
            fm_platform_name, fm_config_name = fm_values
            mbeds_list = []
            for _ in range(parallel_test_exec):
                mbeds_list.append(mbeds.get_dummy_platform(fm_platform_name))
            args.fast_model_connection = fm_config_name
            gt_logger.gt_log_tab(
                "adding dummy fastmodel platform '%s'" % fm_platform_name
            )
        else:
            gt_logger.gt_log(
                "fast model connection switch '--fm %s' in wrong format!"
                % args.fast_model_connection
            )
            return -1

    ready_devices = []  # Devices which can be used (are fully detected)
    not_ready_devices = []  # Devices which can't be used (are not fully detected)

    if mbeds_list:
        ready_devices, not_ready_devices = filter_ready_devices(mbeds_list)
        if ready_devices:
            # devices in form of a pretty formatted table
            for line in log_devices_in_table(ready_devices).splitlines():
                gt_logger.gt_log_tab(line.strip(), print_text=verbose)
    else:
        gt_logger.gt_log_err("no compatible devices detected")
        return RET_NO_DEVICES

    # We can filter in only specific target ids
    accepted_target_ids = None
    if args.use_target_ids:
        gt_logger.gt_log(
            "filtering out target ids not on below list (specified with --use-tids)"
        )
        accepted_target_ids = args.use_target_ids.split(",")
        for tid in accepted_target_ids:
            gt_logger.gt_log_tab("accepting target id '%s'" % gt_logger.gt_bright(tid))

    test_exec_retcode = 0  # Decrement this value each time test case result is not 'OK'
    test_platforms_match = (
        0  # Count how many tests were actually ran with current settings
    )
    target_platforms_match = (
        0  # Count how many platforms were actually tested with current settings
    )

    test_report = {}  # Test report used to export to Junit, HTML etc...
    test_queue = (
        Queue()
    )  # contains information about test_bin and image_path for each test case
    test_result_queue = Queue()  # used to store results of each thread
    execute_threads = []  # list of threads to run test cases

    # Values used to generate random seed for test execution order shuffle
    SHUFFLE_SEED_ROUND = 10  # Value used to round float random seed
    shuffle_random_seed = round(random.random(), SHUFFLE_SEED_ROUND)

    # Set shuffle seed if it is provided with command line option
    if args.shuffle_test_seed:
        shuffle_random_seed = round(float(args.shuffle_test_seed), SHUFFLE_SEED_ROUND)

    # Testing procedures, for each target, for each target's compatible platform
    # When using test spec (switch --test-spec) command line option -t <list_of_targets>
    # is used to enumerate builds from test spec supplied
    filter_test_builds = (
        args.list_of_targets.split(",") if args.list_of_targets else None
    )
    for test_build in test_spec.get_test_builds(filter_test_builds):
        platform_name = test_build.get_platform()
        gt_logger.gt_log(
            "processing target '%s' toolchain '%s' compatible platforms..."
            "(note: switch set to --parallel %d)"
            % (
                gt_logger.gt_bright(platform_name),
                gt_logger.gt_bright(test_build.get_toolchain()),
                parallel_test_exec,
            )
        )

        baudrate = test_build.get_baudrate()

        # Select DUTs to test from list of available DUTs to start testing
        dut = None
        number_of_parallel_instances = 1
        duts_to_test = []  # DUTs to actually be tested
        for dev in ready_devices:
            if accepted_target_ids and dev["target_id"] not in accepted_target_ids:
                continue

            # Check that we have a valid serial port detected.
            sp = dev["serial_port"]
            if not sp:
                gt_logger.gt_log_err(
                    "Serial port for target %s not detected correctly\n"
                    % dev["target_id"]
                )
                continue

            if dev["platform_name"] == platform_name:
                dev["baud_rate"] = baudrate

                dut = dev
                if dev not in duts_to_test:
                    # Only add unique devices to the list to test
                    duts_to_test.append(dev)
                if number_of_parallel_instances < parallel_test_exec:
                    number_of_parallel_instances += 1
                else:
                    break

        # devices in form of a pretty formatted table
        for line in log_devices_in_table(duts_to_test).splitlines():
            gt_logger.gt_log_tab(line.strip(), print_text=verbose)

        # Configuration print mode:
        if args.verbose_test_configuration_only:
            continue

        # If we have at least one available device we can proceed
        if dut:
            target_platforms_match += 1

            build = test_build.get_name()
            build_path = test_build.get_path()

            # Demo mode: --run implementation (already added --run to htrun)
            # Pass file name to htrun (--run NAME  =>  -f NAME_ and run only one binary)
            if args.run_app:
                gt_logger.gt_log(
                    "running '%s' for '%s'-'%s'"
                    % (
                        gt_logger.gt_bright(args.run_app),
                        gt_logger.gt_bright(platform_name),
                        gt_logger.gt_bright(test_build.get_toolchain()),
                    )
                )
                disk = dut["mount_point"]
                # Set format used by htrun:
                # 'serial_port' = '<serial_port_name>:<baudrate>'
                port = "{}:{}".format(dut["serial_port"], dut["baud_rate"])
                micro = dut["platform_name"]
                program_cycle_s = get_platform_property(micro, "program_cycle_s")
                copy_method = args.copy_method if args.copy_method else "shell"
                enum_host_tests_path = get_local_host_tests_dir(args.enum_host_tests)

                test_platforms_match += 1
                host_test_result = run_host_test(
                    args.run_app,
                    disk,
                    port,
                    build_path,
                    dut["target_id"],
                    micro=micro,
                    copy_method=copy_method,
                    program_cycle_s=program_cycle_s,
                    json_test_cfg=args.json_test_configuration,
                    run_app=args.run_app,
                    enum_host_tests_path=enum_host_tests_path,
                    verbose=True,
                )

                # Some error in htrun, abort test execution
                if isinstance(host_test_result, int):
                    # int(host_test_result) > 0 - Call to htrun failed
                    # int(host_test_result) < 0 - Error while executing htrun
                    return host_test_result

                # If execution was successful 'run_host_test' return tuple with results
                (
                    single_test_result,
                    single_test_output,
                    single_testduration,
                    single_timeout,
                    result_test_cases,
                    test_cases_summary,
                    memory_metrics,
                ) = host_test_result
                if single_test_result != TEST_RESULT_OK:
                    test_exec_retcode += 1

            test_list = test_build.get_tests()

            filtered_test_list = create_filtered_test_list(
                test_list, args.test_by_names, args.skip_test, test_spec=test_spec
            )

            gt_logger.gt_log(
                "running %d test%s for platform '%s' and toolchain '%s'"
                % (
                    len(filtered_test_list),
                    "s" if len(filtered_test_list) != 1 else "",
                    gt_logger.gt_bright(platform_name),
                    gt_logger.gt_bright(test_build.get_toolchain()),
                )
            )

            # Test execution order can be shuffled (also with provided random seed)
            # for test execution reproduction.
            filtered_test_list_keys = filtered_test_list.keys()
            if args.shuffle_test_order:
                # We want to shuffle test names randomly
                random.shuffle(filtered_test_list_keys, lambda: shuffle_random_seed)

            for test_name in filtered_test_list_keys:
                image_path = (
                    filtered_test_list[test_name]
                    .get_binary(binary_type=TestBinary.BIN_TYPE_BOOTABLE)
                    .get_path()
                )
                compare_log = (
                    filtered_test_list[test_name]
                    .get_binary(binary_type=TestBinary.BIN_TYPE_BOOTABLE)
                    .get_compare_log()
                )
                if image_path is None:
                    gt_logger.gt_log_err(
                        "Failed to find test binary for test %s flash method %s"
                        % (test_name, "usb")
                    )
                else:
                    test = {
                        "test_bin": test_name,
                        "image_path": image_path,
                        "compare_log": compare_log,
                    }
                    test_queue.put(test)

            number_of_threads = 0
            for dut in duts_to_test:
                # Experimental, parallel test execution
                if number_of_threads < parallel_test_exec:
                    test_args = (
                        test_result_queue,
                        test_queue,
                        args,
                        dut,
                        build,
                        build_path,
                        greentea_hooks,
                    )
                    t = Thread(target=run_test_thread, args=test_args)
                    execute_threads.append(t)
                    number_of_threads += 1

        gt_logger.gt_log_tab(
            "use %s instance%s of execution threads for testing"
            % (len(execute_threads), "s" if len(execute_threads) != 1 else str()),
            print_text=verbose,
        )
        for t in execute_threads:
            t.daemon = True
            t.start()

        # merge partial test reports from different threads to final test report
        for t in execute_threads:
            try:
                # We can't block forever here since that prevents KeyboardInterrupts
                # from being propagated correctly. Therefore, we just join with a
                # timeout of 0.1 seconds until the thread isn't alive anymore.
                # A time of 0.1 seconds is a fairly arbitrary choice. It needs
                # to balance CPU utilization and responsiveness to keyboard interrupts.
                # Checking 10 times a second seems to be stable and responsive.
                while t.is_alive():
                    t.join(0.1)

                test_return_data = test_result_queue.get(False)
            except Exception as e:
                # No test report generated
                gt_logger.gt_log_err("could not generate test report" + str(e))
                test_exec_retcode += -1000
                return test_exec_retcode

            test_platforms_match += test_return_data["test_platforms_match"]
            test_exec_retcode += test_return_data["test_exec_retcode"]
            partial_test_report = test_return_data["test_report"]
            # todo: find better solution, maybe use extend
            for report_key in partial_test_report.keys():
                if report_key not in test_report:
                    test_report[report_key] = {}
                    test_report.update(partial_test_report)
                else:
                    test_report[report_key].update(partial_test_report[report_key])

        execute_threads = []

        if args.verbose_test_configuration_only:
            print(
                "Example: execute 'gt --target=TARGET_NAME' "
                "to start testing for TARGET_NAME target"
            )
            return 0

        gt_logger.gt_log("all tests finished!")

    # We will execute post test hooks on tests
    for build_name in test_report:
        test_name_list = []  # All test case names for particular target
        for test_name in test_report[build_name]:
            test = test_report[build_name][test_name]
            # Test was successful
            if test["single_test_result"] in [TEST_RESULT_OK, TEST_RESULT_FAIL]:
                test_name_list.append(test_name)
                # Call hook executed for each test, just after all tests are finished
                if greentea_hooks:
                    format = {
                        "test_name": test_name,
                        "test_bin_name": test["test_bin_name"],
                        "image_path": test["image_path"],
                        "build_path": test["build_path"],
                        "build_path_abs": test["build_path_abs"],
                    }
                    greentea_hooks.run_hook("hook_post_test_end", format)
        if greentea_hooks:
            build = test_spec.get_test_build(build_name)
            assert build is not None, (
                "Failed to find build info for build %s" % build_name
            )

            # Call hook executed for each target, just after all tests are finished
            build_path = build.get_path()
            build_path_abs = os.path.abspath(build_path)
            format = {
                "build_path": build_path,
                "build_path_abs": build_path_abs,
                "test_name_list": test_name_list,
            }
            greentea_hooks.run_hook("hook_post_all_test_end", format)

    # This tool is designed to work in CI
    # We want to only return success codes based on tool actions,
    # only if tests were executed and all passed we want to
    # return 0 (success)
    if not args.only_build_tests:
        # Prints shuffle seed
        gt_logger.gt_log(
            "shuffle seed: %.*f" % (SHUFFLE_SEED_ROUND, shuffle_random_seed)
        )

        def dump_report_to_text_file(filename, content):
            """Closure for report dumps to text files.

            Args:
                filename: Name of destination file.
                content: Text content of the file to write.

            Returns:
                True if write was successful, else False.
            """
            try:
                with io.open(
                    filename, encoding="utf-8", errors="backslashreplace", mode="w"
                ) as f:
                    f.write(content)
            except IOError as e:
                gt_logger.gt_log_err("can't export to '%s', reason:" % filename)
                gt_logger.gt_log_err(str(e))
                return False
            return True

        # Reports to JUNIT file
        if args.report_junit_file_name:
            gt_logger.gt_log(
                "exporting to JUNIT file '%s'..."
                % gt_logger.gt_bright(args.report_junit_file_name)
            )
            # This test specification will be used by JUnit exporter to populate
            # TestSuite.properties (useful meta-data for Viewer)
            test_suite_properties = {}
            for target_name in test_report:
                test_build_properties = get_test_build_properties(
                    test_spec, target_name
                )
                if test_build_properties:
                    test_suite_properties[target_name] = test_build_properties
            junit_report = exporter_testcase_junit(
                test_report, test_suite_properties=test_suite_properties
            )
            dump_report_to_text_file(args.report_junit_file_name, junit_report)

        # Reports results table to text file
        if args.report_text_file_name:
            gt_logger.gt_log(
                "exporting to TEXT '%s'..."
                % gt_logger.gt_bright(args.report_text_file_name)
            )
            text_report, text_results = exporter_text(test_report)
            text_testcase_report, text_testcase_results = exporter_testcase_text(
                test_report
            )
            text_final_report = "\n".join(
                [text_report, text_results, text_testcase_report, text_testcase_results]
            )
            dump_report_to_text_file(args.report_text_file_name, text_final_report)

        # Reports to JSON file
        if args.report_json_file_name:
            # We will not print summary and json report together
            gt_logger.gt_log(
                "exporting to JSON '%s'..."
                % gt_logger.gt_bright(args.report_json_file_name)
            )
            json_report = exporter_json(test_report)
            dump_report_to_text_file(args.report_json_file_name, json_report)

        # Reports to HTML file
        if args.report_html_file_name:
            gt_logger.gt_log(
                "exporting to HTML file '%s'..."
                % gt_logger.gt_bright(args.report_html_file_name)
            )
            # Generate a HTML page displaying all of the results
            html_report = exporter_html(test_report)
            dump_report_to_text_file(args.report_html_file_name, html_report)

        # Memory metrics to CSV file
        if args.report_memory_metrics_csv_file_name:
            gt_logger.gt_log(
                "exporting memory metrics to CSV file '%s'..."
                % gt_logger.gt_bright(args.report_memory_metrics_csv_file_name)
            )
            # Generate a CSV file page displaying all memory metrics
            memory_metrics_csv_report = exporter_memory_metrics_csv(test_report)
            dump_report_to_text_file(
                args.report_memory_metrics_csv_file_name, memory_metrics_csv_report
            )

        # Final summary
        if test_report:
            # Test suite report
            gt_logger.gt_log("test suite report:")
            text_report, text_results = exporter_text(test_report)
            print(text_report)
            gt_logger.gt_log("test suite results: " + text_results)
            # test case detailed report
            gt_logger.gt_log("test case report:")
            text_testcase_report, text_testcase_results = exporter_testcase_text(
                test_report
            )
            print(text_testcase_report)
            gt_logger.gt_log("test case results: " + text_testcase_results)

        # This flag guards 'build only' so we expect only errors
        if test_platforms_match == 0:
            # No tests were executed
            gt_logger.gt_log_warn("no platform/target matching tests were found!")
        if target_platforms_match == 0:
            # No platforms were tested
            gt_logger.gt_log_warn("no matching platforms were found!")

    return test_exec_retcode
