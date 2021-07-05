#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#


from .. import BaseHostTest


class DefaultAuto(BaseHostTest):
    """Simple, basic host test's test runner waiting for serial port
    output from MUT, no supervision over test running in MUT is executed.
    """

    pass
