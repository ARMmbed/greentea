#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Auto detection host test."""

import re
from .. import BaseHostTest


class DetectPlatformTest(BaseHostTest):
    """Test to auto detect the platform."""

    PATTERN_MICRO_NAME = r"Target '(\w+)'"
    re_detect_micro_name = re.compile(PATTERN_MICRO_NAME)

    def result(self):
        """Not implemented."""
        raise NotImplementedError

    def test(self, selftest):
        """Run test."""
        result = True

        c = selftest.mbed.serial_readline()  # {{start}} preamble
        if c is None:
            return selftest.RESULT_IO_SERIAL

        selftest.notify(c.strip())
        selftest.notify("HOST: Detecting target name...")

        c = selftest.mbed.serial_readline()
        if c is None:
            return selftest.RESULT_IO_SERIAL
        selftest.notify(c.strip())

        # Check for target name
        m = self.re_detect_micro_name.search(c)
        if m and len(m.groups()):
            micro_name = m.groups()[0]
            micro_cmp = selftest.mbed.options.micro == micro_name
            result = result and micro_cmp
            selftest.notify(
                "HOST: MUT Target name '%s', expected '%s'... [%s]"
                % (
                    micro_name,
                    selftest.mbed.options.micro,
                    "OK" if micro_cmp else "FAIL",
                )
            )

        for i in range(0, 2):
            c = selftest.mbed.serial_readline()
            if c is None:
                return selftest.RESULT_IO_SERIAL
            selftest.notify(c.strip())

        return selftest.RESULT_SUCCESS if result else selftest.RESULT_FAILURE
