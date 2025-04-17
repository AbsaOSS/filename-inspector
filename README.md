# Filename Inspector

- [Description](#description)
- [How It Works](#how-it-works)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Usage Example](#usage-example)
  - [Default](#default)
  - [Full example](#full-example)
- [How To Build](#how-to-build)
- [Running Static Code Analysis](#running-static-code-analysis)
- [Run Black Tool Locally](#run-black-tool-locally)
- [Run mypy Tool Locally](#run-mypy-tool-locally)
- [Running Unit Tests](#running-unit-tests)
- [Code Coverage](#code-coverage)
- [Run Action Locally](#run-action-locally)
- [Contributing](#contributing)
- [License](#license)

## Description
The **Filename Inspector** GitHub Action is designed to ensure naming conventions in project files within specified repository directories. It scans for project files and reports any missing specified file name patterns, helping maintain consistency and adherence to project standards. The tool is not limited to any programming language files; it scans file names and ignores extensions until they are used in filters.

## How It Works
This action scans the specified `paths` for project files and checks if their file names fit the `name_patterns.` It reports the count of files not meeting the naming conventions, with options to fail the action if violations are found.

## Inputs
### `name-patterns`
- **Description**: List of file name patterns that project files should fit, separated by commas. Supports [fnmatch pattern](https://docs.python.org/3/library/fnmatch.html).
- **Required**: Yes
- **Example**: `*UnitTest.*,*IntegrationTest.*`

### `paths`
- **Description**: List of paths to include in the scan, separated by commas. Supports the [glob pattern](https://code.visualstudio.com/docs/editor/glob-patterns).
- **Required**: Yes
- **Example**: `**/src/test/java/**,**/src/test/scala/**/*.txt`

### `excludes`
- **Description**: List of filenames to exclude from name-pattern checks, separated by commas. Support [fnmatch pattern](https://docs.python.org/3/library/fnmatch.html).
- **Required**: No
- **Default**: ``

### `report-format`
- **Description**: Specifies the format of the output report. Options include console, csv, and json.
- **Required**: No
- **Default**: `console`
- **Options**:
  - `console`: Prints the list of violated files to the console.
  - `csv`: Generates a CSV file with the report. No printout of violated files to the console, unless verbose is enabled. Path to the report file is provided in the `report-path` output.
  - `json`: Generates a JSON file with the report. No printout of violated files to the console, unless verbose is enabled. Path to the report file is provided in the `report-path` output.

### `verbose-logging`
- **Description**: Enable verbose logging to provide detailed output during the action’s execution, aiding in troubleshooting and setup.
- **Required**: No
- **Default**: `false`
- **Note**: If workflow run in debug mode, 'verbose-logging' is set to 'true.'

### `fail-on-violation`
- **Description**: Set to true to fail the action if any convention violations are detected. Set false to continue without failure.
- **Required**: No
- **Default**: `false`

## Outputs
### `violation-count`
- **Description**: Count of files not complying with the specified file name patterns.

### `report-path`
- **Description**: Path to the generated report file. **Not used** if the `report-format` is set to `console`.

## Usage Example
### Default
```yaml
name: Check Project Files Naming Conventions
on: [push]
jobs:
  check_naming:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Filename Inspector Default
      id: scan-test-files
      uses: AbsaOSS/filename-inspector@v0.1.0
      with:
        name-patterns: '*UnitTest.*,*IntegrationTest.*'
        paths: '**/src/test/java/**,**/src/test/scala/**'
```

### Full example
```yaml
name: Check Project Files Naming Conventions
on: [push]
jobs:
  check_naming:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2

        - name: Filename Inspector Full Custom
          id: scan-test-files
          uses: AbsaOSS/filename-inspector@v0.1.0
          with:
            name-patterns: |
              *UnitTest.*,
              *IntegrationTest.*
            paths: |
              **/src/test/java/**,
              **/src/test/scala/**
            excludes: |
              src/exclude_dir/*.py,
              tests/exclude_file.py
            report-format: 'console'
            verbose-logging: 'false'
            fail-on-violation: 'false'
```

## How to build

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/AbsaOSS/filename-inspector.git
cd filename-inspector
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

## Running Static Code Analysis

This project uses Pylint tool for static code analysis. Pylint analyses your code without actually running it. It checks for errors, enforces, coding standards, looks for code smells etc.

Pylint displays a global evaluation score for the code, rated out of a maximum score of 10.0. We are aiming to keep our code quality high above the score 9.5.

### Set Up Python Environment
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Pylint tool, since it is listed in the project requirements.

### Run Pylint
Run Pylint on all files that are currently tracked by Git in the project.
```shell
pylint $(git ls-files '*.py')
```

To run Pylint on a specific file, follow the pattern `pylint <path_to_file>/<name_of_file>.py`.

Example:
```shell
pylint ./src/filename_inspector.py
``` 

## Run Black Tool Locally
This project uses the [Black](https://github.com/psf/black) tool for code formatting.
Black aims for consistency, generality, readability and reducing git diffs.
The coding style used can be viewed as a strict subset of PEP 8.

The project root file `pyproject.toml` defines the Black tool configuration.
In this project we are accepting the line length of 120 characters.

Follow these steps to format your code with Black locally:

### Set Up Python Environment
From terminal in the root of the project, run the following command:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This command will also install a Black tool, since it is listed in the project requirements.

### Run Black
Run Black on all files that are currently tracked by Git in the project.
```shell
black $(git ls-files '*.py')
```

To run Black on a specific file, follow the pattern `black <path_to_file>/<name_of_file>.py`.

Example:
```shell
black ./src/filename_inspector.py
``` 

### Expected Output
This is the console expected output example after running the tool:
```
All done! ✨ 🍰 ✨
1 file reformatted.
```

## Run mypy Tool Locally

This project uses the [my[py]](https://mypy.readthedocs.io/en/stable/)
tool which is a static type checker for Python.

> Type checkers help ensure that you’re using variables and functions in your code correctly.
> With mypy, add type hints (PEP 484) to your Python programs,
> and mypy will warn you when you use those types incorrectly.
my[py] configuration is in `pyproject.toml` file.

Follow these steps to format your code with my[py] locally:

### Run my[py]

Run my[py] on all files in the project.
```shell
  mypy .
```

To run my[py] check on a specific file, follow the pattern `mypy <path_to_file>/<name_of_file>.py --check-untyped-defs`.

Example:
```shell
   mypy src/filename_inspector.py
``` 

### Expected Output

This is the console expected output example after running the tool:
```
Success: no issues found in 1 source file
```

## Running Unit Tests
Unit tests are written using pytest. To run the tests, use the following command:

```bash
pytest
```

This will execute all tests located in the __tests__ directory and generate a code coverage report.

## Code Coverage
Code coverage is collected using pytest-cov coverage tool. To run the tests and collect coverage information, use the following command:

```bash
pytest --cov=src --cov-report html tests/
```
See the coverage report on the path:
```bash
htmlcov/index.html
```

## Run Action Locally
Create *.sh file and place it in the project root.
```bash
#!/bin/bash

# Set environment variables based on the action inputs
export INPUT_NAME_PATTERNS="*UnitTest.*,*IntegrationTest.*"
export INPUT_PATHS="**/src/test/java/**,**/src/test/scala/**"
export INPUT_EXCLUDES="src/exclude_dir/*.py,tests/exclude_file.py"
export INPUT_REPORT_FORMAT="console"
export INPUT_VERBOSE_LOGGING="true"
export INPUT_FAIL_ON_VIOLATION="false"

# Run the Python script
python3 ./src/filename_inspector.py
```


## Contributing
Feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
