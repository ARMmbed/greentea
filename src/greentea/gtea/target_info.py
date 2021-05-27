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
    """
    Gives platform property.

    :param platform:
    :return: property value, None if property not found
    """
    from_targets_json = _get_platform_property_from_targets(platform, property)
    if from_targets_json:
        return from_targets_json
    return _get_platform_property_from_default(property)


def _get_platform_property_from_default(property):
    return TARGET_DEFAULT_PROPERTIES.get(property)


def _platform_property_from_targets_json(targets, platform, property):
    """! Get a platforms's property from the target data structure in
            targets.json. Takes into account target inheritance.
    @param targets Data structure parsed from targets.json
    @param platform Name of the platform
    @param property Name of the property
    @return property value, None if property not found

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
    """
    Load properties from targets.json file somewhere in the project structure

    :param platform:
    :return: property value, None if property not found
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
