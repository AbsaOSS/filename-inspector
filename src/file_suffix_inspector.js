const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');

async function run() {
    try {
        const suffixesRaw = core.getInput('suffixes');
        const suffixes = suffixesRaw ? suffixesRaw.split(',').map(s => s.trim()) : [];
        const includeDirectoriesRaw = core.getInput('include_directories') || "src/test/";
        const includeDirectories = includeDirectoriesRaw ? includeDirectoriesRaw.split(',').map(s => s.trim()) : [];
        const excludeDirectoriesRaw = core.getInput('exclude_directories') || "dist,node_modules,coverage,target,.idea,.github";
        const excludeDirectories = excludeDirectoriesRaw ? excludeDirectoriesRaw.split(',').map(s => s.trim()) : [];
        const excludeFilesRaw = core.getInput('exclude_files');
        const excludeFiles = excludeFilesRaw ? excludeFilesRaw.split(',').map(s => s.trim()) : [];
        const caseSensitivityInput = core.getInput('case_sensitivity');
        const caseSensitivity = caseSensitivityInput ? caseSensitivityInput === 'true' : true;
        const logicInput = core.getInput('logic');
        const logic = logicInput ? logicInput === 'true' : true;
        const reportFormat = core.getInput('report_format') || "console";
        const verboseLogging = core.getInput('verbose_logging') === 'true';
        const failOnViolations = core.getInput('fail_on_violations') === 'true';

        if (verboseLogging) {
            core.info(`Suffixes: ${JSON.stringify(suffixes)}`);
            core.info(`Include directories: ${JSON.stringify(includeDirectories)}`);
            core.info(`Exclude directories: ${JSON.stringify(excludeDirectories)}`);
            core.info(`Exclude files: ${JSON.stringify(excludeFiles)}`);
            core.info(`Case sensitivity: ${caseSensitivity}`);
            core.info(`Logic: ${logic}`);
            core.info(`Report format: ${reportFormat}`);
            core.info(`Fail on violations: ${failOnViolations}`);
        }

        let violationsCount = 0;
        const violations = [];

        function scanDirectory(directory, level= 1) {
            const files = fs.readdirSync(directory, { withFileTypes: true });

            for (const file of files) {
                const fullPath = path.join(directory, file.name);
                const filename = file.name;

                if (file.isDirectory()) {
                    // check exclude root directories
                    if (level === 1 && excludeDirectories.includes(file.name)) {
                        if (verboseLogging) {
                            core.info(`Skipping excluded directory: ${file.name}`);
                        }
                    } else {
                        scanDirectory(fullPath, level + 1);
                    }
                } else {
                    for (const includeDir of includeDirectories) {
                        // check included directories
                        if (fullPath.includes(includeDir)) {
                            if (excludeFiles.includes(filename)) {
                                if (verboseLogging) {
                                    core.info(`Excluded file: ${fullPath}`);
                                }

                                continue;
                            }

                            const checkFilenameWithExtension = caseSensitivity ? filename : filename.toLowerCase();
                            const checkFilename = checkFilenameWithExtension.split(".")[0];
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
        }

        scanDirectory(path.join(process.cwd()));
        // TODO - test moznosti nastaveni root dir zde

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

module.exports.run = run;

if (require.main === module) {
    run();
}
