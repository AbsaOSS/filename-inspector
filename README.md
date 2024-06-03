# Test File Suffix Inspector

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
The **Test File Suffix Inspector** GitHub Action is designed to ensure naming conventions in test files within specified repository directories. It scans for test files and reports any missing specified suffixes, helping maintain consistency and adherence to project standards. The tool is not limited to any programming language files; it scans file names and ignores extensions until they are used in filters.

## How It Works
This action scans the specified `include_directories` for test files and checks if they end with the defined `suffixes` or contain them anywhere in the filename based on the `pattern_logic.` It reports the count of files not meeting the naming conventions, with options to fail the action if violations are found.

## Inputs
### `suffixes`
- **Description**: List of suffixes that test files should have, separated by commas.
- **Required**: Yes
- **Default**: `UnitTests,IntegrationTests`

### `include_directories`
- **Description**: List of directories to include in the pattern check. This input limits scanning to these directories only.
- **Required**: No
- **Default**: `src/test/`

### `exclude_directories`
- **Description**: List of directories to exclude from scanning, separated by commas.
- **Required**: No
- **Default**: `dist,node_modules,coverage,target,.idea,.github,.git`

### `exclude_files`
- **Description**: List of filenames to exclude from suffix checks, separated by commas.
- **Required**: No
- **Default**: None

### `case_sensitivity`
- **Description**: Determines if the filename check should be case-sensitive.
- **Required**: No
- **Default**: `true`

### `logic`
- **Description**: Switch logic from suffix (end of the filename) to contains (any part of the filename).
- **Required**: No
- **Default**: `false`

### `report_format`
- **Description**: Specifies the format of the output report. Options include console, csv, and json.
- **Required**: No
- **Default**: `console`

### `verbose_logging`
- **Description**: Enable verbose logging to provide detailed output during the action’s execution, aiding in troubleshooting and setup.
- **Required**: No
- **Default**: `false`

### `fail_on_violations`
- **Description**: Set to true to fail the action if any convention violations are detected. Set to false to continue without failure.
- **Required**: No
- **Default**: `false`

## Outputs
### `conventions_violations`
- **Description**: Count test files not complying with the specified suffix conventions.

### `report_path`
- **Description**: Path to the generated report file.

## Usage Example
### Default
```yaml
name: Check Test File Naming Conventions
on: [push]
jobs:
  check_naming:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Test File Suffix Inspector Default
      id: scan-test-files
      uses: AbsaOSS/test-file-suffix-inspector@v0.1.0
      with:
        suffixes: 'UnitTests,IntegrationTests'
```

### Full example
```yaml
name: Check Test File Naming Conventions
on: [push]
jobs:
  check_naming:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2

        - name: Test File Suffix Inspector Full Custom
          id: scan-test-files
          uses: AbsaOSS/test-file-suffix-inspector@v0.1.0
          with:
            suffixes: 'UnitTests,IntegrationTests'
            include_directories: 'src/test/'
            exclude_files: 'TestHelper.scala,TestUtils'
            case_sensitivity: 'true'
            logic: 'false'
            report_format: 'console'
            verbose_logging: 'false'
            fail_on_violations: 'false'
```

## How to build

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/AbsaOSS/test-file-suffix-inspector.git
cd test-file-suffix-inspector
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
export INPUT_SUFFIXES="UnitTests,IntegrationTests"
export INPUT_INCLUDE_DIRECTORIES="src/test/"
export INPUT_EXCLUDE_DIRECTORIES="dist,node_modules,coverage,target,.idea,.github,.git,htmlcov"
export INPUT_EXCLUDE_FILES=""
export INPUT_CASE_SENSITIVITY="true"
export INPUT_LOGIC="true"
export INPUT_REPORT_FORMAT="console"
export INPUT_VERBOSE_LOGGING="true"
export INPUT_FAIL_ON_VIOLATIONS="false"

# Run the Python script
python3 ./src/file_suffix_inspector.py
```


## Contributing
Feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
