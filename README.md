[![Circle CI](https://circleci.com/gh/ARMmbed/greentea.svg?style=svg)](https://circleci.com/gh/ARMmbed/greentea)
[![Coverage Status](https://coveralls.io/repos/github/ARMmbed/greentea/badge.svg?branch=master)](https://coveralls.io/github/ARMmbed/greentea?branch=master)
[![PyPI version](https://badge.fury.io/py/mbed-greentea.svg)](https://badge.fury.io/py/mbed-greentea)

# Greentea - test automation for mbed
_**G**eneric **Re**gression **En**vironment for **te**st **a**utomation_

## Introduction

Greentea is the automated testing tool used for mbed OS development. It automates the process of flashing mbeds, driving the test, and accumulating test results into test reports. It is designed to be used by developers for local development as well as for automation in a Continuous Integration environment.

This document should help you get started using Greentea. It doesn't cover the technical details of the interactions between the platform and the host machine. Please see the [htrun documentation](https://github.com/ARMmbed/htrun) (the tool used by Greentea to drive tests) for more information on this topic.

### Prerequistes

Greentea requires [Python version 2.7](https://www.python.org/downloads/) to run. It supports the following OSes:

- Windows
- Linux (Ubuntu preferred)
- OSX (experimental)

### Installing

Greentea is usually installed by other tools that depend on it. You can see if it is already installed by running:
```
$ mbedgt --version
1.2.5
```

It can also be installed manually via pip.

```
pip install mbed-greentea
```

## Test specification JSON format

The Greentea test specification format allows the test automation to be build system agnostic. It provides important data like test names, paths to test binaries, and on which platform the binaries should run.

Greentea will automatically look for files called `test_spec.json` in your working directory. You can also use the `--test-spec` argument to direct Greentea to a specific test specification file.

When the `-t` / `--target` argument is used with the `--test-spec` argument, it can be used to select which "build" should be used. In the example given below, you could provide the arguments `--test-spec test_spec.json -t K64F-ARM` to only run that build's tests.

### Example of test specification file

In the below example there are two builds defined:
* Build `K64F-ARM` for NXP `K64F` platform compiled with `ARMCC` compiler and
* build `K64F-GCC` for NXP `K64F` platform compiled with `GCC ARM` compiler.

```json
{
    "builds": {
        "K64F-ARM": {
            "platform": "K64F",
            "toolchain": "ARM",
            "base_path": "./BUILD/K64F/ARM",
            "baud_rate": 9600,
            "tests": {
                "tests-mbedmicro-rtos-mbed-mail": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./BUILD/K64F/ARM/tests-mbedmicro-rtos-mbed-mail.bin"
                        }
                    ]
                },
                "tests-mbed_drivers-c_strings": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./BUILD/K64F/ARM/tests-mbed_drivers-c_strings.bin"
                        }
                    ]
                }
            }
        },
        "K64F-GCC": {
            "platform": "K64F",
            "toolchain": "GCC_ARM",
            "base_path": "./BUILD/K64F/GCC_ARM",
            "baud_rate": 9600,
            "tests": {
                "tests-mbedmicro-rtos-mbed-mail": {
                    "binaries": [
                        {
                            "binary_type": "bootable",
                            "path": "./BUILD/K64F/GCC_ARM/tests-mbedmicro-rtos-mbed-mail.bin"
                        }
                    ]
                }
            }
        }
    }
}
```

In below examples we will use the above test specification file.

## Command line usage
Here we will highlight a few of the capabilities of the Greentea command line interface. For a full list of the availble options, please run `mbedgt --help`.

We will assume for the examples below that the above `test_spec.json` file is in current directory.

### Listing all tests
We can use the `-l` argument to list all availble tests:

```
$ mbedgt -l
mbedgt: greentea test automation tool ver. 1.2.5
mbedgt: using multiple test specifications from current directory!
        using 'BUILD\tests\K64F\ARM\test_spec.json'
        using 'BUILD\tests\K64F\GCC_ARM\test_spec.json'
mbedgt: available tests for built 'K64F-GCC_ARM', location 'BUILD/tests/K64F/GCC_ARM'
        test 'tests-mbedmicro-rtos-mbed-mail'
mbedgt: available tests for built 'K64F-ARM', location 'BUILD/tests/K64F/ARM'
        test 'tests-mbed_drivers-c_strings'
        test 'tests-mbedmicro-rtos-mbed-mail'
```

### Executing all tests
The default action of greentea is to execute all tests that were found.
```
$ mbedgt
mbedgt: greentea test automation tool ver. 1.2.5
mbedgt: using multiple test specifications from current directory!
        using 'BUILD\tests\K64F\ARM\test_spec.json'
        using 'BUILD\tests\K64F\GCC_ARM\test_spec.json'
mbedgt: detecting connected mbed-enabled devices...
mbedgt: detected 1 device
mbedgt: processing target 'K64F' toolchain 'GCC_ARM' compatible platforms... (note: switch set to --parallel 1)
mbedgt: running 1 test for platform 'K64F' and toolchain 'GCC_ARM'
mbedgt: mbed-host-test-runner: started
mbedgt: checking for GCOV data...
mbedgt: test case summary event not found
        no test case report present, assuming test suite to be a single test case!
        test suite: tests-mbedmicro-rtos-mbed-mail
        test case: tests-mbedmicro-rtos-mbed-mail
mbedgt: test on hardware with target id: 0240000028884e45005170116bf000468021000097969900
mbedgt: test suite 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 13.18 sec
        test case: 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 13.18 sec
mbedgt: test case summary: 1 pass, 0 failures
mbedgt: all tests finished!
mbedgt: processing target 'K64F' toolchain 'ARM' compatible platforms... (note: switch set to --parallel 1)
mbedgt: running 2 tests for platform 'K64F' and toolchain 'ARM'
mbedgt: mbed-host-test-runner: started
mbedgt: checking for GCOV data...
mbedgt: test case summary event not found
        no test case report present, assuming test suite to be a single test case!
        test suite: tests-mbedmicro-rtos-mbed-mail
        test case: tests-mbedmicro-rtos-mbed-mail
mbedgt: test on hardware with target id: 0240000028884e45005170116bf000468021000097969900
mbedgt: test suite 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 11.65 sec
        test case: 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 11.65 sec
mbedgt: test case summary: 1 pass, 0 failures
mbedgt: mbed-host-test-runner: started
mbedgt: checking for GCOV data...
mbedgt: test on hardware with target id: 0240000028884e45005170116bf000468021000097969900
mbedgt: test suite 'tests-mbed_drivers-c_strings' .................................................... OK in 13.04 sec
        test case: 'C strings: %e %E float formatting' ............................................... OK in 0.06 sec
        test case: 'C strings: %f %f float formatting' ............................................... OK in 0.07 sec
        test case: 'C strings: %g %g float formatting' ............................................... OK in 0.06 sec
        test case: 'C strings: %i %d integer formatting' ............................................. OK in 0.06 sec
        test case: 'C strings: %u %d integer formatting' ............................................. OK in 0.06 sec
        test case: 'C strings: %x %E integer formatting' ............................................. OK in 0.07 sec
        test case: 'C strings: strpbrk' .............................................................. OK in 0.05 sec
        test case: 'C strings: strtok' ............................................................... OK in 0.05 sec
mbedgt: test case summary: 8 passes, 0 failures
mbedgt: all tests finished!
mbedgt: shuffle seed: 0.0968559758
mbedgt: test suite report:
+--------------+---------------+--------------------------------+--------+--------------------+-------------+
| target       | platform_name | test suite                     | result | elapsed_time (sec) | copy_method |
+--------------+---------------+--------------------------------+--------+--------------------+-------------+
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | OK     | 13.04              | shell       |
| K64F-ARM     | K64F          | tests-mbedmicro-rtos-mbed-mail | OK     | 11.65              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbedmicro-rtos-mbed-mail | OK     | 13.18              | shell       |
+--------------+---------------+--------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 3 OK
mbedgt: test case report:
+--------------+---------------+--------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| target       | platform_name | test suite                     | test case                           | passed | failed | result | elapsed_time (sec) |
+--------------+---------------+--------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %e %E float formatting   | 1      | 0      | OK     | 0.06               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %f %f float formatting   | 1      | 0      | OK     | 0.07               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %g %g float formatting   | 1      | 0      | OK     | 0.06               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %i %d integer formatting | 1      | 0      | OK     | 0.06               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %u %d integer formatting | 1      | 0      | OK     | 0.06               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %x %E integer formatting | 1      | 0      | OK     | 0.07               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: strpbrk                  | 1      | 0      | OK     | 0.05               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: strtok                   | 1      | 0      | OK     | 0.05               |
| K64F-ARM     | K64F          | tests-mbedmicro-rtos-mbed-mail | tests-mbedmicro-rtos-mbed-mail      | 1      | 0      | OK     | 11.65              |
| K64F-GCC_ARM | K64F          | tests-mbedmicro-rtos-mbed-mail | tests-mbedmicro-rtos-mbed-mail      | 1      | 0      | OK     | 13.18              |
+--------------+---------------+--------------------------------+-------------------------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 10 OK
mbedgt: completed in 52.13 sec
```

We can also add `-V` to make the output more verbose:
```
$ mbedgt -V
mbedgt: greentea test automation tool ver. 1.2.5
mbedgt: using multiple test specifications from current directory!
        using 'BUILD\tests\K64F\ARM\test_spec.json'
        using 'BUILD\tests\K64F\GCC_ARM\test_spec.json'
mbedgt: detecting connected mbed-enabled devices...
mbedgt: detected 1 device
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
        | platform_name | platform_name_unique | serial_port | mount_point | target_id                                        |
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
        | K64F          | K64F[0]              | COM326      | D:          | 0240000028884e45005170116bf000468021000097969900 |
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
mbedgt: processing target 'K64F' toolchain 'GCC_ARM' compatible platforms... (note: switch set to --parallel 1)
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
        | platform_name | platform_name_unique | serial_port | mount_point | target_id                                        |
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
        | K64F          | K64F[0]              | COM326:9600 | D:          | 0240000028884e45005170116bf000468021000097969900 |
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
mbedgt: running 1 test for platform 'K64F' and toolchain 'GCC_ARM'
        use 1 instance of execution threads for testing
mbedgt: checking for 'host_tests' directory above image directory structure
        found 'host_tests' directory in: 'TESTS\host_tests'
mbedgt: selecting test case observer...
        calling mbedhtrun: mbedhtrun -m K64F -p COM326:9600 -f "BUILD/tests/K64F/GCC_ARM/TESTS/mbedmicro-rtos-mbed/mail/mail.bin" -e "TESTS\host_tests" -d D: -C 4 -c shell -t 0240000028884e45005170116
bf000468021000097969900
mbedgt: mbed-host-test-runner: started
[1486401736.23][HTST][INF] host test executor ver. 1.1.6
[1486401736.23][HTST][INF] copy image onto target...
[1486401736.23][COPY][INF] Waiting up to 60 sec for '0240000028884e45005170116bf000468021000097969900' mount point (current is 'D:')...
        1 file(s) copied.
[1486401744.91][HTST][INF] starting host test process...
[1486401745.38][CONN][INF] starting connection process...
[1486401745.38][CONN][INF] notify event queue about extra 60 sec timeout for serial port pooling
[1486401745.38][CONN][INF] initializing serial port listener...
[1486401745.38][PLGN][INF] Waiting up to 60 sec for '0240000028884e45005170116bf000468021000097969900' serial port (current is 'COM326')...
[1486401745.38][HTST][INF] setting timeout to: 60 sec
[1486401745.51][SERI][INF] serial(port=COM326, baudrate=9600, timeout=0.01)
[1486401745.52][SERI][INF] reset device using 'default' plugin...
[1486401745.77][SERI][INF] waiting 1.00 sec after reset
[1486401746.77][SERI][INF] wait for it...
[1486401746.77][SERI][TXD] mbedmbedmbedmbedmbedmbedmbedmbedmbedmbed
[1486401746.77][CONN][INF] sending up to 2 __sync packets (specified with --sync=2)
[1486401746.77][CONN][INF] sending preamble '040118ca-83cf-42ca-a039-a1b384784129'
[1486401746.77][SERI][TXD] {{__sync;040118ca-83cf-42ca-a039-a1b384784129}}
[1486401746.90][CONN][RXD] mbedmbedmbedmbedmbedmbedmbedmbed
[1486401746.95][CONN][INF] found SYNC in stream: {{__sync;040118ca-83cf-42ca-a039-a1b384784129}} it is #0 sent, queued...
[1486401746.96][HTST][INF] sync KV found, uuid=040118ca-83cf-42ca-a039-a1b384784129, timestamp=1486401746.950000
[1486401746.97][CONN][INF] found KV pair in stream: {{__version;1.3.0}}, queued...
[1486401746.97][HTST][INF] DUT greentea-client version: 1.3.0
[1486401746.99][CONN][INF] found KV pair in stream: {{__timeout;20}}, queued...
[1486401746.99][HTST][INF] setting timeout to: 20 sec
[1486401747.03][CONN][INF] found KV pair in stream: {{__host_test_name;default_auto}}, queued...
[1486401747.04][HTST][INF] host test class: '<class 'mbed_host_tests.host_tests.default_auto.DefaultAuto'>'
[1486401747.04][HTST][INF] host test setup() call...
[1486401747.04][HTST][INF] CALLBACKs updated
[1486401747.04][HTST][INF] host test detected: default_auto
[1486401747.06][CONN][RXD]  11 36.30V 12.10A ... [OK]
[1486401747.15][CONN][RXD]  12 39.60V 13.20A ... [OK]
[1486401747.25][CONN][RXD]  13 42.90V 14.30A ... [OK]
[1486401747.35][CONN][RXD]  14 46.20V 15.40A ... [OK]
[1486401747.45][CONN][RXD]  15 49.50V 16.50A ... [OK]
[1486401747.55][CONN][RXD]  16 52.80V 17.60A ... [OK]
[1486401747.65][CONN][RXD]  17 56.10V 18.70A ... [OK]
[1486401747.75][CONN][RXD]  18 59.40V 19.80A ... [OK]
[1486401747.85][CONN][RXD]  19 62.70V 20.90A ... [OK]
[1486401747.95][CONN][RXD]  20 66.00V 22.00A ... [OK]
[1486401748.05][CONN][RXD]  21 69.30V 23.10A ... [OK]
[1486401748.15][CONN][RXD]  22 72.60V 24.20A ... [OK]
[1486401748.25][CONN][RXD]  23 75.90V 25.30A ... [OK]
[1486401748.35][CONN][RXD]  24 79.20V 26.40A ... [OK]
[1486401748.45][CONN][RXD]  25 82.50V 27.50A ... [OK]
[1486401748.55][CONN][RXD]  26 85.80V 28.60A ... [OK]
[1486401748.58][CONN][INF] found KV pair in stream: {{max_heap_usage;0}}, queued...
[1486401748.59][HTST][ERR] orphan event in main phase: {{max_heap_usage;0}}, timestamp=1486401748.583000
[1486401748.59][CONN][INF] found KV pair in stream: {{end;success}}, queued...
[1486401748.60][HTST][INF] __notify_complete(True)
[1486401748.61][CONN][INF] found KV pair in stream: {{__exit;0}}, queued...
[1486401748.62][HTST][INF] __exit(0)
[1486401748.62][HTST][INF] __exit_event_queue received
[1486401748.62][HTST][INF] test suite run finished after 1.62 sec...
[1486401748.62][CONN][INF] received special even '__host_test_finished' value='True', finishing
[1486401748.63][HTST][INF] CONN exited with code: 0
[1486401748.63][HTST][INF] No events in queue
[1486401748.63][HTST][INF] stopped consuming events
[1486401748.63][HTST][INF] host test result() call skipped, received: True
[1486401748.63][HTST][INF] calling blocking teardown()
[1486401748.63][HTST][INF] teardown() finished
[1486401748.63][HTST][INF] {{result;success}}
mbedgt: checking for GCOV data...
mbedgt: mbed-host-test-runner: stopped and returned 'OK'
mbedgt: test case summary event not found
        no test case report present, assuming test suite to be a single test case!
        test suite: tests-mbedmicro-rtos-mbed-mail
        test case: tests-mbedmicro-rtos-mbed-mail
mbedgt: test on hardware with target id: 0240000028884e45005170116bf000468021000097969900
mbedgt: test suite 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 12.94 sec
        test case: 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 12.94 sec
mbedgt: test case summary: 1 pass, 0 failures
mbedgt: all tests finished!
mbedgt: processing target 'K64F' toolchain 'ARM' compatible platforms... (note: switch set to --parallel 1)
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
        | platform_name | platform_name_unique | serial_port | mount_point | target_id                                        |
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
        | K64F          | K64F[0]              | COM326:9600 | D:          | 0240000028884e45005170116bf000468021000097969900 |
        +---------------+----------------------+-------------+-------------+--------------------------------------------------+
mbedgt: running 2 tests for platform 'K64F' and toolchain 'ARM'
        use 1 instance of execution threads for testing
mbedgt: checking for 'host_tests' directory above image directory structure
        found 'host_tests' directory in: 'TESTS\host_tests'
mbedgt: selecting test case observer...
        calling mbedhtrun: mbedhtrun -m K64F -p COM326:9600 -f "BUILD/tests/K64F/ARM/TESTS/mbedmicro-rtos-mbed/mail/mail.bin" -e "TESTS\host_tests" -d D: -C 4 -c shell -t 0240000028884e45005170116bf00
0468021000097969900
mbedgt: mbed-host-test-runner: started
[1486401756.78][HTST][INF] host test executor ver. 1.1.6
[1486401756.78][HTST][INF] copy image onto target...
[1486401756.78][COPY][INF] Waiting up to 60 sec for '0240000028884e45005170116bf000468021000097969900' mount point (current is 'D:')...
        1 file(s) copied.
[1486401764.01][HTST][INF] starting host test process...
[1486401764.48][CONN][INF] starting connection process...
[1486401764.48][CONN][INF] notify event queue about extra 60 sec timeout for serial port pooling
[1486401764.48][CONN][INF] initializing serial port listener...
[1486401764.48][PLGN][INF] Waiting up to 60 sec for '0240000028884e45005170116bf000468021000097969900' serial port (current is 'COM326')...
[1486401764.50][HTST][INF] setting timeout to: 60 sec
[1486401764.63][SERI][INF] serial(port=COM326, baudrate=9600, timeout=0.01)
[1486401764.63][SERI][INF] reset device using 'default' plugin...
[1486401764.88][SERI][INF] waiting 1.00 sec after reset
[1486401765.88][SERI][INF] wait for it...
[1486401765.88][SERI][TXD] mbedmbedmbedmbedmbedmbedmbedmbedmbedmbed
[1486401765.88][CONN][INF] sending up to 2 __sync packets (specified with --sync=2)
[1486401765.88][CONN][INF] sending preamble 'f48db736-0f70-4c46-bfca-c6a5540d6b7c'
[1486401765.88][SERI][TXD] {{__sync;f48db736-0f70-4c46-bfca-c6a5540d6b7c}}
[1486401766.01][CONN][RXD] mbedmbedmbedmbedmbedmbedmbedmbed
[1486401766.06][CONN][INF] found SYNC in stream: {{__sync;f48db736-0f70-4c46-bfca-c6a5540d6b7c}} it is #0 sent, queued...
[1486401766.07][HTST][INF] sync KV found, uuid=f48db736-0f70-4c46-bfca-c6a5540d6b7c, timestamp=1486401766.063000
[1486401766.08][CONN][INF] found KV pair in stream: {{__version;1.3.0}}, queued...
[1486401766.09][HTST][INF] DUT greentea-client version: 1.3.0
[1486401766.10][CONN][INF] found KV pair in stream: {{__timeout;20}}, queued...
[1486401766.11][HTST][INF] setting timeout to: 20 sec
[1486401766.14][CONN][INF] found KV pair in stream: {{__host_test_name;default_auto}}, queued...
[1486401766.14][HTST][INF] host test class: '<class 'mbed_host_tests.host_tests.default_auto.DefaultAuto'>'
[1486401766.14][HTST][INF] host test setup() call...
[1486401766.14][HTST][INF] CALLBACKs updated
[1486401766.14][HTST][INF] host test detected: default_auto
[1486401766.17][CONN][RXD]  11 36.30V 12.10A ... [OK]
[1486401766.27][CONN][RXD]  12 39.60V 13.20A ... [OK]
[1486401766.37][CONN][RXD]  13 42.90V 14.30A ... [OK]
[1486401766.47][CONN][RXD]  14 46.20V 15.40A ... [OK]
[1486401766.57][CONN][RXD]  15 49.50V 16.50A ... [OK]
[1486401766.67][CONN][RXD]  16 52.80V 17.60A ... [OK]
[1486401766.77][CONN][RXD]  17 56.10V 18.70A ... [OK]
[1486401766.87][CONN][RXD]  18 59.40V 19.80A ... [OK]
[1486401766.97][CONN][RXD]  19 62.70V 20.90A ... [OK]
[1486401767.07][CONN][RXD]  20 66.00V 22.00A ... [OK]
[1486401767.17][CONN][RXD]  21 69.30V 23.10A ... [OK]
[1486401767.27][CONN][RXD]  22 72.60V 24.20A ... [OK]
[1486401767.37][CONN][RXD]  23 75.90V 25.30A ... [OK]
[1486401767.47][CONN][RXD]  24 79.20V 26.40A ... [OK]
[1486401767.57][CONN][RXD]  25 82.50V 27.50A ... [OK]
[1486401767.66][CONN][RXD]  26 85.80V 28.60A ... [OK]
[1486401767.69][CONN][INF] found KV pair in stream: {{max_heap_usage;0}}, queued...
[1486401767.70][HTST][ERR] orphan event in main phase: {{max_heap_usage;0}}, timestamp=1486401767.695000
[1486401767.71][CONN][INF] found KV pair in stream: {{end;success}}, queued...
[1486401767.72][HTST][INF] __notify_complete(True)
[1486401767.72][CONN][INF] found KV pair in stream: {{__exit;0}}, queued...
[1486401767.73][HTST][INF] __exit(0)
[1486401767.73][HTST][INF] __exit_event_queue received
[1486401767.73][HTST][INF] test suite run finished after 1.62 sec...
[1486401767.73][CONN][INF] received special even '__host_test_finished' value='True', finishing
[1486401767.75][HTST][INF] CONN exited with code: 0
[1486401767.75][HTST][INF] No events in queue
[1486401767.75][HTST][INF] stopped consuming events
[1486401767.75][HTST][INF] host test result() call skipped, received: True
[1486401767.75][HTST][INF] calling blocking teardown()
[1486401767.75][HTST][INF] teardown() finished
[1486401767.75][HTST][INF] {{result;success}}
mbedgt: checking for GCOV data...
mbedgt: mbed-host-test-runner: stopped and returned 'OK'
mbedgt: test case summary event not found
        no test case report present, assuming test suite to be a single test case!
        test suite: tests-mbedmicro-rtos-mbed-mail
        test case: tests-mbedmicro-rtos-mbed-mail
mbedgt: test on hardware with target id: 0240000028884e45005170116bf000468021000097969900
mbedgt: test suite 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 11.52 sec
        test case: 'tests-mbedmicro-rtos-mbed-mail' .................................................. OK in 11.52 sec
mbedgt: test case summary: 1 pass, 0 failures
mbedgt: checking for 'host_tests' directory above image directory structure
        found 'host_tests' directory in: 'TESTS\host_tests'
mbedgt: selecting test case observer...
        calling mbedhtrun: mbedhtrun -m K64F -p COM326:9600 -f "BUILD/tests/K64F/ARM/TESTS/mbed_drivers/c_strings/c_strings.bin" -e "TESTS\host_tests" -d D: -C 4 -c shell -t 0240000028884e45005170116b
f000468021000097969900
mbedgt: mbed-host-test-runner: started
[1486401768.45][HTST][INF] host test executor ver. 1.1.6
[1486401768.45][HTST][INF] copy image onto target...
[1486401768.45][COPY][INF] Waiting up to 60 sec for '0240000028884e45005170116bf000468021000097969900' mount point (current is 'D:')...
        1 file(s) copied.
[1486401776.08][HTST][INF] starting host test process...
[1486401776.54][CONN][INF] starting connection process...
[1486401776.54][CONN][INF] notify event queue about extra 60 sec timeout for serial port pooling
[1486401776.54][CONN][INF] initializing serial port listener...
[1486401776.55][PLGN][INF] Waiting up to 60 sec for '0240000028884e45005170116bf000468021000097969900' serial port (current is 'COM326')...
[1486401776.55][HTST][INF] setting timeout to: 60 sec
[1486401776.68][SERI][INF] serial(port=COM326, baudrate=9600, timeout=0.01)
[1486401776.69][SERI][INF] reset device using 'default' plugin...
[1486401776.94][SERI][INF] waiting 1.00 sec after reset
[1486401777.94][SERI][INF] wait for it...
[1486401777.94][SERI][TXD] mbedmbedmbedmbedmbedmbedmbedmbedmbedmbed
[1486401777.94][CONN][INF] sending up to 2 __sync packets (specified with --sync=2)
[1486401777.94][CONN][INF] sending preamble 'd9148788-7df9-45cb-9238-cd4ee161161d'
[1486401777.94][SERI][TXD] {{__sync;d9148788-7df9-45cb-9238-cd4ee161161d}}
[1486401778.07][CONN][RXD] mbedmbedmbedmbedmbedmbedmbedmbed
[1486401778.12][CONN][INF] found SYNC in stream: {{__sync;d9148788-7df9-45cb-9238-cd4ee161161d}} it is #0 sent, queued...
[1486401778.13][HTST][INF] sync KV found, uuid=d9148788-7df9-45cb-9238-cd4ee161161d, timestamp=1486401778.120000
[1486401778.15][CONN][INF] found KV pair in stream: {{__version;1.3.0}}, queued...
[1486401778.15][HTST][INF] DUT greentea-client version: 1.3.0
[1486401778.16][CONN][INF] found KV pair in stream: {{__timeout;5}}, queued...
[1486401778.16][HTST][INF] setting timeout to: 5 sec
[1486401778.20][CONN][INF] found KV pair in stream: {{__host_test_name;default_auto}}, queued...
[1486401778.21][HTST][INF] host test class: '<class 'mbed_host_tests.host_tests.default_auto.DefaultAuto'>'
[1486401778.21][HTST][INF] host test setup() call...
[1486401778.21][HTST][INF] CALLBACKs updated
[1486401778.21][HTST][INF] host test detected: default_auto
[1486401778.22][CONN][INF] found KV pair in stream: {{__testcase_count;8}}, queued...
[1486401778.25][CONN][RXD] >>> Running 8 test cases...
[1486401778.29][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: strtok}}, queued...
[1486401778.34][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: strpbrk}}, queued...
[1486401778.40][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: %i %d integer formatting}}, queued...
[1486401778.45][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: %u %d integer formatting}}, queued...
[1486401778.51][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: %x %E integer formatting}}, queued...
[1486401778.57][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: %f %f float formatting}}, queued...
[1486401778.63][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: %e %E float formatting}}, queued...
[1486401778.68][CONN][RXD]
[1486401778.68][CONN][INF] found KV pair in stream: {{__testcase_name;C strings: %g %g float formatting}}, queued...
[1486401778.73][CONN][RXD] >>> Running case #1: 'C strings: strtok'...
[1486401778.77][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: strtok}}, queued...
[1486401778.82][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: strtok;1;0}}, queued...
[1486401778.86][CONN][RXD] >>> 'C strings: strtok': 1 passed, 0 failed
[1486401778.87][CONN][RXD]
[1486401778.91][CONN][RXD] >>> Running case #2: 'C strings: strpbrk'...
[1486401778.95][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: strpbrk}}, queued...
[1486401779.00][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: strpbrk;1;0}}, queued...
[1486401779.05][CONN][RXD] >>> 'C strings: strpbrk': 1 passed, 0 failed
[1486401779.05][CONN][RXD]
[1486401779.12][CONN][RXD] >>> Running case #3: 'C strings: %i %d integer formatting'...
[1486401779.18][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %i %d integer formatting}}, queued...
[1486401779.24][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %i %d integer formatting;1;0}}, queued...
[1486401779.31][CONN][RXD] >>> 'C strings: %i %d integer formatting': 1 passed, 0 failed
[1486401779.31][CONN][RXD]
[1486401779.37][CONN][RXD] >>> Running case #4: 'C strings: %u %d integer formatting'...
[1486401779.43][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %u %d integer formatting}}, queued...
[1486401779.51][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %u %d integer formatting;1;0}}, queued...
[1486401779.57][CONN][RXD] >>> 'C strings: %u %d integer formatting': 1 passed, 0 failed
[1486401779.57][CONN][RXD]
[1486401779.63][CONN][RXD] >>> Running case #5: 'C strings: %x %E integer formatting'...
[1486401779.69][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %x %E integer formatting}}, queued...
[1486401779.76][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %x %E integer formatting;1;0}}, queued...
[1486401779.83][CONN][RXD] >>> 'C strings: %x %E integer formatting': 1 passed, 0 failed
[1486401779.83][CONN][RXD]
[1486401779.88][CONN][RXD] >>> Running case #6: 'C strings: %f %f float formatting'...
[1486401779.94][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %f %f float formatting}}, queued...
[1486401780.01][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %f %f float formatting;1;0}}, queued...
[1486401780.07][CONN][RXD] >>> 'C strings: %f %f float formatting': 1 passed, 0 failed
[1486401780.08][CONN][RXD]
[1486401780.13][CONN][RXD] >>> Running case #7: 'C strings: %e %E float formatting'...
[1486401780.19][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %e %E float formatting}}, queued...
[1486401780.26][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %e %E float formatting;1;0}}, queued...
[1486401780.32][CONN][RXD] >>> 'C strings: %e %E float formatting': 1 passed, 0 failed
[1486401780.32][CONN][RXD]
[1486401780.38][CONN][RXD] >>> Running case #8: 'C strings: %g %g float formatting'...
[1486401780.44][CONN][INF] found KV pair in stream: {{__testcase_start;C strings: %g %g float formatting}}, queued...
[1486401780.51][CONN][INF] found KV pair in stream: {{__testcase_finish;C strings: %g %g float formatting;1;0}}, queued...
[1486401780.57][CONN][RXD] >>> 'C strings: %g %g float formatting': 1 passed, 0 failed
[1486401780.57][CONN][RXD]
[1486401780.61][CONN][RXD] >>> Test cases: 8 passed, 0 failed
[1486401780.64][CONN][INF] found KV pair in stream: {{__testcase_summary;8;0}}, queued...
[1486401780.66][CONN][INF] found KV pair in stream: {{max_heap_usage;0}}, queued...
[1486401780.66][HTST][ERR] orphan event in main phase: {{max_heap_usage;0}}, timestamp=1486401780.656000
[1486401780.68][CONN][INF] found KV pair in stream: {{end;success}}, queued...
[1486401780.68][HTST][INF] __notify_complete(True)
[1486401780.69][CONN][INF] found KV pair in stream: {{__exit;0}}, queued...
[1486401780.69][HTST][INF] __exit(0)
[1486401780.69][HTST][INF] __exit_event_queue received
[1486401780.69][HTST][INF] test suite run finished after 2.53 sec...
[1486401780.70][CONN][INF] received special even '__host_test_finished' value='True', finishing
[1486401780.71][HTST][INF] CONN exited with code: 0
[1486401780.71][HTST][INF] No events in queue
[1486401780.71][HTST][INF] stopped consuming events
[1486401780.71][HTST][INF] host test result() call skipped, received: True
[1486401780.71][HTST][INF] calling blocking teardown()
[1486401780.71][HTST][INF] teardown() finished
[1486401780.71][HTST][INF] {{result;success}}
mbedgt: checking for GCOV data...
mbedgt: mbed-host-test-runner: stopped and returned 'OK'
mbedgt: test on hardware with target id: 0240000028884e45005170116bf000468021000097969900
mbedgt: test suite 'tests-mbed_drivers-c_strings' .................................................... OK in 12.95 sec
        test case: 'C strings: %e %E float formatting' ............................................... OK in 0.07 sec
        test case: 'C strings: %f %f float formatting' ............................................... OK in 0.07 sec
        test case: 'C strings: %g %g float formatting' ............................................... OK in 0.07 sec
        test case: 'C strings: %i %d integer formatting' ............................................. OK in 0.06 sec
        test case: 'C strings: %u %d integer formatting' ............................................. OK in 0.08 sec
        test case: 'C strings: %x %E integer formatting' ............................................. OK in 0.07 sec
        test case: 'C strings: strpbrk' .............................................................. OK in 0.05 sec
        test case: 'C strings: strtok' ............................................................... OK in 0.05 sec
mbedgt: test case summary: 8 passes, 0 failures
mbedgt: all tests finished!
mbedgt: shuffle seed: 0.5632084240
mbedgt: test suite report:
+--------------+---------------+--------------------------------+--------+--------------------+-------------+
| target       | platform_name | test suite                     | result | elapsed_time (sec) | copy_method |
+--------------+---------------+--------------------------------+--------+--------------------+-------------+
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | OK     | 12.95              | shell       |
| K64F-ARM     | K64F          | tests-mbedmicro-rtos-mbed-mail | OK     | 11.52              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbedmicro-rtos-mbed-mail | OK     | 12.94              | shell       |
+--------------+---------------+--------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 3 OK
mbedgt: test case report:
+--------------+---------------+--------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| target       | platform_name | test suite                     | test case                           | passed | failed | result | elapsed_time (sec) |
+--------------+---------------+--------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %e %E float formatting   | 1      | 0      | OK     | 0.07               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %f %f float formatting   | 1      | 0      | OK     | 0.07               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %g %g float formatting   | 1      | 0      | OK     | 0.07               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %i %d integer formatting | 1      | 0      | OK     | 0.06               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %u %d integer formatting | 1      | 0      | OK     | 0.08               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: %x %E integer formatting | 1      | 0      | OK     | 0.07               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: strpbrk                  | 1      | 0      | OK     | 0.05               |
| K64F-ARM     | K64F          | tests-mbed_drivers-c_strings   | C strings: strtok                   | 1      | 0      | OK     | 0.05               |
| K64F-ARM     | K64F          | tests-mbedmicro-rtos-mbed-mail | tests-mbedmicro-rtos-mbed-mail      | 1      | 0      | OK     | 11.52              |
| K64F-GCC_ARM | K64F          | tests-mbedmicro-rtos-mbed-mail | tests-mbedmicro-rtos-mbed-mail      | 1      | 0      | OK     | 12.94              |
+--------------+---------------+--------------------------------+-------------------------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 10 OK
mbedgt: completed in 53.59 sec

```

### Limiting tests
We can select test cases by name using the `-n` argument. The below command will execute all tests named `tests-mbedmicro-rtos-mbed-mail` from all builds in the test specification:
```
$ mbedgt -n tests-mbedmicro-rtos-mbed-mail
```

When using the `-n` argument, you can use the `*` character at the end of a test name to match all tests that share a prefix. This command will execute all tests that start with `tests*`:

```
$ mbedgt -n tests*
```

We can use the `-t` argument to select which build to use when finding tests. This command will execute the test `tests-mbedmicro-rtos-mbed-mail` for the `K64F-ARM` build in the test specification:
```
$ mbedgt -n tests-mbedmicro-rtos-mbed-mail -t K64F-ARM
```

You can use a comma (`,`) to separate test names (argument `-n`) and build names (argument `-t`). This command will execute the tests `tests-mbedmicro-rtos-mbed-mail` and `tests-mbed_drivers-c_strings` for the `K64F-ARM` and `K64F-GCC_ARM` builds in the test specification:
```
$ mbedgt -n tests-mbedmicro-rtos-mbed-mail,tests-mbed_drivers-c_strings -t K64F-ARM,K64F-GCC_ARM
```

### Selecting platforms
You can limit which boards Greentea should use for testing by using the `--use-tids` argument.

```
$ mbedgt --use-tids 02400203C3423E603EBEC3D8,024002031E031E6AE3FFE3D2
```

Where ```02400203C3423E603EBEC3D8``` and ```024002031E031E6AE3FFE3D2``` are the target IDs of platforms attached to your system.

Target IDs can be viewed by using the [mbed-ls](https://github.com/ARMmbed/mbed-ls) tool (installed with Greentea).

```
$ mbedls
+--------------+---------------------+------------+------------+-------------------------+
|platform_name |platform_name_unique |mount_point |serial_port |target_id                |
+--------------+---------------------+------------+------------+-------------------------+
|K64F          |K64F[0]              |E:          |COM160      |024002031E031E6AE3FFE3D2 |
|K64F          |K64F[1]              |F:          |COM162      |02400203C3423E603EBEC3D8 |
|LPC1768       |LPC1768[0]           |G:          |COM5        |1010ac87cfc4f23c4c57438d |
+--------------+---------------------+------------+------------+-------------------------+
```
In this case, one target - the LPC1768 - won’t be tested.

### Creating reports
Greentea supports a number of report formats.

#### HTML
This creates an interactive HTML page with test results and logs.
```
mbedgt --report-html html_report.html
```

#### JUnit
This creates a XML JUnit report which can be used with popular Continuous Integration software like [Jenkins](https://jenkins.io/index.html).
```
mbedgt --report-junit junit_report.xml
```

#### JSON
This creates a general JSON report.
```
mbedgt --report-json json_report.json
```

#### Plain text
This creates a human-friendly text summary of the test run.
```
mbedgt --report-text text_report.text
```

## Host test detection
When developing with mbed OS, Grentea will detect host tests automatically if they placed in the correct location. All tests in mbed OS are placed under a `TESTS` directory. You may place custom host test scripts in a folder named `host_tests` in this folder. For more information on the mbed OS test directory structure, please see the [mbed CLI documentation](https://docs.mbed.com/docs/mbed-os-handbook/en/latest/dev_tools/cli/#test-directory-structure)

## Common issues

### `IOERR_SERIAL` errors
This can be caused by a number of things:
- The serial port is in use by another program. Be sure all terminals and other instances of Greentea are closed before trying again
- The mbed's interface firmware is out of date. Please see the platform's page on [developer.mbed.org](https://developer.mbed.org/) for details on how to update it
