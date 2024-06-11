import fnmatch
import glob
import logging
import os
import json
import csv
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_input(name: str) -> str:
    value = os.getenv(f'INPUT_{name.upper()}')
    return value


def set_output(name: str, value: str, default_output_path: str = "default_output.txt"):
    output_file = os.getenv('GITHUB_OUTPUT', default_output_path)
    with open(output_file, 'a') as f:
        f.write(f'{name}={value}\n')


def set_failed(message: str):
    logging.error(message)
    exit(1)


def find_non_matching_files(name_patterns, paths, excludes):
    non_matching_files = []

    # Iterate over each glob pattern to find files
    for path in paths:
        if '.' in path:
            logging.error(f"Skipped path to file value '{path}'. Only path to directories are accepted.")
            continue

        for file in glob.glob(path, recursive=True):
            # Check if the file matches any of the exclude patterns
            if any(fnmatch.fnmatch(file, e) for e in excludes):
                continue
            # Check if the file matches any of the name patterns
            if os.path.isfile(file) and not any(fnmatch.fnmatch(file, p) for p in name_patterns):
                non_matching_files.append(file)

    return non_matching_files


def run():
    try:
        name_patterns_raw = get_input('name_patterns')
        name_patterns = name_patterns_raw.split(',') if name_patterns_raw else []
        paths_raw = get_input('paths')
        paths = paths_raw.split(',')
        excludes_raw = get_input('excludes')
        excludes = excludes_raw.split(',')
        report_format = get_input('report_format').lower()
        verbose_logging = get_input('verbose_logging').lower() == 'true'
        fail_on_violation = get_input('fail_on_violation').lower() == 'true'

        if verbose_logging:
            logging.getLogger().setLevel(logging.DEBUG)

        logging.debug(f'Name patterns: {name_patterns}')
        logging.debug(f'Paths: {paths}')
        logging.debug(f'Excludes: {excludes}')
        logging.debug(f'Report format: {report_format}')
        logging.debug(f'Fail on violations: {fail_on_violation}')

        violations = find_non_matching_files(name_patterns, paths, excludes)
        violation_count = len(violations)

        set_output('violation_count', str(violation_count))

        if report_format == 'console' or verbose_logging:
            logging.warning(f'Total violations: {violation_count}')
            logging.warning(f'Violating files: {violations}')

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
        logging.error(f'Action failed with error: {error}')
        set_failed(f'Action failed with error: {error}')


if __name__ == '__main__':
    run()
