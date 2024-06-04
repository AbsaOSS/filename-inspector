import os
import json
import csv
from pathlib import Path


def get_input(name: str) -> str:
    value = os.getenv(f'INPUT_{name.upper()}')
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
        include_directories_raw = get_input('include_directories')
        include_directories = include_directories_raw.split(',')
        excludes_raw = get_input('excludes')
        excludes = excludes_raw.split(',')
        case_sensitive = get_input('case_sensitive') == 'true'
        contains = get_input('contains') == 'true'
        report_format = get_input('report_format')
        verbose_logging = get_input('verbose_logging') == 'true'
        fail_on_violation = get_input('fail_on_violation') == 'true'

        if verbose_logging:
            info(f'Suffixes: {suffixes}')
            info(f'Include directories: {include_directories}')
            info(f'Excludes: {excludes}')
            info(f'Case sensitivity: {case_sensitive}')
            info(f'Contains: {contains}')
            info(f'Report format: {report_format}')
            info(f'Fail on violations: {fail_on_violation}')

        violation_count = 0
        violations = []

        def scan_directory(directory: Path, level: int = 1):
            if verbose_logging:
                info(f'Scanning directory: {directory}')

            nonlocal violation_count
            nonlocal violations
            for item in directory.iterdir():
                if item.is_dir():
                    scan_directory(item, level + 1)
                else:
                    for include_dir in include_directories:
                        # Check if item path contains the include directory
                        if str(item).__contains__(include_dir):
                            # Check if item is defined as an exception to exclude
                            if item.name in excludes:
                                if verbose_logging:
                                    info(f'Excluded file: {item}')
                                continue

                            check_filename_with_extension = item.name if case_sensitive else item.name.lower()
                            check_filename = check_filename_with_extension.split(".")[0]
                            matches_suffix = any(
                                (check_filename.endswith(suffix) if contains else suffix in check_filename)
                                for suffix in (suffixes if case_sensitive else map(str.lower, suffixes))
                            )

                            if not matches_suffix:
                                if verbose_logging:
                                    info(f'Violating file: {item}')
                                violation_count += 1
                                violations.append(str(item))
                            else:
                                if verbose_logging:
                                    info(f'Valid file: {item}')

        scan_directory(Path.cwd())

        set_output('violation_count', str(violation_count))

        if report_format == 'console' or verbose_logging:
            print(f'Total violations: {violation_count}')
            print(f'Violating files: {violations}')

        if report_format == 'csv':
            with open('violations.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([[violation] for violation in violations])
            set_output('report_path', 'violations.csv')
        elif report_format == 'json':
            with open('violations.json', mode='w') as file:
                json.dump({'violations': violations}, file)
            set_output('report_path', 'violations.json')

        if fail_on_violation and violation_count > 0:
            set_failed(f'There are {violation_count} test file naming convention violations.')

    except Exception as error:
        print(f'Action failed with error: {error}')
        set_failed(f'Action failed with error: {error}')


if __name__ == '__main__':
    run()
