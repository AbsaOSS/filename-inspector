# Test File Suffix Inspector

- [Description](#description)
- [How It Works](#how-it-works)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Usage Example](#usage-example)
  - [Default](#default)
  - [Full example](#full-example)

## Description
The **Test File Suffix Inspector** GitHub Action is designed to ensure naming conventions in test files within specified repository directories. It scans for test files and reports any missing specified suffixes, helping maintain consistency and adherence to project standards.

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

## Prerequisites

- **Node.js**: Ensure you have Node.js installed. You can download it from [nodejs.org](https://nodejs.org/).
- **npm**: npm is installed with Node.js. Ensure you have npm installed by running `npm -v` in your terminal.

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/AbsaOSS/test-file-suffix-inspector.git
cd test-file-suffix-inspector
```

Install the dependencies:
```bash
npm install
```

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

## Running Unit Tests
Unit tests are written using Jest. To run the tests, use the following command:

```sbt
npm test
```

This will execute all tests located in the __tests__ directory and generate a code coverage report.

## Code Coverage
Code coverage is collected using Jest's built-in coverage tool. To run the tests and collect coverage information, use the following command:

```bash
npm test -- --coverage
```

After running the tests with coverage, you can find the coverage reports in the coverage directory. The reports include a summary printed in the terminal and detailed HTML reports.

To view the detailed HTML coverage report, open the following file in your browser:

```
coverage/lcov-report/index.html
```

## Contributing
Feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.


## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
