import os
import json
import csv
import subprocess
from pathlib import Path


def get_input(name: str) -> str:
    value = os.getenv(f'INPUT_{name.upper().replace("-", "_")}')
    return value


def set_output(name: str, value: str):
    output_file = os.getenv('GITHUB_OUTPUT', None)
    if output_file:
        with open(output_file, 'a') as f:
            f.write(f'{name}={value}\n')
    else:
        raise EnvironmentError('GITHUB_OUTPUT environment variable is not set.')


def set_failed(message: str):
    print(f'::error::{message}')
    exit(1)


def info(message: str):
    print(message)


def run():
    try:
        suffixes_raw = get_input('suffixes')
        suffixes = suffixes_raw.split(',') if suffixes_raw else []
        include_directories_raw = get_input('include-directories')
        include_directories = include_directories_raw.split(',')
        exclude_directories_raw = get_input('exclude-directories')
        exclude_directories = exclude_directories_raw.split(',')
        exclude_files_raw = get_input('exclude-files')
        exclude_files = exclude_files_raw.split(',')
        case_sensitivity = get_input('case-sensitivity') == 'true'
        logic = get_input('logic') == 'true'
        report_format = get_input('report-format')
        verbose_logging = get_input('verbose-logging') == 'true'
        fail_on_violations = get_input('fail-on-violations') == 'true'

        if verbose_logging:
            info(f'Suffixes: {suffixes}')
            info(f'Include directories: {include_directories}')
            info(f'Exclude directories: {exclude_directories}')
            info(f'Exclude files: {exclude_files}')
            info(f'Case sensitivity: {case_sensitivity}')
            info(f'Logic: {logic}')
            info(f'Report format: {report_format}')
            info(f'Fail on violations: {fail_on_violations}')

        violations_count = 0
        violations = []

        def scan_directory(directory: Path, level: int = 1):
            if verbose_logging:
                info(f'Scanning directory: {directory}')

            nonlocal violations_count
            nonlocal violations
            for item in directory.iterdir():
                if item.is_dir():
                    if level == 1 and item.name in exclude_directories:
                        if verbose_logging:
                            info(f'Skipping excluded directory: {item.name}')
                    else:
                        scan_directory(item, level + 1)
                else:
                    for include_dir in include_directories:
                        # Check if item path contains the include directory
                        if str(item).__contains__(include_dir):
                            # CHeck if item is defined as an exception to exclude
                            if item.name in exclude_files:
                                if verbose_logging:
                                    info(f'Excluded file: {item}')
                                continue

                            check_filename_with_extension = item.name if case_sensitivity else item.name.lower()
                            check_filename = check_filename_with_extension.split(".")[0]
                            matches_suffix = any(
                                (check_filename.endswith(suffix) if logic else suffix in check_filename)
                                for suffix in (suffixes if case_sensitivity else map(str.lower, suffixes))
                            )

                            if not matches_suffix:
                                if verbose_logging:
                                    info(f'Violating file: {item}')
                                violations_count += 1
                                violations.append(str(item))
                            else:
                                if verbose_logging:
                                    info(f'Valid file: {item}')

        scan_directory(Path.cwd())

        set_output('conventions-violations', str(violations_count))

        if report_format == 'console' or verbose_logging:
            print(f'Total violations: {violations_count}')
            print(f'Violating files: {violations}')

        if report_format == 'csv':
            with open('violations.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([[violation] for violation in violations])
            set_output('report-path', 'violations.csv')
        elif report_format == 'json':
            with open('violations.json', mode='w') as file:
                json.dump({'violations': violations}, file)
            set_output('report-path', 'violations.json')

        if fail_on_violations and violations_count > 0:
            set_failed(f'There are {violations_count} test file naming convention violations.')

    except Exception as error:
        print(f'Action failed with error: {error}')
        set_failed(f'Action failed with error: {error}')


if __name__ == '__main__':
    run()
