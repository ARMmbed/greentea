#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Greentea Host Tests Runner."""

from multiprocessing import freeze_support
from htrun import init_host_test_cli_params
from htrun.host_tests_runner.host_test_default import DefaultTestSelector
from htrun.host_tests_toolbox.host_functional import handle_send_break_cmd


def main():
    """Drive command line tool 'htrun' which is using DefaultTestSelector.

    1. Create DefaultTestSelector object and pass command line parameters.
    2. Call default test execution function run() to start test instrumentation.
    """
    freeze_support()
    result = 0
    cli_params = init_host_test_cli_params()

    if cli_params.version:  # --version
        import pkg_resources  # part of setuptools

        version = pkg_resources.require("htrun")[0].version
        print(version)
    elif cli_params.send_break_cmd:  # -b with -p PORT (and optional -r RESET_TYPE)
        handle_send_break_cmd(
            port=cli_params.port,
            disk=cli_params.disk,
            reset_type=cli_params.forced_reset_type,
            baudrate=cli_params.baud_rate,
            verbose=cli_params.verbose,
        )
    else:
        test_selector = DefaultTestSelector(cli_params)
        try:
            result = test_selector.execute()
            # Ensure we don't return a negative value
            if result < 0 or result > 255:
                result = 1
        except (KeyboardInterrupt, SystemExit):
            test_selector.finish()
            result = 1
            raise
        else:
            test_selector.finish()

    return result
