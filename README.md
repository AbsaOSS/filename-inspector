# Filename Inspector

- [Description](#description)
- [How It Works](#how-it-works)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Usage Example](#usage-example)
  - [Default](#default)
  - [Full example](#full-example)
- [How To Build](#how-to-build)
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
