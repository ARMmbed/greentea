#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import re
import json

from os import walk
from contextlib import suppress

from .common_api import run_cli_process
from .greentea_log import gt_logger


## Information about some properties of targets (platforms)
#
#  "default" entry is used to fetch "global" properties if they are not
#  specified with each platform
#

TARGET_INFO_MAPPING = {
    "default": {
        "program_cycle_s": 4,
        "binary_type": ".bin",
        "copy_method": "default",
        "reset_method": "default",
    },
    "K64F": {
        "yotta_targets": [
            {"yotta_target": "frdm-k64f-gcc", "mbed_toolchain": "GCC_ARM"},
            {"yotta_target": "frdm-k64f-armcc", "mbed_toolchain": "ARM"},
        ],
        "properties": {
            "binary_type": ".bin",
            "copy_method": "default",
            "reset_method": "default",
            "program_cycle_s": 4,
        },
    },
    "RAPIDIOT_K64F": {"properties": {"forced_reset_timeout": 7}},
    "NUCLEO_F401RE": {
        "yotta_targets": [
            {"yotta_target": "st-nucleo-f401re-gcc", "mbed_toolchain": "GCC_ARM"}
        ],
        "properties": {
            "binary_type": ".bin",
            "copy_method": "cp",
            "reset_method": "default",
            "program_cycle_s": 4,
        },
    },
    "NRF51_DK": {
        "yotta_targets": [
            {"yotta_target": "nrf51dk-gcc", "mbed_toolchain": "GCC_ARM"},
            {"yotta_target": "nrf51dk-armcc", "mbed_toolchain": "ARM"},
        ],
        "properties": {
            "binary_type": "-combined.hex",
            "copy_method": "shell",
            "reset_method": "default",
            "program_cycle_s": 4,
        },
    },
    "NRF51822": {
        "yotta_targets": [
            {"yotta_target": "mkit-gcc", "mbed_toolchain": "GCC_ARM"},
            {"yotta_target": "mkit-armcc", "mbed_toolchain": "ARM"},
        ],
        "properties": {
            "binary_type": "-combined.hex",
            "copy_method": "shell",
            "reset_method": "default",
            "program_cycle_s": 4,
        },
    },
    "ARCH_BLE": {
        "yotta_targets": [{"yotta_target": "tinyble-gcc", "mbed_toolchain": "GCC_ARM"}],
        "properties": {
            "binary_type": "-combined.hex",
            "copy_method": "shell",
            "reset_method": "default",
            "program_cycle_s": 4,
        },
    },
}

TARGET_TOOLCAHINS = {
    "-armcc": "ARM",
    "-gcc": "GCC_ARM",
    "-iar": "IAR",
}


def parse_mbed_target_from_target_json(mbed_classic_name, target_json_data):
    if (
        not target_json_data
        or "keywords" not in target_json_data
        or "name" not in target_json_data
    ):
        return None

    for keyword in target_json_data["keywords"]:
        target, _, name = keyword.partition(":")
        if target == "mbed-target" and name.lower() == mbed_classic_name.lower():
            return target_json_data["name"]

    return None


def get_binary_type_for_platform(platform):
    """
    Gives binary type for the given platform.

    :param platform:
    :return:
    """
    # return TARGET_INFO_MAPPING[platform]['properties']["binary_type"]
    return get_platform_property(platform, "binary_type")


def get_platform_property(platform, property):
    """
    Gives platform property.

    :param platform:
    :return: property value, None if property not found
    """

    default = _get_platform_property_from_default(property)
    from_targets_json = _get_platform_property_from_targets(platform, property, default)
    if from_targets_json:
        return from_targets_json
    from_info_mapping = _get_platform_property_from_info_mapping(platform, property)
    if from_info_mapping:
        return from_info_mapping
    return default


def _get_platform_property_from_default(property):
    with suppress(KeyError):
        return TARGET_INFO_MAPPING["default"][property]


def _get_platform_property_from_info_mapping(platform, property):
    with suppress(KeyError):
        return TARGET_INFO_MAPPING[platform]["properties"][property]


def _platform_property_from_targets_json(targets, platform, property, default):
    """! Get a platforms's property from the target data structure in
            targets.json. Takes into account target inheritance.
    @param targets Data structure parsed from targets.json
    @param platform Name of the platform
    @param property Name of the property
    @param default the fallback value if none is found, but the target exists
    @return property value, None if property not found

    """
    with suppress(KeyError):
        return targets[platform][property]
    with suppress(KeyError):
        for inherited_target in targets[platform]["inherits"]:
            result = _platform_property_from_targets_json(
                targets, inherited_target, property, None
            )
            if result:
                return result
    if platform in targets:
        return default


IGNORED_DIRS = [".build", "BUILD", "tools"]


def _find_targets_json(path):
    for root, dirs, files in walk(path, followlinks=True):
        for ignored_dir in IGNORED_DIRS:
            if ignored_dir in dirs:
                dirs.remove(ignored_dir)
        if "targets.json" in files:
            yield os.path.join(root, "targets.json")


def _get_platform_property_from_targets(platform, property, default):
    """
    Load properties from targets.json file somewhere in the project structure

    :param platform:
    :return: property value, None if property not found
    """
    for targets_path in _find_targets_json(os.getcwd()):
        with suppress(IOError, ValueError):
            with open(targets_path, "r") as f:
                targets = json.load(f)
                result = _platform_property_from_targets_json(
                    targets, platform, property, default
                )
                if result:
                    return result
