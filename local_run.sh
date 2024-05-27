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
