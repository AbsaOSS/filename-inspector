import fnmatch
import glob
import os
import json
import csv


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


def find_non_matching_files(glob_patterns, suffix_patterns, exclude_patterns):
    def matches_suffix(file, suffix_patterns):
        for pattern in suffix_patterns:
            if fnmatch.fnmatch(file, pattern):
                return True
        return False

    def matches_exclude(file, exclude_patterns):
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file, pattern):
                return True
        return False

    non_matching_files = []

    # Iterate over each glob pattern to find files
    for pattern in glob_patterns:
        for file in glob.glob(pattern, recursive=True):
            # Check if the file matches any of the exclude patterns
            if matches_exclude(file, exclude_patterns):
                continue
            # Check if the file matches any of the suffix patterns
            if not matches_suffix(file, suffix_patterns):
                non_matching_files.append(file)

    return non_matching_files


def run():
    try:
        suffixes_raw = get_input('suffixes')
        suffixes = suffixes_raw.split(',') if suffixes_raw else []
        paths_raw = get_input('paths')
        paths = paths_raw.split(',')
        excludes_raw = get_input('excludes')
        excludes = excludes_raw.split(',')
        report_format = get_input('report_format')
        verbose_logging = get_input('verbose_logging') == 'true'
        fail_on_violation = get_input('fail_on_violation') == 'true'

        if verbose_logging:
            info(f'Suffixes: {suffixes}')
            info(f'Paths: {paths}')
            info(f'Excludes: {excludes}')
            info(f'Report format: {report_format}')
            info(f'Fail on violations: {fail_on_violation}')

        violations = find_non_matching_files(paths, suffixes, excludes)
        violation_count = len(violations)

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
