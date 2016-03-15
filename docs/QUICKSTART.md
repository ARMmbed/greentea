# Table of content



# Description

This document is a simple cookbook introducing the testing facilities available for mbed 3.0. ```Greentea``` test automation tools and its device counterpart ```greentea-client``` are used to build test suites and test cases. From this document you will learn how to:

* Create simple tests inside yotta modules. To read the full yotta documentation go [here](http://docs.yottabuild.org/reference/commands.html).
* Create test cases with host test support (additional instrumentation from host side).
* Use [unity](https://github.com/ARMmbed/unity) and [utest](https://github.com/ARMmbed/unity) to improve your tests.

This document provides examples for all three methods of testing.

Both test tools and host test scripts are written in Python 2.7. This means some knowledge about Python development is required.

## Vocabulary

* Test suite
* Test case
* Code coverage
* gcov, LCOV

## Test resources

* Greentea
* htrun
* mbedls
* greentea-client

## Archtecture

* mbed-drivers/test_env.h vs greentea-client/test_env.h
* porting between 0.1.x and 0.2.x

* greentea-client
* key-value protocol
* protocol flow
* events / messages

## Test process

* Flow
* Reporting
* Error handling

## Code coverage

### Limitations

## tests in yotta package
Place your test case under a sub-directory of the ```\test``` directory located in your yotta package:

Note: For details please check ['The ```test``` Directory' section of the yotta documentation](http://docs.yottabuild.org/tutorial/testing.html).

```
\your-yotta-pacjage-dir
  \source
    ...
  \test
    \test_case_1
      source.cpp
      test-case-1.cpp
    \test_case_2
      test-case-2.cpp
    ...
```

All tests in ```\test```'s sub-directories will be built by yotta, and the test case binaries will be stored in the ```\build\<target-name>\test``` directory where ```<target-name>``` is the yotta target used to build tests.

It is your responsibility to provide test cases in the ```\test``` directory so they will build to target-specific binaries. It is test suite's (mbed-greentea) responsibility to flash all test binaries and perform test supervision by calling the host test from the mbed-host-tests package.

## yotta testDependencies
The [testDependencies](http://docs.yottabuild.org/reference/module.html#testDependencies) section can be used to list modules that are only depended on by tests. They will not normally be installed if your module is installed as a dependency of another.

In our case we need to add testDependencies to ```mbed-sdk-private``` so we can include test-related macros from the ```mbed/test_env.h``` header file. Test macros will be explained in the next sections of this document.

# Test development

* Concepts etc.

## Creating a simple test suite

* Test suite == test case

## Using unity

## Using utest & unity

* Test cases
* MINAR usage
* Limitations

## Host test support

# Porting guild from 0.1.x to 0.2.x

# Examples
In this section we will show you how to create a few flavours of test cases for your yotta package with mbed-greentea and mbed-host-tests.

* Lot's of examples and links
