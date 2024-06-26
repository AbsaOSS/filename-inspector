import contextlib
import io
import tempfile
from unittest import mock

import pytest
import os

from unittest.mock import patch, mock_open
from src.filename_inspector import get_action_input, set_action_output, set_action_failed, run

# Constants
DEFAULT_NAME_PATTERNS = '*UnitTest.*,*IntegrationTest.*'
PATHS = '**/src/test/**'
PATHS_WITH_FILE = '**/src/test/**,**/src/xyz/**/*.txt'
EXCLUDES_EMPTY = ''
EXCLUDES = '*src/exclude_dir/*,*ttests.java,*java/test1.java'
REPORT_FORMAT_CONSOLE = 'console'
REPORT_FORMAT_CSV = 'csv'
REPORT_FORMAT_JSON = 'json'
VERBOSE_LOGGING_FALSE = 'false'
VERBOSE_LOGGING_TRUE = 'true'
FAIL_ON_VIOLATION_FALSE = 'false'
FAIL_ON_VIOLATION_TRUE = 'true'

# Variables & parameters
output_values = {}
failed_message: str = ""


# Fixtures
@pytest.fixture(autouse=True)
def clear_output_values():
    output_values.clear()


@pytest.fixture(autouse=True)
def reset_failed_message():
    global failed_message
    failed_message = ""


@pytest.fixture
def mock_getenv(monkeypatch):
    def getenv_mock(key, default=''):
        env = {
            'INPUT_NAME_PATTERNS': DEFAULT_NAME_PATTERNS,
            'INPUT_PATHS': PATHS,
            'INPUT_EXCLUDES': EXCLUDES_EMPTY,
            'INPUT_REPORT_FORMAT': default,
            'INPUT_VERBOSE_LOGGING': VERBOSE_LOGGING_FALSE,
            'INPUT_FAIL_ON_VIOLATION': FAIL_ON_VIOLATION_FALSE
        }
        return env.get(key, 'test_value')
    monkeypatch.setattr(os, 'getenv', getenv_mock)


def mock_set_action_output(name, value):
    output_values[name] = value


def mock_set_action_failed(message):
    global failed_message
    failed_message = message


# Tests
def test_set_action_output_env_var_set():
    with tempfile.NamedTemporaryFile() as tmpfile:
        with patch.dict(os.environ, {'GITHUB_OUTPUT': tmpfile.name}):
            set_action_output('test_name', 'test_value')
            tmpfile.seek(0)
            assert 'test_name=test_value\n' == tmpfile.read().decode()


def test_set_action_output_env_var_not_set():
    with patch.dict(os.environ, {}, clear=True):
        # Using mock_open with an in-memory stream to simulate file writing
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            set_action_output('test_name', 'test_value')
            mock_file().write.assert_called_with('test_name=test_value\n')


@pytest.mark.parametrize("name, value, expected", [
    ('name1', 'value1', 'name1=value1\n'),
    ('name2', 'value2', 'name2=value2\n'),
    ('foo', 'bar', 'foo=bar\n')
])
def test_set_action_output_parametrized(name, value, expected):
    with tempfile.NamedTemporaryFile() as tmpfile:
        with patch.dict(os.environ, {'GITHUB_OUTPUT': tmpfile.name}):
            set_action_output(name, value)
            tmpfile.seek(0)
            assert expected == tmpfile.read().decode()


def test_get_action_input(mock_getenv):
    with patch('os.getenv', return_value='test_value') as mock_getenv_func:
        assert get_action_input('INPUT_TEST') == 'test_value'
        mock_getenv_func.assert_called_with('INPUT_TEST')


def test_set_failed():
    test_message = 'falling!'

    # Mock the logging.error method
    with mock.patch('logging.error') as mock_log_error:
        # Test the SystemExit exception
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            set_action_failed(test_message)
        assert SystemExit == pytest_wrapped_e.type
        assert 1 == pytest_wrapped_e.value.code

        # Ensure logging.error was called with the correct message
        mock_log_error.assert_called_once_with(test_message)


@pytest.mark.parametrize(
    "paths, report_format, verbose_logging, excludes, fail_on_violation, expected_violation_count, expected_report, expected_failed_message", [
    (PATHS, REPORT_FORMAT_CONSOLE, VERBOSE_LOGGING_FALSE, EXCLUDES_EMPTY, FAIL_ON_VIOLATION_FALSE, 4, None, None),     # default values
    (PATHS_WITH_FILE, REPORT_FORMAT_CONSOLE, VERBOSE_LOGGING_FALSE, EXCLUDES_EMPTY, FAIL_ON_VIOLATION_FALSE, 6, None, None),
    (PATHS, REPORT_FORMAT_CONSOLE, VERBOSE_LOGGING_TRUE, EXCLUDES, FAIL_ON_VIOLATION_FALSE, 2, None, None),
    (PATHS, REPORT_FORMAT_CSV, VERBOSE_LOGGING_FALSE, EXCLUDES_EMPTY, FAIL_ON_VIOLATION_FALSE, 4, 'violations.csv', None),
    (PATHS, REPORT_FORMAT_JSON, VERBOSE_LOGGING_FALSE, EXCLUDES_EMPTY, FAIL_ON_VIOLATION_FALSE, 4, 'violations.json', None),
    (PATHS, REPORT_FORMAT_CONSOLE, VERBOSE_LOGGING_FALSE, EXCLUDES_EMPTY, FAIL_ON_VIOLATION_TRUE, 4, None, 'There are 4 test file naming convention violations.')
])
def test_run(monkeypatch, paths, report_format, verbose_logging, excludes, fail_on_violation, expected_violation_count, expected_report, expected_failed_message):
    def getenv_mock(key, default=''):
        env = {
            'INPUT_NAME_PATTERNS': DEFAULT_NAME_PATTERNS,
            'INPUT_PATHS': paths,
            'INPUT_EXCLUDES': excludes,
            'INPUT_REPORT_FORMAT': report_format,
            'INPUT_VERBOSE_LOGGING': verbose_logging,
            'INPUT_FAIL_ON_VIOLATION': fail_on_violation
        }
        return env.get(key, 'test_value')

    monkeypatch.setattr(os, 'getenv', getenv_mock)
    with (patch('src.filename_inspector.set_action_output', new=mock_set_action_output),
          patch('src.filename_inspector.set_action_failed', new=mock_set_action_failed)):
        run()
        assert str(expected_violation_count) == output_values['violation-count']
        if expected_report:
            assert expected_report == output_values['report-path']
        if expected_failed_message:
            assert expected_failed_message == failed_message


def test_run_exception_handling():
    with patch('src.filename_inspector.get_action_input', side_effect=Exception('Test exception')), \
            patch('src.filename_inspector.set_action_failed', new=mock_set_action_failed):
        run()
        assert 'Action failed with error: Test exception' == failed_message


# Run the tests
if __name__ == '__main__':
    pytest.main()
