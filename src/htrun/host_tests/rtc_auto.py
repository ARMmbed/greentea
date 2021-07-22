#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""RTC auto test."""

import re
from time import strftime, gmtime
from .. import BaseHostTest


class RTCTest(BaseHostTest):
    """Test RTC."""

    PATTERN_RTC_VALUE = r"\[(\d+)\] \[(\d+-\d+-\d+ \d+:\d+:\d+ [AaPpMm]{2})\]"
    re_detect_rtc_value = re.compile(PATTERN_RTC_VALUE)

    __result = None
    timestamp = None
    rtc_reads = []

    def _callback_timestamp(self, key, value, timestamp):
        self.timestamp = int(value)

    def _callback_rtc(self, key, value, timestamp):
        self.rtc_reads.append((key, value, timestamp))

    def _callback_end(self, key, value, timestamp):
        self.notify_complete()

    def setup(self):
        """Set up the test."""
        self.register_callback("timestamp", self._callback_timestamp)
        self.register_callback("rtc", self._callback_rtc)
        self.register_callback("end", self._callback_end)

    def result(self):
        """Report test result."""

        def check_strftimes_format(t):
            m = self.re_detect_rtc_value.search(t)
            if m and len(m.groups()):
                sec, time_str = int(m.groups()[0]), m.groups()[1]
                correct_time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime(float(sec)))
                return time_str == correct_time_str
            return False

        ts = [t for _, t, _ in self.rtc_reads]
        self.__result = all(filter(check_strftimes_format, ts))
        return self.__result

    def teardown(self):
        """Tear down the test."""
        pass
