import contextlib
import io
import subprocess

import pytest
import os

from unittest.mock import patch
from src.file_suffix_inspector import get_input, set_output, set_failed, run

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
def mock_getenv_default(monkeypatch):
    def getenv_mock(key):
        if key == 'INPUT_SUFFIXES':
            return 'UnitTests,IntegrationTests'
        elif key == 'INPUT_INCLUDE_DIRECTORIES':
            return 'src/test/'
        elif key == 'INPUT_EXCLUDE_DIRECTORIES':
            return 'dist,node_modules,coverage,target,.idea,.github,.git,htmlcov'
        elif key == 'INPUT_EXCLUDE_FILES':
            return ''
        elif key == 'INPUT_CASE_SENSITIVITY':
            return 'true'
        elif key == 'INPUT_LOGIC':
            return 'true'
        elif key == 'INPUT_REPORT_FORMAT':
            return 'console'
        elif key == 'INPUT_VERBOSE_LOGGING':
            return 'false'
        elif key == 'INPUT_FAIL_ON_VIOLATIONS':
            return 'false'
        else:
            return 'test_value'
    monkeypatch.setattr(os, 'getenv', getenv_mock)


@pytest.fixture
def mock_getenv_csv(monkeypatch):
    def getenv_mock(key):
        if key == 'INPUT_SUFFIXES':
            return 'UnitTests,IntegrationTests'
        elif key == 'INPUT_INCLUDE_DIRECTORIES':
            return 'src/test/'
        elif key == 'INPUT_EXCLUDE_DIRECTORIES':
            return 'dist,node_modules,coverage,target,.idea,.github,.git,htmlcov'
        elif key == 'INPUT_EXCLUDE_FILES':
            return ''
        elif key == 'INPUT_CASE_SENSITIVITY':
            return 'true'
        elif key == 'INPUT_LOGIC':
            return 'true'
        elif key == 'INPUT_REPORT_FORMAT':
            return 'csv'
        elif key == 'INPUT_VERBOSE_LOGGING':
            return 'false'
        elif key == 'INPUT_FAIL_ON_VIOLATIONS':
            return 'false'
        else:
            return 'test_value'
    monkeypatch.setattr(os, 'getenv', getenv_mock)


@pytest.fixture
def mock_getenv_fail(monkeypatch):
    def getenv_mock(key):
        if key == 'INPUT_SUFFIXES':
            return 'UnitTests,IntegrationTests'
        elif key == 'INPUT_INCLUDE_DIRECTORIES':
            return 'src/test/'
        elif key == 'INPUT_EXCLUDE_DIRECTORIES':
            return 'dist,node_modules,coverage,target,.idea,.github,.git,htmlcov'
        elif key == 'INPUT_EXCLUDE_FILES':
            return ''
        elif key == 'INPUT_CASE_SENSITIVITY':
            return 'true'
        elif key == 'INPUT_LOGIC':
            return 'true'
        elif key == 'INPUT_REPORT_FORMAT':
            return 'console'
        elif key == 'INPUT_VERBOSE_LOGGING':
            return 'false'
        elif key == 'INPUT_FAIL_ON_VIOLATIONS':
            return 'true'
        else:
            return 'test_value'
    monkeypatch.setattr(os, 'getenv', getenv_mock)


@pytest.fixture
def mock_getenv_json(monkeypatch):
    def getenv_mock(key):
        if key == 'INPUT_SUFFIXES':
            return 'UnitTests,IntegrationTests'
        elif key == 'INPUT_INCLUDE_DIRECTORIES':
            return 'src/test/'
        elif key == 'INPUT_EXCLUDE_DIRECTORIES':
            return 'dist,node_modules,coverage,target,.idea,.github,.git,htmlcov'
        elif key == 'INPUT_EXCLUDE_FILES':
            return ''
        elif key == 'INPUT_CASE_SENSITIVITY':
            return 'true'
        elif key == 'INPUT_LOGIC':
            return 'true'
        elif key == 'INPUT_REPORT_FORMAT':
            return 'json'
        elif key == 'INPUT_VERBOSE_LOGGING':
            return 'false'
        elif key == 'INPUT_FAIL_ON_VIOLATIONS':
            return 'false'
        else:
            return 'test_value'
    monkeypatch.setattr(os, 'getenv', getenv_mock)


@pytest.fixture
def mock_getenv_verbose_file_exclude(monkeypatch):
    def getenv_mock(key):
        if key == 'INPUT_SUFFIXES':
            return 'UnitTests,IntegrationTests'
        elif key == 'INPUT_INCLUDE_DIRECTORIES':
            return 'src/test/'
        elif key == 'INPUT_EXCLUDE_DIRECTORIES':
            return 'dist,node_modules,coverage,target,.idea,.github,.git,htmlcov'
        elif key == 'INPUT_EXCLUDE_FILES':
            return 'test1.java'
        elif key == 'INPUT_CASE_SENSITIVITY':
            return 'true'
        elif key == 'INPUT_LOGIC':
            return 'true'
        elif key == 'INPUT_REPORT_FORMAT':
            return 'console'
        elif key == 'INPUT_VERBOSE_LOGGING':
            return 'true'
        elif key == 'INPUT_FAIL_ON_VIOLATIONS':
            return 'false'
        else:
            return 'test_value'
    monkeypatch.setattr(os, 'getenv', getenv_mock)


def mock_set_output(name, value):
    output_values[name] = value


def mock_set_failed(message):
    global failed_message
    failed_message = message


# Tests

def test_get_input(mock_getenv_default):
    with patch('os.getenv', return_value='test_value') as mock_getenv_func:
        assert get_input('test') == 'test_value'
        mock_getenv_func.assert_called_with('INPUT_TEST')


def test_set_output(monkeypatch):
    name = 'test_name'
    value = 'test_value'
    expected_output = f'{name}={value}\n'

    # Mock the subprocess.run method to prevent actual command execution
    def mock_run(*args, **kwargs):
        with open('GITHUB_OUTPUT', 'w') as f:
            f.write(expected_output)
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(subprocess, 'run', mock_run)

    # Call the set_output method
    set_output(name, value)

    # Check the content of the GITHUB_OUTPUT file
    with open('GITHUB_OUTPUT', 'r') as f:
        output = f.read()

    assert output == expected_output

    # Clean up the GITHUB_OUTPUT file
    os.remove('GITHUB_OUTPUT')


def test_set_failed():
    test_message = 'falling!'
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        set_failed(test_message)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        try:
            set_failed(test_message)
        except SystemExit:
            pass
        stdout = buf.getvalue().strip()
    assert stdout == '::error::falling!'


def test_set_output_exception(monkeypatch):
    name = 'test_name'
    value = 'test_value'

    # Mock the subprocess.run method to return a non-zero return code
    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 1)  # returncode is 1

    monkeypatch.setattr(subprocess, 'run', mock_run)

    # Call the set_output method and check if it raises an exception
    with pytest.raises(Exception) as e:
        set_output(name, value)

    assert str(e.value) == f'Failed to set output: {name}={value}'


def test_run_default(mock_getenv_default):
    with patch('src.file_suffix_inspector.set_output', new=mock_set_output):
        run()
        assert output_values['conventions_violations'] == '3'


def test_run_verbose(mock_getenv_verbose_file_exclude):
    with patch('src.file_suffix_inspector.set_output', new=mock_set_output):
        run()
        assert output_values['conventions_violations'] == '2'


def test_run_csv(mock_getenv_csv):
    with patch('src.file_suffix_inspector.set_output', new=mock_set_output):
        run()
        assert output_values['conventions_violations'] == '3'
        assert output_values['report_file'] == 'violations.csv'


def test_run_json(mock_getenv_json):
    with patch('src.file_suffix_inspector.set_output', new=mock_set_output):
        run()
        assert output_values['conventions_violations'] == '3'
        assert output_values['report_file'] == 'violations.json'


def test_run_fail(mock_getenv_fail):
    with (patch('src.file_suffix_inspector.set_output', new=mock_set_output),
          patch('src.file_suffix_inspector.set_failed', new=mock_set_failed)):
        run()
        assert output_values['conventions_violations'] == '3'
        assert failed_message == 'There are 3 test file naming convention violations.'


def test_run_exception_handling():
    with patch('src.file_suffix_inspector.get_input', side_effect=Exception('Test exception')), \
            patch('src.file_suffix_inspector.set_failed', new=mock_set_failed):
        run()
        assert failed_message == 'Action failed with error: Test exception'


# Run the tests
if __name__ == '__main__':
    pytest.main()
