#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Default host test."""

from .. import BaseHostTest


class DefaultAuto(BaseHostTest):
    """Waits for serial port output from the DUT.

    Only recognises the test completion message from greentea-client.
    """

    pass
