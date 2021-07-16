#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""greentea-host-test-runner.

This package contains basic host test implementation with algorithms to flash
and reset devices. Functionality can be overridden by set of plugins which can
provide specialised flashing and reset implementations.
"""

from pkg_resources import get_distribution

__version__ = get_distribution("greentea-host").version
