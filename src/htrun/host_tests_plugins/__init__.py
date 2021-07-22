#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""greentea-host-test-plugins package.

This package contains plugins used by host test to reset, flash devices etc.
This package can be extended with new packages to add more generic functionality.
"""

from . import host_test_registry

# This plugins provide 'flashing' and 'reset' methods to host test scripts
from . import module_copy_shell
from . import module_copy_to_target
from . import module_reset_target
from . import module_power_cycle_target
from . import module_copy_pyocd
from . import module_reset_pyocd

# Additional, non standard platforms
from . import module_copy_silabs
from . import module_reset_silabs
from . import module_copy_stlink
from . import module_reset_stlink
from . import module_copy_ublox
from . import module_reset_ublox
from . import module_reset_mps2
from . import module_copy_mps2

# import module_copy_jn51xx
# import module_reset_jn51xx


# Plugin registry instance
HOST_TEST_PLUGIN_REGISTRY = host_test_registry.HostTestRegistry()

# Static plugin registration
# Some plugins are commented out if they are not stable or not commonly used
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_to_target.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_shell.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_reset_target.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_pyocd.load_plugin())

# Extra platforms support
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_mps2.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_reset_mps2.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_silabs.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_reset_silabs.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_stlink.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_reset_stlink.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_power_cycle_target.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_reset_pyocd.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_reset_ublox.load_plugin())
HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_ublox.load_plugin())
# HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_copy_jn51xx.load_plugin())
# HOST_TEST_PLUGIN_REGISTRY.register_plugin(module_reset_jn51xx.load_plugin())

# TODO: extend plugin loading to files with name module_*.py loaded ad-hoc

###############################################################################
# Functional interface for host test plugin registry
###############################################################################


def call_plugin(type, capability, *args, **kwargs):
    """Call a plugin from the HOST_TEST_PLUGIN_REGISTRY.

    Args:
        capability: Plugin capability we want to call.
        args: Additional parameters passed to plugin.
        kwargs: Additional parameters passed to plugin.

    Returns:
        True if the call succeeded, otherwise False.
    """
    return HOST_TEST_PLUGIN_REGISTRY.call_plugin(type, capability, *args, **kwargs)


def get_plugin_caps(type):
    """Get a list of all capabilities for a plugin type.

    Args:
        type: Type of a plugin.

    Returns:
        List of all capabilities for plugin family with the same type. If there are no
        capabilities an empty list is returned.
    """
    return HOST_TEST_PLUGIN_REGISTRY.get_plugin_caps(type)


def get_plugin_info():
    """Get 'information' about the plugins currently in the registry.

    Returns:
        Dictionary of 'information' about the plugins in HOST_TEST_PLUGIN_REGISTRY.
    """
    return HOST_TEST_PLUGIN_REGISTRY.get_dict()


def print_plugin_info():
    """Print plugin information in a user friendly way."""
    print(HOST_TEST_PLUGIN_REGISTRY)
