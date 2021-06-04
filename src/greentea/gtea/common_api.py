#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from subprocess import call, Popen, PIPE


def run_cli_command(cmd, shell=True, verbose=False):
    """! Runs command from command line
    @param shell Shell command (e.g. ls, ps)
    @param verbose Verbose mode flag
    @return Returns (True, 0) if command was executed successfully else return (False, error code)
    """
    result = True
    ret = 0
    try:
        ret = call(cmd, shell=shell)
        if ret:
            result = False
            if verbose:
                print("mbedgt: [ret=%d] Command: %s" % (int(ret), cmd))
    except OSError as e:
        result = False
        if verbose:
            print("mbedgt: [ret=%d] Command: %s" % (int(ret), cmd))
            print(str(e))
    return (result, ret)


def run_cli_process(cmd):
    """! Runs command as a process and return stdout, stderr and ret code
    @param cmd Command to execute
    @return Tuple of (stdout, stderr, returncode)
    """
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        _stdout, _stderr = p.communicate()
    except OSError as e:
        print("gt: Command: %s" % (cmd))
        print(str(e))
        print("gt: traceback...")
        print(e.child_traceback)
        return str(), str(), -1
    return _stdout, _stderr, p.returncode
