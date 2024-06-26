import fnmatch
import glob
import logging
import os
import json
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


INPUT_NAME_PATTERNS = "INPUT_NAME_PATTERNS"
INPUT_PATHS = "INPUT_PATHS"
INPUT_EXCLUDES = "INPUT_EXCLUDES"
INPUT_REPORT_FORMAT = "INPUT_REPORT_FORMAT"
INPUT_VERBOSE_LOGGING = "INPUT_VERBOSE_LOGGING"
INPUT_FAIL_ON_VIOLATION = "INPUT_FAIL_ON_VIOLATION"


def get_action_input(name: str) -> str:
    return os.getenv(name)


def set_action_output(name: str, value: str, default_output_path: str = "default_output.txt"):
    output_file = os.getenv('GITHUB_OUTPUT', default_output_path)
    with open(output_file, 'a') as f:
        f.write(f'{name}={value}\n')


def set_action_failed(message: str):
    logging.error(message)
    exit(1)


def find_non_matching_files(name_patterns, paths, excludes):
    non_matching_files = []

    # Iterate over each glob pattern to find files
    for path in paths:
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
        name_patterns_raw = get_action_input(INPUT_NAME_PATTERNS)
        name_patterns = name_patterns_raw.split(',') if name_patterns_raw else []
        paths_raw = get_action_input(INPUT_PATHS)
        paths = paths_raw.split(',')
        excludes_raw = get_action_input(INPUT_EXCLUDES)
        excludes = excludes_raw.split(',')
        report_format = get_action_input(INPUT_REPORT_FORMAT).lower()
        verbose_logging = get_action_input(INPUT_VERBOSE_LOGGING).lower() == 'true'
        fail_on_violation = get_action_input(INPUT_FAIL_ON_VIOLATION).lower() == 'true'

        if verbose_logging:
            logging.getLogger().setLevel(logging.DEBUG)

        logging.debug(f'Name patterns: {name_patterns}')
        logging.debug(f'Paths: {paths}')
        logging.debug(f'Excludes: {excludes}')
        logging.debug(f'Report format: {report_format}')
        logging.debug(f'Fail on violations: {fail_on_violation}')

        violations = find_non_matching_files(name_patterns, paths, excludes)
        violation_count = len(violations)

        set_action_output('violation-count', str(violation_count))

        logging.info(f'Total violations: {violation_count}')

        if report_format == 'console' or verbose_logging:
            logging.info(f'Violating files: {violations}')

        if report_format == 'csv':
            with open('violations.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows([[violation] for violation in violations])
            set_action_output('report-path', 'violations.csv')
        elif report_format == 'json':
            with open('violations.json', mode='w') as file:
                json.dump({'violations': violations}, file)
            set_action_output('report-path', 'violations.json')

        if fail_on_violation and violation_count > 0:
            set_action_failed(f'There are {violation_count} test file naming convention violations.')

    except Exception as error:
        logging.error(f'Action failed with error: {error}')
        set_action_failed(f'Action failed with error: {error}')


if __name__ == '__main__':
    run()
