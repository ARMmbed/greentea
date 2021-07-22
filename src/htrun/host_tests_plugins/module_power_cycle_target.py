#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Power cycle devices using the 'Mbed TAS RM REST API'."""

import os
import json
import time
import requests
from .host_test_plugins import HostTestPluginBase


class HostTestPluginPowerCycleResetMethod(HostTestPluginBase):
    """Plugin interface adaptor for Mbed TAS RM REST API."""

    name = "HostTestPluginPowerCycleResetMethod"
    type = "ResetMethod"
    stable = True
    capabilities = ["power_cycle"]
    required_parameters = ["target_id", "device_info"]

    def __init__(self):
        """Initialise plugin."""
        HostTestPluginBase.__init__(self)

    def setup(self, *args, **kwargs):
        """Configure plugin.

        This function should be called before plugin execute() method is used.
        """
        return True

    def execute(self, capability, *args, **kwargs):
        """Power cycle a device using the TAS RM API.

        If the "capability" name is not "power_cycle" this method will just fail.

        Args:
            capability: Capability name.
            args: Additional arguments.
            kwargs: Additional arguments.

        Returns:
            True if the power cycle succeeded, otherwise False.
        """
        if "target_id" not in kwargs or not kwargs["target_id"]:
            self.print_plugin_error("Error: This plugin requires unique target_id")
            return False

        if "device_info" not in kwargs or type(kwargs["device_info"]) is not dict:
            self.print_plugin_error(
                "Error: This plugin requires dict parameter 'device_info' passed by "
                "the caller."
            )
            return False

        result = False
        if self.check_parameters(capability, *args, **kwargs) is True:
            if capability in HostTestPluginPowerCycleResetMethod.capabilities:
                target_id = kwargs["target_id"]
                device_info = kwargs["device_info"]
                ret = self.__get_mbed_tas_rm_addr()
                if ret:
                    ip, port = ret
                    result = self.__hw_reset(ip, port, target_id, device_info)
        return result

    def __get_mbed_tas_rm_addr(self):
        """Get IP and Port of mbed tas rm service."""
        try:
            ip = os.environ["MBED_TAS_RM_IP"]
            port = os.environ["MBED_TAS_RM_PORT"]
            return ip, port
        except KeyError as e:
            self.print_plugin_error(
                "HOST: Failed to read environment variable ("
                + str(e)
                + "). Can't perform hardware reset."
            )

        return None

    def __hw_reset(self, ip, port, target_id, device_info):
        """Reset target device using TAS RM API."""
        switch_off_req = {
            "name": "switchResource",
            "sub_requests": [
                {
                    "resource_type": "mbed_platform",
                    "resource_id": target_id,
                    "switch_command": "OFF",
                }
            ],
        }

        switch_on_req = {
            "name": "switchResource",
            "sub_requests": [
                {
                    "resource_type": "mbed_platform",
                    "resource_id": target_id,
                    "switch_command": "ON",
                }
            ],
        }

        result = False

        # reset target
        switch_off_req = self.__run_request(ip, port, switch_off_req)
        if switch_off_req is None:
            self.print_plugin_error("HOST: Failed to communicate with TAS RM!")
            return result

        if "error" in switch_off_req["sub_requests"][0]:
            self.print_plugin_error(
                "HOST: Failed to reset target. error = %s"
                % switch_off_req["sub_requests"][0]["error"]
            )
            return result

        def poll_state(required_state):
            switch_state_req = {
                "name": "switchResource",
                "sub_requests": [
                    {
                        "resource_type": "mbed_platform",
                        "resource_id": target_id,
                        "switch_command": "STATE",
                    }
                ],
            }
            resp = self.__run_request(ip, port, switch_state_req)
            start = time.time()
            while (
                resp
                and (
                    resp["sub_requests"][0]["state"] != required_state
                    or (
                        required_state == "ON"
                        and resp["sub_requests"][0]["mount_point"] == "Not Connected"
                    )
                )
                and (time.time() - start) < 300
            ):
                time.sleep(2)
                resp = self.__run_request(ip, port, resp)
            return resp

        poll_state("OFF")

        self.__run_request(ip, port, switch_on_req)
        resp = poll_state("ON")
        if (
            resp
            and resp["sub_requests"][0]["state"] == "ON"
            and resp["sub_requests"][0]["mount_point"] != "Not Connected"
        ):
            for k, v in resp["sub_requests"][0].viewitems():
                device_info[k] = v
            result = True
        else:
            self.print_plugin_error("HOST: Failed to reset device %s" % target_id)

        return result

    @staticmethod
    def __run_request(ip, port, request):
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        get_resp = requests.get(
            "http://%s:%s/" % (ip, port), data=json.dumps(request), headers=headers
        )
        resp = get_resp.json()
        if get_resp.status_code == 200:
            return resp
        else:
            return None


def load_plugin():
    """Return plugin available in this module."""
    return HostTestPluginPowerCycleResetMethod()
