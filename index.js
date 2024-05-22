const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');

async function run() {
    try {
        const suffixesRaw = core.getInput('suffixes');
        const suffixes = suffixesRaw ? suffixesRaw.split(',').map(s => s.trim()) : [];
        const includeDirectoriesRaw = core.getInput('include_directories');
        const includeDirectories = includeDirectoriesRaw ? includeDirectoriesRaw.split(',').map(s => s.trim()) : [];
        const excludesRaw = core.getInput('excludes');
        const excludes = excludesRaw ? excludesRaw.split(',').map(s => s.trim()) : [];
        const caseSensitivity = core.getInput('case_sensitivity') === 'true';
        const logic = core.getInput('logic') === 'true';
        const reportFormat = core.getInput('report_format');
        const verboseLogging = core.getInput('verbose_logging') === 'true';
        const failOnViolations = core.getInput('fail_on_violations') === 'true';

        if (verboseLogging) {
            core.info(`Suffixes: ${JSON.stringify(suffixes)}`);
            core.info(`Include directories: ${JSON.stringify(includeDirectories)}`);
            core.info(`Excludes: ${JSON.stringify(excludes)}`);
            core.info(`Case sensitivity: ${caseSensitivity}`);
            core.info(`Logic: ${logic}`);
            core.info(`Report format: ${reportFormat}`);
            core.info(`Fail on violations: ${failOnViolations}`);
        }

        let violationsCount = 0;
        const violations = [];

        function scanDirectory(directory) {
            const files = fs.readdirSync(directory, { withFileTypes: true });
            // core.info(`Files in directory: ${JSON.stringify(files)}`);

            for (const file of files) {
                const fullPath = path.join(file.path, file.name);
                const filename = file.name;

                if (file.isDirectory()) {
                    scanDirectory(fullPath);
                } else {
                    console.log(`D 1: ${JSON.stringify(includeDirectories)}`)
                    console.log(`D 2: ${fullPath}`)

                    // TODO - fix to exact name of folder
                    const fullPathParts = fullPath.split(path.sep);
                    const isIncluded = includeDirectories.some(dir => fullPathParts.includes(dir));
                    if (isIncluded) {
                        if (excludes.includes(filename)) {
                            if (verboseLogging) {
                                core.info(`Excluded file: ${fullPath}`);
                            }

                            continue;
                        }

                        const checkFilename = caseSensitivity ? filename : filename.toLowerCase();
                        const matchesSuffix = suffixes.some(suffix => {
                            const checkSuffix = caseSensitivity ? suffix : suffix.toLowerCase();
                            return logic ? checkFilename.endsWith(checkSuffix) : checkFilename.includes(checkSuffix);
                        });

                        if (!matchesSuffix) {
                            if (verboseLogging) {
                                core.info(`Violating file: ${fullPath}`);
                            }
                            violationsCount++;
                            violations.push(fullPath);
                        } else {
                            if (verboseLogging) {
                                core.info(`Valid file: ${fullPath}`);
                            }
                        }
                    }
                }
            }
        }

        scanDirectory(path.join(process.cwd(), "__tests__"));

        if (verboseLogging) {
            core.info(`Total violations: ${violationsCount}`);
            core.info(`Violating files: ${violations.join(', ')}`);
        }

        core.setOutput('conventions_violations', violationsCount);

        if (reportFormat === 'console' || verboseLogging) {
            console.log(`Total violations: ${violationsCount}`);
            console.log(`Violating files: ${violations.join(', ')}`);
        } else if (reportFormat === 'csv') {
            const csvContent = violations.join('\n');
            fs.writeFileSync('violations.csv', csvContent);
            core.setOutput('report_file', 'violations.csv');
        } else if (reportFormat === 'json') {
            const jsonContent = JSON.stringify({ violations });
            fs.writeFileSync('violations.json', jsonContent);
            core.setOutput('report_file', 'violations.json');
        }

        if (failOnViolations && violationsCount > 0) {
            core.setFailed(`There are ${violationsCount} test file naming convention violations.`);
        }
    } catch (error) {
        console.log(`Action failed with error: ${error}`);
        core.setFailed(`Action failed with error: ${error}`);
    }
}

module.exports = run;
