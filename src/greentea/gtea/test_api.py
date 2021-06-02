#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Functions for extracting data from test outputs."""
import re
import os
import sys
import json
import string
from subprocess import Popen, PIPE, STDOUT

from .coverage_api import coverage_dump_file, coverage_pack_hex_payload
from .greentea_log import gt_logger
from .tests_spec import TestSpec, list_binaries_for_builds


# Return codes for test script
TEST_RESULT_OK = "OK"
TEST_RESULT_FAIL = "FAIL"
TEST_RESULT_ERROR = "ERROR"
TEST_RESULT_SKIPPED = "SKIPPED"
TEST_RESULT_UNDEF = "UNDEF"
TEST_RESULT_IOERR_COPY = "IOERR_COPY"
TEST_RESULT_IOERR_DISK = "IOERR_DISK"
TEST_RESULT_IOERR_SERIAL = "IOERR_SERIAL"
TEST_RESULT_TIMEOUT = "TIMEOUT"
TEST_RESULT_NO_IMAGE = "NO_IMAGE"
TEST_RESULT_MBED_ASSERT = "MBED_ASSERT"
TEST_RESULT_BUILD_FAILED = "BUILD_FAILED"
TEST_RESULT_SYNC_FAILED = "SYNC_FAILED"

TEST_RESULTS = [
    TEST_RESULT_OK,
    TEST_RESULT_FAIL,
    TEST_RESULT_ERROR,
    TEST_RESULT_SKIPPED,
    TEST_RESULT_UNDEF,
    TEST_RESULT_IOERR_COPY,
    TEST_RESULT_IOERR_DISK,
    TEST_RESULT_IOERR_SERIAL,
    TEST_RESULT_TIMEOUT,
    TEST_RESULT_NO_IMAGE,
    TEST_RESULT_MBED_ASSERT,
    TEST_RESULT_BUILD_FAILED,
    TEST_RESULT_SYNC_FAILED,
]

TEST_RESULT_MAPPING = {
    "success": TEST_RESULT_OK,
    "failure": TEST_RESULT_FAIL,
    "error": TEST_RESULT_ERROR,
    "skipped": TEST_RESULT_SKIPPED,
    "end": TEST_RESULT_UNDEF,
    "ioerr_copy": TEST_RESULT_IOERR_COPY,
    "ioerr_disk": TEST_RESULT_IOERR_DISK,
    "ioerr_serial": TEST_RESULT_IOERR_SERIAL,
    "timeout": TEST_RESULT_TIMEOUT,
    "no_image": TEST_RESULT_NO_IMAGE,
    "mbed_assert": TEST_RESULT_MBED_ASSERT,
    "build_failed": TEST_RESULT_BUILD_FAILED,
    "sync_failed": TEST_RESULT_SYNC_FAILED,
}


# Return code when invoking htrun fails
RUN_HOST_TEST_POPEN_ERROR = 1729


def get_test_result(output):
    """Parse test 'output' data.

    Args:
        output: Test result output data to parse.

    Returns:
        Test result, or TEST_RESULT_TIMEOUT value.
    """
    re_detect = re.compile(r"\{result;([\w+_]*)\}")

    for line in output.split():
        search_result = re_detect.search(line)
        if search_result:
            if search_result.group(1) in TEST_RESULT_MAPPING:
                return TEST_RESULT_MAPPING[search_result.group(1)]
            else:
                return TEST_RESULT_UNDEF
    return TEST_RESULT_TIMEOUT


def run_command(cmd):
    """Run command with Popen.

    Args:
        cmd: List with command line to execute e.g. ['ls', '-l].

    Returns:
        Value returned by subprocess.Popen, None if fails.
    """
    try:
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
    except OSError as e:
        gt_logger.gt_log_err("run_host_test.run_command(%s) failed!" % str(cmd))
        gt_logger.gt_log_tab(str(e))
        return None
    return p


def run_htrun(cmd, verbose):
    """Call htrun command.

    Args:
        cmd: Command to call.
        verbose: Flag for outputting from htrun to stdout.

    Returns:
        Tuple of popen return code and htrun output.
    """
    htrun_output = str()
    p = run_command(cmd)
    if p is None:
        return RUN_HOST_TEST_POPEN_ERROR, None

    htrun_failure_line = re.compile(r"\[RXD\] (:\d+::FAIL: .*)")

    for line in iter(p.stdout.readline, b""):
        decoded_line = line.decode("utf-8", "replace")
        htrun_output += decoded_line
        # When dumping output to file both \r and \n will be a new line
        # To avoid this "extra new-line" we only use \n at the end

        test_error = htrun_failure_line.search(decoded_line)
        if test_error:
            gt_logger.gt_log_err(test_error.group(1))

        if verbose:
            output = decoded_line.rstrip() + "\n"
            try:
                # Try to output decoded unicode. Should be fine in most Python 3
                # environments.
                sys.stdout.write(output)
            except UnicodeEncodeError:
                try:
                    # Try to encode to unicode bytes and let the terminal handle
                    # the decoding. Some Python 2 and OS combinations handle this
                    # gracefully.
                    sys.stdout.write(output.encode("utf-8"))
                except TypeError:
                    # Fallback to printing just ascii characters
                    sys.stdout.write(output.encode("ascii", "replace").decode("ascii"))
            sys.stdout.flush()

    # Check if process was terminated by signal
    returncode = p.wait()
    return returncode, htrun_output


def get_testcase_count_and_names(output):
    """Fetch events from log with test case count and test case names.

    Example test case count + names prints
    [1467197417.34][HTST][INF] host test detected: default_auto
    [1467197417.36][CONN][RXD] {{__testcase_count;2}}
    [...] found KV pair in stream: {{__testcase_count;2}}, queued...
    [1467197417.39][CONN][RXD] >>> Running 2 test cases...
    [1467197417.43][CONN][RXD] {{__testcase_name;C strings: strtok}}
    [...] found KV pair in stream: {{__testcase_name;C strings: strtok}}, queued...
    [1467197417.47][CONN][RXD] {{__testcase_name;C strings: strpbrk}}
    [...] found KV pair in stream: {{__testcase_name;C strings: strpbrk}}, queued...
    [1467197417.52][CONN][RXD] >>> Running case #1: 'C strings: strtok'...
    [1467197417.56][CONN][RXD] {{__testcase_start;C strings: strtok}}
    [...] found KV pair in stream: {{__testcase_start;C strings: strtok}}, queued...

    Args:
        output: htrun output to extract count and names from.

    Returns:
        Tuple of test case count, list of test case names in order of appearance.
    """
    testcase_count = 0
    testcase_names = []

    re_tc_count = re.compile(
        r"^\[(\d+\.\d+)\]\[(\w+)\]\[(\w+)\].*\{\{(__testcase_count);(\d+)\}\}"
    )
    re_tc_names = re.compile(
        r"^\[(\d+\.\d+)\]\[(\w+)\]\[(\w+)\].*\{\{(__testcase_name);([^;]+)\}\}"
    )

    for line in output.splitlines():
        m = re_tc_names.search(line)
        if m:
            testcase_names.append(m.group(5))
            continue
        m = re_tc_count.search(line)
        if m:
            testcase_count = m.group(5)

    return (testcase_count, testcase_names)


def get_testcase_utest(output, test_case_name):
    """Fetch all prints for given utest test case.

    Example test case prints
    [1455553765.52][CONN][RXD] >>> Running case #1: 'Simple Test'...
    [1455553765.52][CONN][RXD] {{__testcase_start;Simple Test}}
    [...] found KV pair in stream: {{__testcase_start;Simple Test}}, queued...
    [1455553765.58][CONN][RXD] Simple test called
    [1455553765.58][CONN][RXD] {{__testcase_finish;Simple Test;1;0}}
    [...] found KV pair in stream: {{__testcase_finish;Simple Test;1;0}}, queued...
    [1455553765.70][CONN][RXD] >>> 'Simple Test': 1 passed, 0 failed

    Args:
        output: htrun output to extract from.
        test_case_name: Name of the test case to search for.

    Returns:
        List of lines in log between start and end prints for test case.
    """
    # Return string with all non-alphanumerics backslashed;
    # this is useful if you want to match an arbitrary literal
    # string that may have regular expression metacharacters in it.
    escaped_test_case_name = re.escape(test_case_name)

    re_tc_utest_log_start = re.compile(
        r"^\[(\d+\.\d+)\]\[(\w+)\]\[(\w+)\] >>> Running case #(\d)+: '(%s)'"
        % escaped_test_case_name
    )
    re_tc_utest_log_finish = re.compile(
        r"^\[(\d+\.\d+)\]\[(\w+)\]\[(\w+)\] >>> '(%s)': (\d+) passed, (\d+) failed"
        % escaped_test_case_name
    )

    tc_log_lines = []
    for line in output.splitlines():

        # utest test case start string search
        m = re_tc_utest_log_start.search(line)
        if m:
            tc_log_lines.append(line)
            continue

        # If utest test case end string found
        m = re_tc_utest_log_finish.search(line)
        if m:
            tc_log_lines.append(line)
            break

        # Continue adding utest log lines
        if tc_log_lines:
            tc_log_lines.append(line)

    return tc_log_lines


def get_coverage_data(build_path, output):
    r"""Get gcov data from htrun output and write to file.

    Example GCOV output
    [1456840876.73][CONN][RXD] {{__coverage_start;c:\Work\core-util/source/
    PoolAllocator.cpp.gcda;6164636772393034c2733f32...a33e...b9}}

    Args:
        build_path: Path to build directory.
        output: htrun output to process.
    """
    gt_logger.gt_log("checking for GCOV data...")
    re_gcov = re.compile(
        r"^\[(\d+\.\d+)\][^\{]+\{\{(__coverage_start);([^;]+);([^}]+)\}\}$"
    )
    for line in output.splitlines():
        m = re_gcov.search(line)
        if m:
            _, _, gcov_path, gcov_payload = m.groups()
            try:
                bin_gcov_payload = coverage_pack_hex_payload(gcov_payload)
                coverage_dump_file(build_path, gcov_path, bin_gcov_payload)
            except Exception as e:
                gt_logger.gt_log_err("error while handling GCOV data: " + str(e))
            gt_logger.gt_log_tab(
                "storing %d bytes in '%s'" % (len(bin_gcov_payload), gcov_path)
            )


def get_printable_string(unprintable_string):
    """Remove unprintable characters from a string.

    Args:
        unprintable_string: String to process.

    Returns:
        String with unprintable characters removed.
    """
    return "".join(filter(lambda x: x in string.printable, unprintable_string))


def get_testcase_summary(output):
    """Parse test case summary.

    Example string to parse:
    [...][CONN][INF] found KV pair in stream: {{__testcase_summary;7;1}}, queued...

    Args:
        output: htrun output to process.

    Returns:
        Tuple of passed and failed counts, None if no summary found.
    """
    re_tc_summary = re.compile(
        r"^\[(\d+\.\d+)\][^\{]+\{\{(__testcase_summary);(\d+);(\d+)\}\}"
    )
    for line in output.splitlines():
        m = re_tc_summary.search(line)
        if m:
            _, _, passes, failures = m.groups()
            return int(passes), int(failures)
    return None


def get_testcase_result(output):
    """Parse test case results.

    Args:
        output: htrun output to process.

    Return:
        Dictionary containing test case results.
    """
    result_test_cases = {}  # Test cases results
    re_tc_start = re.compile(r"^\[(\d+\.\d+)\][^\{]+\{\{(__testcase_start);([^;]+)\}\}")
    re_tc_finish = re.compile(
        r"^\[(\d+\.\d+)\][^\{]+\{\{(__testcase_finish);([^;]+);(\d+);(\d+)\}\}"
    )
    for line in output.splitlines():
        m = re_tc_start.search(line)
        if m:
            timestamp, _, testcase_id = m.groups()
            if testcase_id not in result_test_cases:
                result_test_cases[testcase_id] = {}

            # Data collected when __testcase_start is fetched
            result_test_cases[testcase_id]["time_start"] = float(timestamp)
            result_test_cases[testcase_id]["utest_log"] = get_testcase_utest(
                output, testcase_id
            )

            # Data collected when __testcase_finish is fetched
            result_test_cases[testcase_id]["duration"] = 0.0
            result_test_cases[testcase_id]["result_text"] = "ERROR"
            result_test_cases[testcase_id]["time_end"] = float(timestamp)
            result_test_cases[testcase_id]["passed"] = 0
            result_test_cases[testcase_id]["failed"] = 0
            result_test_cases[testcase_id]["result"] = -4096
            continue

        m = re_tc_finish.search(line)
        if m:
            timestamp, _, testcase_id, testcase_passed, testcase_failed = m.groups()

            testcase_passed = int(testcase_passed)
            testcase_failed = int(testcase_failed)

            testcase_result = 0  # OK case
            if testcase_failed != 0:
                testcase_result = testcase_failed  # testcase_result > 0 is FAILure

            if testcase_id not in result_test_cases:
                result_test_cases[testcase_id] = {}
            # Setting some info about test case itself
            result_test_cases[testcase_id]["duration"] = 0.0
            result_test_cases[testcase_id]["result_text"] = "OK"
            result_test_cases[testcase_id]["time_end"] = float(timestamp)
            result_test_cases[testcase_id]["passed"] = testcase_passed
            result_test_cases[testcase_id]["failed"] = testcase_failed
            result_test_cases[testcase_id]["result"] = testcase_result
            # Assign human readable test case result
            if testcase_result > 0:
                result_test_cases[testcase_id]["result_text"] = "FAIL"
            elif testcase_result < 0:
                result_test_cases[testcase_id]["result_text"] = "ERROR"

            if "time_start" in result_test_cases[testcase_id]:
                result_test_cases[testcase_id]["duration"] = (
                    result_test_cases[testcase_id]["time_end"]
                    - result_test_cases[testcase_id]["time_start"]
                )
            else:
                result_test_cases[testcase_id]["duration"] = 0.0

            if "utest_log" not in result_test_cases[testcase_id]:
                result_test_cases[testcase_id][
                    "utest_log"
                ] = "__testcase_start tag not found."

    # Adding missing test cases which were defined with __testcase_name
    # Get test case names reported by utest + test case names
    # This data will be used to process all tests which were not executed
    # do their status can be set to SKIPPED (e.g. in JUnit)
    tc_count, tc_names = get_testcase_count_and_names(output)
    for testcase_id in tc_names:
        if testcase_id not in result_test_cases:
            result_test_cases[testcase_id] = {}
            # Data collected when __testcase_start is fetched
            result_test_cases[testcase_id]["time_start"] = 0.0
            result_test_cases[testcase_id]["utest_log"] = []
            # Data collected when __testcase_finish is fetched
            result_test_cases[testcase_id]["duration"] = 0.0
            result_test_cases[testcase_id]["result_text"] = "SKIPPED"
            result_test_cases[testcase_id]["time_end"] = 0.0
            result_test_cases[testcase_id]["passed"] = 0
            result_test_cases[testcase_id]["failed"] = 0
            result_test_cases[testcase_id]["result"] = -8192

    return result_test_cases


def get_memory_metrics(output):
    """Parse for test case memory metrics.

    Example string to parse:
    [...][CONN][INF] found KV pair in stream: {{max_heap_usage;2284}}, queued...

    Args:
        output: htrun output to parse.

    Returns:
        Tuple of max heap usage and list of dicts: {entry, arg, max_stack, stack_size}.
    """
    max_heap_usage = None
    reserved_heap = None
    thread_info = {}
    re_tc_max_heap_usage = re.compile(
        r"^\[(\d+\.\d+)\][^\{]+\{\{(max_heap_usage);(\d+)\}\}"
    )
    re_tc_reserved_heap = re.compile(
        r"^\[(\d+\.\d+)\][^\{]+\{\{(reserved_heap);(\d+)\}\}"
    )
    re_tc_thread_info = re.compile(
        r"^\[(\d+\.\d+)\][^\{]+\{\{(__thread_info);\""
        r"([A-Fa-f0-9\-xX]+)\",(\d+),(\d+)\}\}"
    )
    for line in output.splitlines():
        m = re_tc_max_heap_usage.search(line)
        if m:
            _, _, max_heap_usage = m.groups()
            max_heap_usage = int(max_heap_usage)

        m = re_tc_reserved_heap.search(line)
        if m:
            _, _, reserved_heap = m.groups()
            reserved_heap = int(reserved_heap)

        m = re_tc_thread_info.search(line)
        if m:
            _, _, thread_entry_arg, thread_max_stack, thread_stack_size = m.groups()
            thread_max_stack = int(thread_max_stack)
            thread_stack_size = int(thread_stack_size)
            thread_entry_arg_split = thread_entry_arg.split("-")
            thread_entry = thread_entry_arg_split[0]

            thread_info[thread_entry_arg] = {
                "entry": thread_entry,
                "max_stack": thread_max_stack,
                "stack_size": thread_stack_size,
            }

            if len(thread_entry_arg_split) > 1:
                thread_arg = thread_entry_arg_split[1]
                thread_info[thread_entry_arg]["arg"] = thread_arg

    thread_info_list = list(thread_info.values())

    return max_heap_usage, reserved_heap, thread_info_list


def get_thread_stack_info_summary(thread_stack_info):
    """Get thread stack size summary.

    Args:
        thread_stack_info: List of stack info to search through.

    Returns:
        Stack info summary dictionary.
    """
    max_thread_stack_size = 0
    max_thread = None
    max_stack_usage_total = 0
    reserved_stack_total = 0
    for cur_thread_stack_info in thread_stack_info:
        if cur_thread_stack_info["stack_size"] > max_thread_stack_size:
            max_thread_stack_size = cur_thread_stack_info["stack_size"]
            max_thread = cur_thread_stack_info
        max_stack_usage_total += cur_thread_stack_info["max_stack"]
        reserved_stack_total += cur_thread_stack_info["stack_size"]
    summary = {
        "max_stack_size": max_thread["stack_size"],
        "max_stack_usage": max_thread["max_stack"],
        "max_stack_usage_total": max_stack_usage_total,
        "reserved_stack_total": reserved_stack_total,
    }
    return summary


def log_devices_in_table(
    duts,
    cols=[
        "platform_name",
        "platform_name_unique",
        "serial_port",
        "mount_point",
        "target_id",
    ],
):
    """Print table of DUTs using prettytable.

    Args:
        muts: List of MUTs to print in table.
        cols: Columns used to for a table, required for each DUT.

    Returns:
        String with formatted prettytable.
    """
    from prettytable import PrettyTable, HEADER

    pt = PrettyTable(cols, junction_char="|", hrules=HEADER)
    for col in cols:
        pt.align[col] = "l"
    pt.padding_width = 1  # One space between column edges and contents (default)
    row = []
    for dut in duts:
        for col in cols:
            cell_val = dut[col] if col in dut else "not detected"
            row.append(cell_val)
        pt.add_row(row)
        row = []
    return pt.get_string()


def get_test_spec(opts):
    """Closure encapsulating how we get test specification and load it from file.

    Returns:
        Tuple (test specification, ret code), Test specification == None if load fails.
    """
    test_spec = None

    test_spec_file_name = opts.test_spec
    test_spec_file_name_list = []

    def get_all_test_specs_from_build_dir(path_to_scan):
        """Search for all test_spec.json files.

        Args:
            path_to_scan: Directory path used to recursively search for test_spec.json.

        Returns:
            List of locations of test_spec.json.
        """
        return [
            os.path.join(dp, f)
            for dp, dn, filenames in os.walk(path_to_scan)
            for f in filenames
            if f == "test_spec.json"
        ]

    def merge_multiple_test_specifications_from_file_list(test_spec_file_name_list):
        """Merge all test specifications into one.

        Args:
            test_spec_file_name_list: List of paths to test specifications.

        Returns:
            TestSpec object with all test specification data inside
        """

        def copy_builds_between_test_specs(source, destination):
            """Copy build key-value pairs between two test_spec dicts.

            Args:
                source: Source dictionary.
                destination: Dictionary which will be updated from source.

            Returns:
                Dictionary with merged source.
            """
            result = destination.copy()
            if "builds" in source and "builds" in destination:
                for k in source["builds"]:
                    result["builds"][k] = source["builds"][k]
            return result

        merged_test_spec = {}
        for test_spec_file in test_spec_file_name_list:
            gt_logger.gt_log_tab("using '%s'" % test_spec_file)
            try:
                with open(test_spec_file, "r") as f:
                    test_spec_data = json.load(f)
                    merged_test_spec = copy_builds_between_test_specs(
                        merged_test_spec, test_spec_data
                    )
            except Exception as e:
                gt_logger.gt_log_err(
                    "Unexpected error while processing '%s' test specification file"
                    % test_spec_file
                )
                gt_logger.gt_log_tab(str(e))
                merged_test_spec = {}

        test_spec = TestSpec()
        test_spec.parse(merged_test_spec)
        return test_spec

    # Test specification look-up
    if opts.test_spec:
        # Loading test specification from command line specified file
        gt_logger.gt_log(
            "test specification file '%s' (specified with --test-spec option)"
            % opts.test_spec
        )
    elif os.path.exists("test_spec.json"):
        # Test specification file exists in current directory
        gt_logger.gt_log("using 'test_spec.json' from current directory!")
        test_spec_file_name = "test_spec.json"
    elif "BUILD" in os.listdir(os.getcwd()):
        # Checking 'BUILD' directory for test specifications
        # Using `os.listdir()` since it preserves case
        test_spec_file_name_list = get_all_test_specs_from_build_dir("BUILD")
    elif os.path.exists(".build"):
        # Checking .build directory for test specifications
        test_spec_file_name_list = get_all_test_specs_from_build_dir(".build")
    elif os.path.exists("mbed-os") and "BUILD" in os.listdir("mbed-os"):
        # Checking mbed-os/.build directory for test specifications
        # Using `os.listdir()` since it preserves case
        test_spec_file_name_list = get_all_test_specs_from_build_dir(
            os.path.join(["mbed-os", "BUILD"])
        )
    elif os.path.exists(os.path.join("mbed-os", ".build")):
        # Checking mbed-os/.build directory for test specifications
        test_spec_file_name_list = get_all_test_specs_from_build_dir(
            os.path.join(["mbed-os", ".build"])
        )

    # Actual load and processing of test specification from sources
    if test_spec_file_name:
        # Test specification from command line (--test-spec) or default test_spec.json
        gt_logger.gt_log("using '%s' from current directory!" % test_spec_file_name)
        test_spec = TestSpec(test_spec_file_name)
        if opts.list_binaries:
            list_binaries_for_builds(test_spec)
            return None, 0
    elif test_spec_file_name_list:
        # Merge multiple test specs into one and keep calm
        gt_logger.gt_log("using multiple test specifications from current directory!")
        test_spec = merge_multiple_test_specifications_from_file_list(
            test_spec_file_name_list
        )
        if opts.list_binaries:
            list_binaries_for_builds(test_spec)
            return None, 0
    else:
        gt_logger.gt_log_err(
            "No test spec found. Use --test-spec to explicitly select a test spec."
        )
        return None, -1
    return test_spec, 0


def get_test_build_properties(test_spec, test_build_name):
    """Get properties of a test_build.

    Args:
        test_spec: Test specification to get the test build from.
        test_build_name: Name of the test build to get.

    Returns:
        Dictionary with name, toolchain, and target, or None.
    """
    result = dict()
    test_builds = test_spec.get_test_builds(filter_by_names=[test_build_name])
    if test_builds:
        test_build = test_builds[0]
        result["name"] = test_build.get_name()
        result["toolchain"] = test_build.get_toolchain()
        result["target"] = test_build.get_platform()
        return result
    else:
        return None


def parse_global_resource_mgr(global_resource_mgr):
    """Parse --grm switch with global resource manager info.

    Args:
        global_resource_mgr: Input GRM such as K64F:module_name:10.2.123.43:3334.

    Returns:
        Tuple of GRM elements, or None.
    """
    try:
        platform_name, module_name, leftover = global_resource_mgr.split(":", 2)
        parts = leftover.rsplit(":", 1)

        try:
            ip_name, port_name = parts
            int(port_name)
        except ValueError:
            # No valid port was found, so assume no port was supplied
            ip_name = leftover
            port_name = None

    except ValueError:
        return None
    return platform_name, module_name, ip_name, port_name


def parse_fast_model_connection(fast_model_connection):
    """Parse --fm switch with simulator resource manager info.

    Args:
        fast_model_connection: FM info, such as FVP_MPS2_M3:DEFAULT.

    Returns:
        Tuple of platform name and config name, or None.
    """
    try:
        platform_name, config_name = fast_model_connection.split(":")
    except ValueError:
        return None
    return platform_name, config_name
