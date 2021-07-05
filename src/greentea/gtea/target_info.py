#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Information about target properties."""
import os
import json

TARGET_DEFAULT_PROPERTIES = {
    "program_cycle_s": 4,
    "binary_type": ".bin",
    "copy_method": "default",
    "reset_method": "default",
}


def get_platform_property(platform, property):
    """Get value of a property for a platform.

    Args:
        platform: Name of the platform.
        property: Name of the property.

    Returns:
        Property value, None if property not found.
    """
    from_targets_json = _get_platform_property_from_targets(platform, property)
    if from_targets_json:
        return from_targets_json
    return _get_platform_property_from_default(property)


def _get_platform_property_from_default(property):
    return TARGET_DEFAULT_PROPERTIES.get(property)


def _platform_property_from_targets_json(targets, platform, property):
    """Get platform property from targets.json, accounting for target inheritance.

    Args:
        targets: Data structure from targets.json.
        platform: Name of the platform.
        property: Name of the property.
    Returns:
        Property value, None if not found.

    """
    if platform not in targets:
        return None
    result = targets[platform].get(property)
    if result:
        return result
    for inherited_target in targets[platform].get("inherits", []):
        result = _platform_property_from_targets_json(
            targets, inherited_target, property
        )
        if result:
            return result
    return None


IGNORED_DIRS = [".build", "BUILD", "tools"]


def _find_targets_json(path):
    for root, dirs, files in os.walk(path, followlinks=True):
        for ignored_dir in IGNORED_DIRS:
            if ignored_dir in dirs:
                dirs.remove(ignored_dir)
        if "targets.json" in files:
            yield os.path.join(root, "targets.json")


def _get_platform_property_from_targets(platform, property):
    """Load properties from targets.json file somewhere in the project structure.

    Args:
        platform: Target to find the property for in targets.json.
        property: Property to extract the value of.

    Returns:
        Property value, or None if platform or property not found.
    """
    for targets_path in _find_targets_json(os.getcwd()):
        try:
            with open(targets_path, "r") as f:
                targets = json.load(f)
                result = _platform_property_from_targets_json(
                    targets, platform, property
                )
                if result:
                    return result
        except (IOError, ValueError):
            pass
    return None
