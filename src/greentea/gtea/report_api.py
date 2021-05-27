#
# Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""API to export test results in various formats."""
from pathlib import Path


def export_to_file(file_name, payload):
    """! Simple file dump used to store reports on disk
    @param file_name Report file name (with path if needed)
    @param payload Data to store inside file
    @return True if report save was successful
    """
    try:
        with open(file_name, "w") as f:
            f.write(payload)
    except IOError as e:
        print(f"Exporting report to file failed: {str(e)}")
        return False
    return True


def exporter_json(test_result_ext, test_suite_properties=None):
    """! Exports test results to indented JSON format
    @details This is a machine friendly format
    """
    import json

    for target in test_result_ext.values():
        for suite in target.values():
            try:
                suite["single_test_output"] = suite["single_test_output"]
            except KeyError:
                pass
    return json.dumps(test_result_ext, indent=4)


def exporter_text(test_result_ext, test_suite_properties=None):
    """! Exports test results to text formatted output
    @details This is a human friendly format
    @return Tuple with table of results and result quantity summary string
    """
    from prettytable import PrettyTable, HEADER

    # TODO: export to text, preferably to PrettyTable (SQL like) format
    cols = [
        "target",
        "platform_name",
        "test suite",
        "result",
        "elapsed_time (sec)",
        "copy_method",
    ]
    pt = PrettyTable(cols, junction_char="|", hrules=HEADER)
    pt.align = "l"
    pt.padding_width = 1

    result_dict = {}  # Used to print test suite results

    for target_name in sorted(test_result_ext):
        test_results = test_result_ext[target_name]
        row = []
        for test_name in sorted(test_results):
            test = test_results[test_name]

            # Grab quantity of each test result
            if test["single_test_result"] in result_dict:
                result_dict[test["single_test_result"]] += 1
            else:
                result_dict[test["single_test_result"]] = 1

            row.append(target_name)
            row.append(test["platform_name"])
            row.append(test_name)
            row.append(test["single_test_result"])
            row.append(round(test["elapsed_time"], 2))
            row.append(test["copy_method"])
            pt.add_row(row)
            row = []

    result_pt = pt.get_string()
    result_res = " / ".join(
        [f"{value} {key}" for key, value in result_dict.items() if value != 0]
    )
    return result_pt, result_res


def exporter_testcase_text(test_result_ext):
    """! Exports test case results to text formatted output
    @param test_result_ext Extended report from Greentea
    @details This is a human friendly format
    @return Tuple with table of results and result quantity summary string
    """
    from prettytable import PrettyTable, HEADER

    # TODO: export to text, preferably to PrettyTable (SQL like) format
    cols = [
        "target",
        "platform_name",
        "test suite",
        "test case",
        "passed",
        "failed",
        "result",
        "elapsed_time (sec)",
    ]
    pt = PrettyTable(cols, junction_char="|", hrules=HEADER)
    for col in cols:
        pt.align[col] = "l"
    pt.padding_width = 1  # One space between column edges and contents (default)

    result_testcase_dict = {}  # Used to print test case results

    for target_name in sorted(test_result_ext):
        test_results = test_result_ext[target_name]
        row = []
        for test_suite_name in sorted(test_results):
            test = test_results[test_suite_name]

            # testcase_result stores info about test case results
            testcase_result = test["testcase_result"]
            #   "testcase_result": {
            #       "STRINGS004": {
            #           "duration": 0.009999990463256836,
            #           "time_start": 1453073018.275,
            #           "time_end": 1453073018.285,
            #           "result": 1
            #       },

            for tc_name in sorted(testcase_result):
                duration = testcase_result[tc_name].get("duration", 0.0)
                # result = testcase_result[tc_name].get('result', 0)
                passed = testcase_result[tc_name].get("passed", 0)
                failed = testcase_result[tc_name].get("failed", 0)
                result_text = testcase_result[tc_name].get("result_text", "UNDEF")

                # Grab quantity of each test result
                if result_text in result_testcase_dict:
                    result_testcase_dict[result_text] += 1
                else:
                    result_testcase_dict[result_text] = 1

                row.append(target_name)
                row.append(test["platform_name"])
                row.append(test_suite_name)
                row.append(tc_name)
                row.append(passed)
                row.append(failed)
                row.append(result_text)
                row.append(round(duration, 2))
                pt.add_row(row)
                row = []

    result_pt = pt.get_string()
    result_res = " / ".join(
        [f"{value} {key}" for key, value in result_testcase_dict.items() if value != 0]
    )
    return result_pt, result_res


def exporter_testcase_junit(test_result_ext, test_suite_properties=None):
    """! Export test results in JUnit XML compliant format
    @param test_result_ext Extended report from Greentea
    @param test_spec Dictionary of test build names to test suite properties
    @details This function will import junit_xml library to perform report conversion
    @return String containing Junit XML formatted test result output
    """
    from junit_xml import TestSuite, TestCase

    test_suites = []

    for target_name in test_result_ext:
        test_results = test_result_ext[target_name]
        for test_suite_name in test_results:
            test = test_results[test_suite_name]
            tc_stdout = test["single_test_output"]

            # testcase_result stores info about test case results
            testcase_result = test["testcase_result"]
            #   "testcase_result": {
            #       "STRINGS004": {
            #           "duration": 0.009999990463256836,
            #           "time_start": 1453073018.275,
            #           "time_end": 1453073018.285,
            #           "result": 1
            #       },

            test_cases = []

            for tc_name in sorted(testcase_result.keys()):
                duration = testcase_result[tc_name].get("duration", 0.0)
                utest_log = testcase_result[tc_name].get("utest_log", "")
                result_text = testcase_result[tc_name].get("result_text", "UNDEF")

                tc_stderr = "\n".join(utest_log)
                tc_class = target_name + "." + test_suite_name

                if result_text == "SKIPPED":
                    # Skipped test cases do not have logs and we do not want to put
                    # whole log inside JUNIT for skipped test case
                    tc_stderr = str()

                tc = TestCase(tc_name, tc_class, duration, tc_stdout, tc_stderr)

                if result_text == "FAIL":
                    tc.add_failure_info(result_text)
                elif result_text == "SKIPPED":
                    tc.add_skipped_info(result_text)
                elif result_text != "OK":
                    tc.add_error_info(result_text)

                test_cases.append(tc)

            ts_name = target_name

            if test_suite_properties is not None:
                test_build_properties = test_suite_properties.get(target_name, None)
            else:
                test_build_properties = None

            ts = TestSuite(ts_name, test_cases, properties=test_build_properties)
            test_suites.append(ts)

    return TestSuite.to_xml_string(test_suites)


TEST_RESULT_COLOURS = {
    "OK": "limegreen",
    "FAIL": "darkorange",
    "ERROR": "orangered",
    "SKIPPED": "lightsteelblue",
    "UNDEF": "Red",
    "IOERR_COPY": "DarkSalmon",
    "IOERR_DISK": "DarkSalmon",
    "IOERR_SERIAL": "DarkSalmon",
    "TIMEOUT": "DarkKhaki",
    "NO_IMAGE": "DarkSalmon",
    "NOT_RAN": "grey"
    # 'MBED_ASSERT': "",
    # 'BUILD_FAILED': "",
}

TEST_RESULT_DEFAULT_COLOUR = "lavender"


def get_result_colour_class_css():
    """! Get the CSS for the colour classes
    @details Returns a string of the CSS classes that are used to colour the different results
    @return String containing the CSS classes
    """
    colour_class_template = """

            .result-{} {{
                background-color: {};
            }}"""

    # Create CSS classes for all of the allocated colours
    css = ""
    for result, colour in TEST_RESULT_COLOURS.items():
        css += colour_class_template.format(result.lower().replace("_", "-"), colour)

    css += colour_class_template.format("other", TEST_RESULT_DEFAULT_COLOUR)

    return css


def get_result_colour_class(result):
    """! Get the CSS colour class representing the result
    @param result The result of the test
    @details Returns a string of the CSS colour class of the result, or returns the default if the result is not found
    @return String containing the CSS colour class
    """
    if result in TEST_RESULT_COLOURS:
        return f"result-{result.lower().replace('_', '-')}"
    else:
        return "result-other"


def get_dropdown_html(
    div_id,
    dropdown_name,
    content,
    title_classes="",
    output_text=False,
    sub_dropdown=False,
):
    """! Get the HTML for a dropdown menu
    @param title_classes A space separated string of css classes on the title
    @param div_id The id of the dropdowns menus inner div
    @param dropdown_name The name on the dropdown menu
    @param dropdown_classes A space separated string of css classes on the inner div
    @param content The content inside of the dropdown menu
    @details This function will create the HTML for a dropdown menu
    @return String containing the HTML of dropdown menu
    """
    dropdown_template = """
        <div class="nowrap">
            <p class="dropdown no-space {}" onclick="toggleDropdown('{}')">&#9650 {}</p>
            <div id="{}" class="dropdown-content{}">{}
            </div>
        </div>"""

    dropdown_classes = ""
    if output_text:
        dropdown_classes += " output-text"
    if sub_dropdown:
        dropdown_classes += " sub-dropdown-content"

    return dropdown_template.format(
        title_classes, div_id, dropdown_name, div_id, dropdown_classes, content,
    )


def get_result_overlay_testcase_dropdown(
    result_div_id, index, testcase_result_name, testcase_result
):
    """! Get the HTML for an individual testcase dropdown
    @param result_div_id The div id used for the test
    @param index The index of the testcase for the divs unique id
    @param testcase_result_name The name of the testcase
    @param testcase_result The results of the testcase
    @details This function will create the HTML for a testcase dropdown
    @return String containing the HTML of the testcases dropdown
    """

    import datetime

    testcase_result_template = """Result: {}
                                        Elapsed Time: {:.2f}
                                        Start Time: {}
                                        End Time: {}
                                        Failed: {}
                                        Passed: {}
                                        <br>{}"""

    # Create unique ids to reference the divs
    testcase_div_id = f"{result_div_id}_testcase_result_{index}"
    testcase_utest_div_id = f"{testcase_div_id}_utest"

    testcase_utest_log_dropdown = get_dropdown_html(
        testcase_utest_div_id,
        "uTest Log",
        "\n".join(testcase_result.get("utest_log", "n/a")).rstrip("\n"),
        output_text=True,
        sub_dropdown=True,
    )

    time_start = "n/a"
    time_end = "n/a"
    if "time_start" in testcase_result.keys():
        time_start = datetime.datetime.fromtimestamp(
            testcase_result["time_start"]
        ).strftime("%d-%m-%Y %H:%M:%S.%f")
    if "time_end" in testcase_result.keys():
        time_end = datetime.datetime.fromtimestamp(
            testcase_result["time_end"]
        ).strftime("%d-%m-%Y %H:%M:%S.%f")

    testcase_info = testcase_result_template.format(
        testcase_result.get("result_text", "n/a"),
        testcase_result.get("duration", "n/a"),
        time_start,
        time_end,
        testcase_result.get("failed", "n/a"),
        testcase_result.get("passed", "n/a"),
        testcase_utest_log_dropdown,
    )

    testcase_class = get_result_colour_class(testcase_result["result_text"])
    testcase_dropdown = get_dropdown_html(
        testcase_div_id,
        f"Testcase: {testcase_result_name}<br>",
        testcase_info,
        title_classes=testcase_class,
        sub_dropdown=True,
    )
    return testcase_dropdown


def get_result_overlay_testcases_dropdown_menu(result_div_id, test_results):
    """! Get the HTML for a test overlay's testcase dropdown menu
    @param result_div_id The div id used for the test
    @param test_results The results of the test
    @details This function will create the HTML for the result overlay's testcases dropdown menu
    @return String containing the HTML test overlay's testcase dropdown menu
    """
    testcase_results_div_id = f"{result_div_id}_testcase"
    testcase_results_info = ""

    # Loop through the test cases giving them a number to create a unique id
    for index, (testcase_result_name, testcase_result) in enumerate(
        test_results["testcase_result"].items()
    ):
        testcase_results_info += get_result_overlay_testcase_dropdown(
            result_div_id, index, testcase_result_name, testcase_result
        )

    result_testcases_dropdown = get_dropdown_html(
        testcase_results_div_id,
        "Testcase Results",
        testcase_results_info,
        sub_dropdown=True,
    )

    return result_testcases_dropdown


def get_result_overlay_dropdowns(result_div_id, test_results):
    """! Get the HTML for a test overlay's dropdown menus
    @param result_div_id The div id used for the test
    @param test_results The results of the test
    @details This function will create the HTML for the dropdown menus of an overlay
    @return String containing the HTML test overlay's dropdowns
    """
    # The HTML for the dropdown containing the output of the test
    result_output_div_id = f"{result_div_id}_output"
    result_output_dropdown = get_dropdown_html(
        result_output_div_id,
        "Test Output",
        test_results["single_test_output"].rstrip("\n"),
        output_text=True,
    )

    if len(test_results):
        result_overlay_dropdowns = (
            result_output_dropdown
            + get_result_overlay_testcases_dropdown_menu(result_div_id, test_results)
        )
    else:
        result_overlay_dropdowns = result_output_dropdown

    return result_overlay_dropdowns


def get_result_overlay(result_div_id, test_name, platform, toolchain, test_results):
    """! Get the HTML for a test's overlay
    @param result_div_id The div id used for the test
    @param test_name The name of the test the overlay is for
    @param platform The name of the platform the test was performed on
    @param toolchain The name of toolchain the test was performed on
    @param test_results The results of the test
    @details This function will create the HTML of an overlay to display additional information on a test
    @return String containing the HTML test overlay
    """
    overlay_template = """
    <div id="{}" class="overlay">
        <div class="overlay-content" onclick="event.stopPropagation()">
            <p class="no-space">
                <span class="no-space test-title-font">
                <b>Test: {}
                <a class="close-button" onclick="toggleOverlay('{}')">x
                </a></b>
                </span>
                <span class="no-space test-result-title-font">Result: {}</span><br>
                <b>Platform: {} - Toolchain: {}</b>
                Elapsed Time: {:.2f} seconds
                Build Path: {}
                Absolute Build Path: {}
                Copy Method: {}
                Image Path: {}
            </p>{}
        </div>
    </div>"""

    overlay_dropdowns = get_result_overlay_dropdowns(result_div_id, test_results)

    return overlay_template.format(
        result_div_id,
        test_name,
        result_div_id,
        test_results["single_test_result"],
        platform,
        toolchain,
        test_results["elapsed_time"],
        test_results["build_path"],
        test_results["build_path_abs"],
        test_results["copy_method"],
        test_results["image_path"],
        overlay_dropdowns,
    )


def exporter_html(test_result_ext, test_suite_properties=None):
    """! Export test results as HTML
    @param test_result_ext Extended report from Greentea
    @details This function will create a user friendly HTML report
    @return String containing the HTML output
    """
    result_cell_template = """
                <td>
                    <div class="result {}" onclick="toggleOverlay('{}')">
                        <center>{}  -  {}&#37; ({}/{})</center>
                        {}
                    </div>
                </td>"""
    platform_template = """<tr>
                <td rowspan="2" class="level_header">
                    <center>Tests</center>
                </td>{}
            </tr>
            <tr>
                {}
            </tr>"""

    unique_test_names = set()
    platforms_toolchains = {}
    # Populate a set of all of the unique tests
    for platform_toolchain, test_list in test_result_ext.items():
        # Format of string is <PLATFORM>-<TOOLCHAIN>
        # <PLATFORM> can however contain '-' such as "frdm-k64f"
        # <TOOLCHAIN> is split with '_' fortunately, as in "gcc_arm"
        platform, toolchain = platform_toolchain.rsplit("-", 1)
        if platform in platforms_toolchains:
            platforms_toolchains[platform].append(toolchain)
        else:
            platforms_toolchains[platform] = [toolchain]

        for test_name in test_list:
            unique_test_names.add(test_name)

    table = ""
    platform_row = ""
    toolchain_row = ""

    platform_cell_template = """
                <td colspan="{}" class="level_header">
                    <center>{}</center>
                </td>"""
    center_cell_template = """
                <td class="level_header">
                    <center>{}</center>
                </td>"""

    for platform, toolchains in platforms_toolchains.items():
        platform_row += platform_cell_template.format(len(toolchains), platform)
        for toolchain in toolchains:
            toolchain_row += center_cell_template.format(toolchain)
    table += platform_template.format(platform_row, toolchain_row)

    test_cell_template = """
                <td class="test-column">{}</td>"""
    row_template = """
            <tr>{}
            </tr>"""

    for test_name in unique_test_names:
        this_row = test_cell_template.format(test_name)
        for platform, toolchains in platforms_toolchains.items():
            for toolchain in toolchains:
                test_results = None

                if test_name in test_result_ext[f"{platform}-{toolchain}"]:
                    test_results = test_result_ext[f"{platform}-{toolchain}"][test_name]
                else:
                    test_results = {
                        "single_test_result": "NOT_RAN",
                        "elapsed_time": 0.0,
                        "build_path": "N/A",
                        "build_path_abs": "N/A",
                        "copy_method": "N/A",
                        "image_path": "N/A",
                        "single_test_output": "N/A",
                        "platform_name": platform,
                        "test_bin_name": "N/A",
                        "testcase_result": {},
                    }

                test_results["single_test_passes"] = 0
                test_results["single_test_count"] = 0
                result_div_id = (
                    f"target_{platform}_toolchain_{toolchain}_test_"
                    + test_name.replace("-", "_")
                )

                result_overlay = get_result_overlay(
                    result_div_id, test_name, platform, toolchain, test_results
                )

                for testcase_result in test_results["testcase_result"].values():
                    test_results["single_test_passes"] += testcase_result["passed"]
                    test_results["single_test_count"] += 1

                result_class = get_result_colour_class(
                    test_results["single_test_result"]
                )
                if test_results["single_test_count"]:
                    percent_pass = int(
                        (test_results["single_test_passes"] * 100.0)
                        / test_results["single_test_count"]
                    )
                else:
                    percent_pass = 100
                this_row += result_cell_template.format(
                    result_class,
                    result_div_id,
                    test_results["single_test_result"],
                    percent_pass,
                    test_results["single_test_passes"],
                    test_results["single_test_count"],
                    result_overlay,
                )

        table += row_template.format(this_row)

    # Add the numbers of columns to make them have the same width
    html_template = (
        Path(__file__).parent / "templates" / "report_html.tmpl"
    ).read_text()
    return html_template.format(
        get_result_colour_class_css(), len(test_result_ext), table
    )


def exporter_memory_metrics_csv(test_result_ext, test_suite_properties=None):
    """! Export memory metrics as CSV
    @param test_result_ext Extended report from Greentea
    @details This function will create a CSV file that is parsable via CI software
    @return String containing the CSV output
    """

    metrics_report = {}

    for target_name in test_result_ext:
        test_results = test_result_ext[target_name]
        for test_suite_name in test_results:
            test = test_results[test_suite_name]

            if test.get("memory_metrics"):
                memory_metrics = test["memory_metrics"]

                if "max_heap" in memory_metrics:
                    report_key = f"{target_name}_{test_suite_name}_max_heap_usage"
                    metrics_report[report_key] = memory_metrics["max_heap"]

                if "reserved_heap" in memory_metrics:
                    report_key = f"{target_name}_{test_suite_name}_reserved_heap_usage"
                    metrics_report[report_key] = memory_metrics["reserved_heap"]

                if "thread_stack_summary" in memory_metrics:
                    thread_stack_summary = memory_metrics["thread_stack_summary"]

                    if "max_stack_size" in thread_stack_summary:
                        report_key = f"{target_name}_{test_suite_name}_max_stack_size"
                        metrics_report[report_key] = thread_stack_summary[
                            "max_stack_size"
                        ]

                    if "max_stack_usage" in thread_stack_summary:
                        report_key = f"{target_name}_{test_suite_name}_max_stack_usage"
                        metrics_report[report_key] = thread_stack_summary[
                            "max_stack_usage"
                        ]

                    if "max_stack_usage_total" in thread_stack_summary:
                        report_key = (
                            f"{target_name}_{test_suite_name}_max_stack_usage_total"
                        )
                        metrics_report[report_key] = thread_stack_summary[
                            "max_stack_usage_total"
                        ]

                    if "reserved_stack_total" in thread_stack_summary:
                        report_key = (
                            f"{target_name}_{test_suite_name}_reserved_stack_total"
                        )
                        metrics_report[report_key] = thread_stack_summary[
                            "reserved_stack_total"
                        ]

    column_names = sorted(metrics_report.keys())
    column_values = [str(metrics_report[x]) for x in column_names]

    return f"{','.join(column_names)}\n{','.join(column_values)}"
