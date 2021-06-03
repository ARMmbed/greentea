#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest
from mock import patch

from mbed_os_tools.test.mbed_report_api import (
    exporter_html,
    exporter_memory_metrics_csv,
    exporter_testcase_junit,
    exporter_testcase_text,
    exporter_text,
    exporter_json,
)


class ReportEmitting(unittest.TestCase):

    report_fns = [
        exporter_html,
        exporter_memory_metrics_csv,
        exporter_testcase_junit,
        exporter_testcase_text,
        exporter_text,
        exporter_json,
    ]

    def test_report_zero_tests(self):
        test_data = {}
        for report_fn in self.report_fns:
            report_fn(test_data)

    def test_report_zero_testcases(self):
        test_data = {
            "k64f-gcc_arm": {
                "garbage_test_suite": {
                    u"single_test_result": u"NOT_RAN",
                    u"elapsed_time": 0.0,
                    u"build_path": u"N/A",
                    u"build_path_abs": u"N/A",
                    u"copy_method": u"N/A",
                    u"image_path": u"N/A",
                    u"single_test_output": u"\x80abc",
                    u"platform_name": u"k64f",
                    u"test_bin_name": u"N/A",
                    u"testcase_result": {},
                }
            }
        }
        for report_fn in self.report_fns:
            report_fn(test_data)
