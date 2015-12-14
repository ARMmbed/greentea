"""
mbed SDK
Copyright (c) 2011-2015 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.wirkus@arm.com>
"""

import json
from mbed_greentea.mbed_greentea_log import gt_log
from mbed_greentea.mbed_greentea_log import gt_bright
from mbed_greentea.mbed_greentea_log import gt_log_tab
from mbed_greentea.mbed_greentea_log import gt_log_err
from mbed_greentea.mbed_test_api import run_cli_command

"""
List of available hooks:
* hook_test_end - executed when test is completed
* hook_all_test_end - executed when all tests are completed
"""


class GreenteaTestHook():
    """! Class used to define
    """
    name = None

    def __init__(self, name, ):
        pass

    def run(self, format=None):
        pass

class GreenteaCliTestHook(GreenteaTestHook):
    """! Class used to define a hook which will call command line program
    """
    cmd = None

    def __init__(self, name, cmd):
        GreenteaTestHook.__init__(self, name)
        self.cmd = cmd

    def run(self, format=None):
        """! Runs hook
        @param format Used to format string with cmd, notation used is e.g: {build_name}
        """
        cmd = self.cmd
        if format:
            cmd = self.cmd.format(**format)

        return run_cli_command(cmd, shell=False)

class GreenteaHooks():
    """! Class used to store all hooks
    @details Hooks command starts with '$' dollar sign
    """
    HOOKS = {}
    def __init__(self, path_to_hooks):
        """! Opens JSON file with
        """
        try:
            with open(path_to_hooks, 'r') as data_file:
                hooks = json.load(data_file)
                if 'hooks' in hooks:
                    for hook in hooks['hooks']:
                        hook_name = hook
                        hook_expression = hooks['hooks'][hook]
                        # This is a command line hook
                        if hook_expression.startswith('$'):
                            self.HOOKS[hook_name] = GreenteaCliTestHook(hook_name, hook_expression[1:])
        except IOError as e:
            HOOKS = None

    def is_hooked_to(self, hook_name):
        return hook_name in self.HOOKS

    def run_hook(self, hook_name, format):
        if hook_name in self.HOOKS:
            return self.HOOKS[hook_name].run(format)
