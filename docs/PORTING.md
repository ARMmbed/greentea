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
  * [Generating reports](#generating-reports)
  * [Troubleshooting](#troubleshooting)

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

Command itself:
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
## Generating reports
## Troubleshooting
