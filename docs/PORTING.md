# Table of contents

* [Table of contents](#table-of-contents)
* [How to prepare test tools for porting](#how-to-prepare-test-tools-for-porting)
* [Getting started](#getting-started)
  * [Test tools overview](#test-tools-overview)
    * [Greentea](#greentea)
    * [greentea-client](#greentea-client)
    * [htrun](#htrun)
    * [mbed-ls](#mbed-ls)
* [Test tools installation dependencies](#test-tools-installation-dependencies)
  * [Test tools installation](#test-tools-installation)
  * [Using virtual environment](#using-virtual-environment)
    * [How to get and install `virtualenv`](#how-to-get-and-install-virtualenv)
    * [Basic Usage of virtual environment](#basic-usage-of-virtual-environment)
  * [Verify test tools setup](#verify-test-tools-setup)
* [Test tools work flows](#test-tools-work-flows)
  * [List connected devices](#list-connected-devices)
  * [Detect your mbed platform with mbed-ls](#detect-your-mbed-platform-with-mbed-ls)
    * [Checking if your platform is already supported by mbed-ls](#checking-if-your-platform-is-already-supported-by-mbed-ls)
  * [Build your project](#build-your-project)
* [Run test case using Greentea](#run-test-case-using-greentea)
  * [Running one test binary with htrun](#running-one-test-binary-with-htrun)
  * [Interpretting test results](#interpretting-test-results)
    * [Terms used in `htrun` and `Greentea` output](#terms-used-in-htrun-and-greentea-output)
    * [Test suite result](#test-suite-result)
    * [Test cases results](#test-cases-results)

# How to prepare test tools for porting

This document will walk you through most common work flow with mbed test tools. It will also demonstrate how to prepare test tools and outline useful features.

# Getting started

Below you will find short *HOW TO* setup mbed test tools for new mbed-enabled platform porting.

## Test tools overview
```mbed ```  test tools collection:
* [Greentea](https://github.com/ARMmbed/greentea) - mbed test automation framework, instrument test suite execution inside your yotta module.
  * This application is also distributed as Python Package: [mbed-greentea in PyPI](https://pypi.python.org/pypi/mbed-greentea).
* [greentea-client](https://github.com/ARMmbed/greentea-client) - Greenteas device under test (DUT) side C++ library.
    * Greentea-client public API can be found [here](https://github.com/ARMmbed/htrun#greentea-client-api).
* [htrun](https://github.com/ARMmbed/htrun) - test runner for mbed test suite.
  * This application is also distributed as Python Package: [mbed-host-tests in PyPI](https://pypi.python.org/pypi/mbed-host-tests).
* [mbed-ls](https://github.com/ARMmbed/mbed-ls) - list all connected to host mbed compatible devices.
  * This application is also distributed as Python Package: [mbed-ls in PyPI](https://pypi.python.org/pypi/mbed-ls).

### Greentea
"Generic Regression Environment for test automation" for mbed-enabled platforms. use this application to execute group of tests, generate report and check for regressions.
This application is available as command line tool called `mbedgt` and importable Python 2.7 library.

* [Greentea](https://github.com/ARMmbed/greentea) - mbed test automation framework, instrument test suite execution inside your yotta module.
* Installation guide is [here](https://github.com/ARMmbed/greentea#installing-greentea).
* This application is also distributed as Python Package: [mbed-greentea in PyPI](https://pypi.python.org/pypi/mbed-greentea).

### greentea-client
C/C++ DUT's (Device Under Test) side of Greentea test suite. Use this library to instrument your test cases so they work with Greentea. This library will allow your DUT to communicate with Greentea and host tests.
This application is available in your C/C++ environment via `#include "greentea-client/test_env.h"`.

* [greentea-client](https://github.com/ARMmbed/greentea-client) - Greentea's device side, C++ library.
* This application is also distributed as yotta module: [greentea-client](https://yotta.mbed.com/#/module/greentea-client/0.1.8).

### htrun
Use `htrun` to flash, reset and perform host supervised tests on mbed-enabled platforms. This application is used explicitly by Greentea to instrument test binary execution (flashing, platform reset and test cases instrumentation). You can also use this application to manually trigger test binary execution.
This application is available as command line tool called `mbedhtrun`  and importable Python 2.7 library.

* [htrun](https://github.com/ARMmbed/htrun) - test runner for mbed test suite.
* Installation guide is [here](https://github.com/ARMmbed/htrun#installation).
* This application is also distributed as Python Package: [mbed-host-tests in PyPI](https://pypi.python.org/pypi/mbed-host-tests).

### mbed-ls
`mbedls` is a set of tools used to detect mbed-enabled devices on the host OSs: Windows 7 onwards, Ubuntu/Linux and Mac OS.
This application is available as command line tool called `mbedls` and importable Python 2.7 library.

* [mbed-ls](https://github.com/ARMmbed/mbed-ls) - list all connected to host mbed compatible devices.
* Installation guide is [here](https://github.com/ARMmbed/mbed-ls#installation-from-python-sources).
* This application is also distributed as Python Package: [mbed-ls in PyPI](https://pypi.python.org/pypi/mbed-ls).

# Test tools installation dependencies

All test tools are implemented with and are using Python 2.7.11:
* [Python](https://www.python.org/downloads/). If you do not have Python installed already, we recommend [version 2.7.11](https://www.python.org/downloads/release/python-2711/). You'll need to add the following modules:
  * [Pip](https://pypi.python.org/pypi/pip). Pip comes bundled with some Python versions; run `$ pip --version` to see if you already have it.
  * [setuptools](https://pythonhosted.org/an_example_pypi_project/setuptools.html) to install dependencies.
* Installed source control client: [Git](https://git-scm.com/downloads) in case you want to install test tools from sources directly.

For `mbed-enabled` devices you may need to install additional serial port drivers:
* Please follow the installation instructions [for the serial port driver](https://developer.mbed.org/handbook/Windows-serial-configuration).

Test tools require your platform to expose MSD (mount point) and CDC (serial port) for flashing (binary drag&drop) and DUT <-> host communication.

## Test tools installation

Installation of test tools will include installation of `Greentea`, `htrun` and `mbed-ls`:
```
$ pip install mbed-greentea --upgrade
```

Above command will install all Python package dependencies together with required mbed test tools: `mbed-host-tests` and `mbed-ls`.
No additional steps are necessary if this installation is successful.

## Using virtual environment

You may already recognize that out test tools are mainly written in Python (2.7). If your project / Continuous Integration job is using Python tools and Python packages extensively you may find that installing our test tools may cause Python dependencies collision. To avoid unnecessary hassle and separate packages used by tools and your system you can use virtual environment!

*A Virtual Environment is a tool to keep Python package dependencies required by different projects in separate places, by creating virtual Python environments for them.*

For more details about Python's virtual environment please check [Virtual Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

### How to get and install `virtualenv`

Note that even installing virtual environment is option for some systems it is recommended.

The simplest way is to just install ```virtualenv``` via ```pip```:
```
$ pip install virtualenv -U
```

### Basic Usage of virtual environment

* Create a virtual environment for your project:
```
$ cd my_project
$ virtualenv venv
```

* To begin using the virtual environment (On Windows), it needs to be activated:
```bash
$ venv\Scripts\activate.bat
```

* To begin using the virtual environment (On Linux), it needs to be activated:
```bash
$ source venv/bin/activate
```

* Install packages as usual, for example:
```bash
$ pip install mbed-greentea
```

* If you are done working in the virtual environment (On Windows) for the moment, you can deactivate it:
```
$ venv/script/deactivate.bat
```

* If you are done working in the virtual environment (On Windows) for the moment, you can deactivate it:
```
$ source venv/bin/deactivate
```

More information regarding virtual environment and mbed test tools can be found [here](https://github.com/ARMmbed/greentea#virtual-environments-python). Please note that these instructions may include `yotta` installation. You can skip this steps if you are not using `yotta` as your build system.

## Verify test tools setup

You can use `pip freeze` command to check if mbed test tools are installed on your system correctly:
```
$ pip freeze | grep mbed
mbed-greentea==0.2.18
mbed-host-tests==0.2.14
mbed-ls==0.2.10
```

We can see that all required packages (`mbed-greentea`, `mbed-host-tests` and `mbed-host-tests`) are present and in latest `0.2.x` versions.

Alternatively you can just command line tools with help option:
```
$ mbedgt --version
```
```
$ mbedhtrun --version
```
```
$ mbedls --version
```

# Test tools work flows

This chapter will present most common work flows when using mbed test tools.

## List connected devices

To list all connected to your host computer devices please use `mbedls` command:
```
$ mbedls
+---------------+----------------------+-------------+-------------+----------------------+-----------------+
| platform_name | platform_name_unique | mount_point | serial_port | target_id            | daplink_version |
+---------------+----------------------+-------------+-------------+----------------------+-----------------+
| K64F          | K64F[0]              | E:          | COM228      | 02400000293049769900 | 0241            |
| K64F          | K64F[1]              | H:          | COM230      | 02400000335149769900 | 0241            |
+---------------+----------------------+-------------+-------------+----------------------+-----------------+
```

`mbedls` reports:
* `platform_name` as canonical platform name used across our build systems and test tools.
* `mount_point` as where mbed-enabled device's MSD was mounted. Mount point is used to flash binaries onto platforms.
* `mount_point` as where mbed-enabled device's CDC was mounted. Serial port is used to communicate with devices and host while test execution. Serial port is also used to reset device by calling embedded into DAPLink `sendBreak` command support.
* `target_id` as unique ASCII HEX identifier used to distinguish between devices.
* `daplink_version` as DAPLink / Interface Chip version.

Above command should list all detected mbed-enabled platforms. Note that `mbedls` is used by our test tools to detect platforms. Automation process requires us to:
* Detect all available platform.
* Allocate platform(s) for testing purposes by Greentea application.
* Determine device presence in the system using unique target ID while testing.

## Detect your mbed platform with mbed-ls

If your device is not detected, for example `target_id` can't be mapped to `platform_name` you may want to mock / temporarily map  `target_id` to your custom platform name (`platform_name`).

You can use [this instructions](https://github.com/ARMmbed/mbed-ls#mocking-new-or-existing-target-to-custom-platform-name) to configure `mbed-ls` to remap `target_id` to custom platforms name.

Note: Please make sure that remapping will present platforms name which can be distinguished by our build system and test tools. So it can't be random / arbitrary name.

### Checking if your platform is already supported by mbed-ls

```
$ mbedls --list
+------------------+----------------------+
| target_id_prefix | platform_name        |
+------------------+----------------------+
  ....
| 0183             | UBLOX_C027           |
| 0200             | KL25Z                |
| 0231             | K22F                 |
| 0240             | K64F                 |
  ....
| 9009             | ARCH_BLE             |
| 9900             | NRF51_MICROBIT       |
+------------------+----------------------+
```

Above command will let you list all platforms `mbed-ls` can detect and map its `target_id` to `platform_name`.
Note: `target_id_prefix` prefix is four characters long and determines `target_id` vendor and platform IDs.

## Build your project

You need to use your build system to build project. You can use `yotta` build system if your project if encapsulated in `yotta` module.

In other case you can use you need to use other build system which can build your project. Greenteas supports [test specification](https://github.com/ARMmbed/greentea#test-specification-json-formatted-input) file so make sure you will use build system with test specification support.

Build + test work flow should be as follow:

* Invoking custom build system:
```
$ build ...
```
Build system compiles and build all libraries, code and tests.
While building tests, build system should generate automatically test specification file called `test_spec.json`. Test specification file will be automatically read and loaded if it exists in current directory (directory in which `Greentea` is invoked). For more details on how to use command line go [here](https://github.com/ARMmbed/greentea#command-line-usage)

* Calling `Greentea` to [list all built test binaries](https://github.com/ARMmbed/greentea#command-line-usage):
```
$ mbedgt --list
```

* Calling `Greentea` to execute all tests:
```
$ mbedgt -V
```

# Run test case using Greentea

* Run all test cases

Command `mbedgt -V` will execute all tests build with build system.
Note: This may take a while and you probably do not want to run them all at once. You may want to cherry-pick tests by names and use command line switch `-n`.

* Cherry pick tests by names

Use comma separated test cases names witch command line option `-n`.
```
$ mbedgt -V -n test-case-name-basic,test-case-name-rtos
```

Read more [here](https://github.com/ARMmbed/greentea#cherry-pick-group-of-tests.

* Chery pick group of tests

Filter test case names witch command line option `-n` and test case name suffix `*` to filter with names `<test-case-name>...`.
```
$ mbedgt -V -n test-case-name*
```

Read more [here](https://github.com/ARMmbed/greentea#cherry-pick-tests).

## Running one test binary with htrun

While executing each test binary Greentea will explicitly pass control to and call `htrun` (command line tool name is `mbedhtrun`).
Below Greentea log with sequence calling `mbedhtrun` command line tool:
```
mbedgt: selecting test case observer...
        calling mbedhtrun: mbedhtrun -d E: -p COM228:9600 -f ".build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mail\TESTS-mbedmicro-rtos-mbed-mail.bin" -C 4 -c shell -m K64F -t 0240000029304e450038500878a3003cf131000097969900
```

Command executing `mbedhtrun` from Greentea context:
```
$ mbedhtrun -d E: -p COM228:9600 -f ".build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mail\TESTS-mbedmicro-rtos-mbed-mail.bin" -C 4 -c shell -m K64F -t 0240000029304e450038500878a3003cf131000097969900
```
Where:
* `-d E:` is definition of mount point which will be used to flash DUT.
* `-p COM228:9600` is definition of serial port with baudrate used for communication with DUT.
* `-f ".build\tests\K64F\GCC_ARM\TESTS\mbedmicro-rtos-mbed\mail\TESTS-mbedmicro-rtos-mbed-mail.bin"` is path to image we will use to flash DUT.
* `-C 4` is time we will wait after device is flashed. This time may vary depending on platform.
* `-c shell` is method used to copy binary onto DUT mount point.
* `-m K64F` is platform name, currently not used.
* `-t 0240000029304e450038500878a3003cf131000097969900` is TargetID of platform we will use. This useful option is passed by `Greentea` to `htrun` during process of auto-detection of test compatible platforms. Greentea uses `mbed-ls` to list all compatible platforms (by platform names) and maps it to TargetID.

This command with few modifications can be used by user to reproduce binary test run (flashing, reset and test execution). Use `--skip-flashing` flag of `mbedhtrun` to skip flashing phase in case you have the same binary already flashed on your device.

## Interpretting test results

### Terms used in `htrun` and `Greentea` output

Please check [this link](https://github.com/ARMmbed/greentea-client#terms) for details. Especially [test suite](https://github.com/ARMmbed/greentea-client#test-suite) and [test case](https://github.com/ARMmbed/greentea-client#test-case).

```
$ mbedgt -V -n TESTS-mbed_drivers*
```

### Test suite result

Test suite report describes what was the state of test binary after all test procedures were finished. In general we return one of three states in our reports:
* `OK` - all tests in test binary passed.
* `FAIL` - test binary itself behaved as expected but some test cases, assertions in test code failed.
* Undeifned state which can manifest itself as many other erroneous states. For example: `ERROR` or for example `TIMEOUT` - something went wrong with binary itself or test mechanism inside binary failed to instrument test code.

```
mbedgt: test suite report:
+--------------+---------------+----------------------------------+--------+--------------------+-------------+
| target       | platform_name | test suite                       | result | elapsed_time (sec) | copy_method |
+--------------+---------------+----------------------------------+--------+--------------------+-------------+
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | FAIL   | 13.3               | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-dev_null      | OK     | 13.14              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-echo          | FAIL   | 41.08              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | OK     | 12.11              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-rtc           | OK     | 21.6               | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | OK     | 12.87              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker        | OK     | 22.08              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_2      | OK     | 22.04              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_3      | OK     | 22.07              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-timeout       | OK     | 22.06              | shell       |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-wait_us       | OK     | 20.96              | shell       |
+--------------+---------------+----------------------------------+--------+--------------------+-------------+
mbedgt: test suite results: 2 FAIL / 9 OK
```

### Test cases results

Some test suites (test binaries) may use our in-house test hardness called [utest](https://github.com/ARMmbed/utest). `utest` test harness allows users to write set of test cases inside one binary. This allows us to add more test code inside test binaries and report results for each test case separately. Each test case may report `OK`, `FAIL` or `ERROR`.

```
mbedgt: test case report:
+--------------+---------------+----------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| target       | platform_name | test suite                       | test case                           | passed | failed | result | elapsed_time (sec) |
+--------------+---------------+----------------------------------+-------------------------------------+--------+--------+--------+--------------------+
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %e %E float formatting   | 1      | 0      | OK     | 1.01               |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %f %f float formatting   | 0      | 1      | FAIL   | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %g %g float formatting   | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %i %d integer formatting | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %u %d integer formatting | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: %x %E integer formatting | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: strpbrk                  | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-c_strings     | C strings: strtok                   | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-dev_null      | tests-mbed_drivers-dev_null         | 1      | 0      | OK     | 13.14              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-echo          | Echo server: x16                    | 1      | 0      | OK     | 16.54              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-echo          | Echo server: x32                    | 0      | 0      | ERROR  | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | Basic                               | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | Blinky                              | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | C++ heap                            | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-generic_tests | C++ stack                           | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-rtc           | RTC strftime                        | 1      | 0      | OK     | 10.14              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::equal                      | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::sort abs                   | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::sort greater               | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-stl_features  | STL std::transform                  | 1      | 0      | OK     | 0.0                |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker        | Timers: 2 x tickers                 | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_2      | Timers: 1x ticker                   | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-ticker_3      | Timers: 2x callbacks                | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-timeout       | Timers: toggle on/off               | 1      | 0      | OK     | 11.15              |
| K64F-GCC_ARM | K64F          | tests-mbed_drivers-wait_us       | Timers: wait_us                     | 1      | 0      | OK     | 10.14              |
+--------------+---------------+----------------------------------+-------------------------------------+--------+--------+--------+--------------------+
mbedgt: test case results: 1 FAIL / 23 OK / 1 ERROR
mbedgt: completed in 223.55 sec
mbedgt: exited with code 2
```
