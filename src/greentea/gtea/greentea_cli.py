#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Functions used by Greentea CLI."""
import os
import fnmatch

from .tests_spec import list_binaries_for_builds
from .greentea_log import gt_logger

RET_NO_DEVICES = 1001
LOCAL_HOST_TESTS_DIR = "./test/host_tests"  # Used by htrun -e <dir>


def get_local_host_tests_dir(path):
    """Create path to local host tests.

    Args:
        path: Path to check if local host test directory.

    Returns:
        path if exists and is dir, else default if exists and is dir, else None.
    """
    if path and os.path.exists(path) and os.path.isdir(path):
        return path
    if (
        not path
        and os.path.exists(LOCAL_HOST_TESTS_DIR)
        and os.path.isdir(LOCAL_HOST_TESTS_DIR)
    ):
        return LOCAL_HOST_TESTS_DIR
    return None


def create_filtered_test_list(test_list, test_by_names, skip_test, test_spec):
    """Create a filtered test case list.

    Args:
        test_list: List of tests, derived from test specification.
        test_by_names: Comma-separated string of names of tests to run.
        skip_test: Comma-separated string of names of tests to skip.
        test_spec: Test specification object loaded with --test-spec switch.

    Returns:
        Filtered test case list.
    """
    filtered_test_list = test_list
    test_name_list = None
    invalid_test_names = []
    if filtered_test_list is None:
        return {}

    if test_by_names:
        filtered_test_list = {}  # Subset of 'test_list'
        test_name_list = test_by_names.lower().split(",")
        gt_logger.gt_log("test case filter (specified with -n option)")

        for test_name in set(test_name_list):
            gt_logger.gt_log_tab(test_name)
            matches = [
                test for test in test_list.keys() if fnmatch.fnmatch(test, test_name)
            ]
            if matches:
                for match in matches:
                    gt_logger.gt_log_tab(
                        "test filtered in '%s'" % gt_logger.gt_bright(match)
                    )
                    filtered_test_list[match] = test_list[match]
            else:
                invalid_test_names.append(test_name)

    if skip_test:
        test_name_list = skip_test.split(",")
        gt_logger.gt_log("test case filter (specified with -i option)")

        for test_name in set(test_name_list):
            gt_logger.gt_log_tab(test_name)
            matches = [
                test
                for test in filtered_test_list.keys()
                if fnmatch.fnmatch(test, test_name)
            ]
            if matches:
                for match in matches:
                    gt_logger.gt_log_tab(
                        "test filtered out '%s'" % gt_logger.gt_bright(match)
                    )
                    del filtered_test_list[match]
            else:
                invalid_test_names.append(test_name)

    if invalid_test_names:
        opt_to_print = "-n" if test_by_names else "skip-test"
        gt_logger.gt_log_warn(
            "invalid test case names (specified with '%s' option)" % opt_to_print
        )
        for test_name in invalid_test_names:
            test_spec_name = test_spec.test_spec_filename
            gt_logger.gt_log_warn(
                "test name '%s' not found in '%s' "
                "(specified with --test-spec option)"
                % (
                    gt_logger.gt_bright(test_name),
                    gt_logger.gt_bright(test_spec_name),
                )
            )
        gt_logger.gt_log_tab("note: test case names are case sensitive")
        gt_logger.gt_log_tab("note: see list of available test cases below")
        # Print available test suite names (binary names user can use with -n
        list_binaries_for_builds(test_spec)
    return filtered_test_list
