#
# Copyright 2024 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
This script is designed to validate file naming conventions in a project. It checks if files in specified paths
match given name patterns, while allowing exclusions and generating reports in various formats.

Features:
- Validate file names against specified patterns.
- Support for excluding specific files or directories.
- Generate reports in console, CSV, or JSON formats.
- Configurable logging for detailed output.
- Fail the process if violations are detected (optional).

Environment Variables:
- INPUT_NAME_PATTERNS: Comma-separated list of file name patterns to match.
- INPUT_PATHS: Comma-separated list of glob patterns to search for files.
- INPUT_EXCLUDES: Comma-separated list of glob patterns to exclude files.
- INPUT_REPORT_FORMAT: Format of the report ('console', 'csv', or 'json').
- INPUT_VERBOSE_LOGGING: Enable detailed logging ('true' or 'false').
- INPUT_FAIL_ON_VIOLATION: Fail the process if violations are found ('true' or 'false').
- RUNNER_DEBUG: Enable debug mode for GitHub Actions.

Usage:
Run this script as part of a GitHub Action or locally to enforce file naming conventions.
"""

import fnmatch
import glob
import logging
import os
import json
import csv
import sys
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


INPUT_NAME_PATTERNS = "INPUT_NAME_PATTERNS"
INPUT_PATHS = "INPUT_PATHS"
INPUT_EXCLUDES = "INPUT_EXCLUDES"
INPUT_REPORT_FORMAT = "INPUT_REPORT_FORMAT"
INPUT_VERBOSE_LOGGING = "INPUT_VERBOSE_LOGGING"
INPUT_FAIL_ON_VIOLATION = "INPUT_FAIL_ON_VIOLATION"

RUNNER_DEBUG = "RUNNER_DEBUG"


def get_action_list_input(name: str) -> list[str]:
    """
    Get a list of input values from the environment variable.

    Parameters:
        name (str): The name of the environment variable to retrieve.

    Returns:
        list[str]: A list of input values, split by commas.
    """
    # Note: this is cleanup when input defined by multiple lines
    value = os.getenv(name)
    if value is None:
        return []
    return value.replace("\n", "").split(",")


def get_action_input(name: str) -> Optional[str]:
    """
    Get a single input value from the environment variable.

    Parameters:
        name (str): The name of the environment variable to retrieve.

    Returns:
        Optional[str]: The value of the environment variable, or None if not set.
    """
    res = os.getenv(name)
    return res.lower() if res else None


def set_action_output(name: str, value: str, default_output_path: str = "default_output.txt") -> None:
    """
    Set the output value for a GitHub Action.

    Parameters:
        name (str): The name of the output variable.
        value (str): The value to set for the output variable.
        default_output_path (str): The default path to the output file.

    Returns:
        None
    """
    output_file = os.getenv("GITHUB_OUTPUT", default_output_path)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"{name}={value}\n")


def set_action_failed(message: str) -> None:
    """
    Set the action as failed and log the error message.

    Parameters:
        message (str): The error message to log.

    Returns:
        None
    """
    logging.error(message)
    sys.exit(1)


def find_non_matching_files(name_patterns, paths, excludes) -> list[str]:
    """
    Find files that do not match the specified name patterns in the given paths.

    Parameters:
        name_patterns (list[str]): List of name patterns to match.
        paths (list[str]): List of glob patterns to search for files.
        excludes (list[str]): List of glob patterns to exclude files.

    Returns:
        list[str]: List of files that do not match the name patterns.

    """
    non_matching_files = []

    # Iterate over each glob pattern to find files
    for path in paths:
        for file in glob.glob(path, recursive=True):
            # Check if the file matches any of the exclude patterns
            logging.debug("Checking file: %s", file)
            for e in excludes:
                logging.debug("Checking exclude: %s", e)
                if fnmatch.fnmatch(file, e):
                    logging.debug("Excluding file: %s", file)
                else:
                    logging.debug("File not excluded: %s", file)

            if any(fnmatch.fnmatch(file, e) for e in excludes):
                continue
            # Check if the file matches any of the name patterns
            if os.path.isfile(file) and not any(fnmatch.fnmatch(file, p) for p in name_patterns):
                non_matching_files.append(file)

    return non_matching_files


def run() -> None:
    """
    Main function to run the file naming convention validation.
    """
    try:
        name_patterns = get_action_list_input(INPUT_NAME_PATTERNS)
        paths = get_action_list_input(INPUT_PATHS)
        excludes = get_action_list_input(INPUT_EXCLUDES)
        report_format = get_action_input(INPUT_REPORT_FORMAT)
        verbose_logging = get_action_input(INPUT_VERBOSE_LOGGING) == "true"
        fail_on_violation = get_action_input(INPUT_FAIL_ON_VIOLATION) == "true"

        if int(os.getenv(RUNNER_DEBUG, "0")) or verbose_logging:
            logging.getLogger().setLevel(logging.DEBUG)

        logging.debug("Name patterns: %s", name_patterns)
        logging.debug("Paths: %s", paths)
        logging.debug("Excludes: %s", excludes)
        logging.debug("Report format: %s", report_format)
        logging.debug("Fail on violations: %s", fail_on_violation)

        violations = find_non_matching_files(name_patterns, paths, excludes)
        violation_count = len(violations)

        set_action_output("violation-count", str(violation_count))

        logging.info("Total violations: %s", violation_count)

        if report_format == "console" or verbose_logging:
            logging.info("Violating files: %s", violations)

        if report_format == "csv":
            with open("violations.csv", mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows([[violation] for violation in violations])
            set_action_output("report-path", "violations.csv")
        elif report_format == "json":
            with open("violations.json", mode="w", encoding="utf-8") as file:
                json.dump({"violations": violations}, file)
            set_action_output("report-path", "violations.json")

        if fail_on_violation and violation_count > 0:
            set_action_failed(f"There are {violation_count} test file naming convention violations.")

    except ValueError as error:
        logging.error("Value error occurred: %s", error)
        set_action_failed(f"Action failed with ValueError: {error}")
    except FileNotFoundError as error:
        logging.error("File not found: %s", error)
        set_action_failed(f"Action failed with FileNotFoundError: {error}")
    except KeyError as error:
        logging.error("Key error: %s", error)
        set_action_failed(f"Action failed with KeyError: {error}")
    # pylint: disable=W0718
    except Exception as error:
        logging.error("An unexpected error occurred: %s", error)
        set_action_failed(f"Action failed with an unexpected error: {error}")


if __name__ == "__main__":
    run()
