const core = require('@actions/core');
const fs = require('fs');
const path = require('path');
const run = require('../src');
const {mockCore, mockFs, mockPath, mockInputs} = require("./mocks");

describe('run function', () => {
    let logOutput = [];

    beforeEach(() => {
        jest.clearAllMocks();
        logOutput = [];

        mockCore();
        mockFs();
        mockPath();

        core.info.mockImplementation((msg) => logOutput.push(msg));
    });

    afterEach(() => {
        console.log('Collected log output:', logOutput);
    });

    const inputConfigurations = [
        {
            description: 'default inputs only',
            inputs: {
                'suffixes': 'UnitTests,IntegrationTests',
                'verbose_logging': 'true'
            },
            expectedOutput: 'success',
            expectedViolations: 3
        },
        {
            description: 'fail on violation',
            inputs: {
                'suffixes': 'UnitTests,IntegrationTests',
                'fail_on_violations': 'true'
            },
            expectedOutput: 'fail',
            expectedViolations: 0
        },
        {
            description: 'custom include directories',
            inputs: {
                'suffixes': 'UnitTests,IntegrationTests',
                'include_directories': 'src/another'
            },
            expectedOutput: 'success',
            expectedViolations: 1
        },
        {
            description: 'custom exclude files',
            inputs: {
                'suffixes': 'UnitTests,IntegrationTests',
                'exclude_files': 'test2.java',
                'verbose_logging': 'true',
            },
            expectedOutput: 'success',
            expectedViolations: 2
        },
        {
            description: 'case insensitivity',
            inputs: {
                'suffixes': 'UnitTests,IntegrationTests',
                'exclude_files': 'test2.java'
            },
            expectedOutput: 'success',
            expectedViolations: 2
        },
        {
            description: 'change detection logic',
            inputs: {
                'suffixes': 'Unitt',
                'logic': 'false'
            },
            expectedOutput: 'success',
            expectedViolations: 3
        },
        {
            description: 'change report format - json',
            inputs: {
                'suffixes': 'UnitTests,IntegrationTests',
                'report_format': 'json',
            },
            expectedOutput: 'success',
            expectedViolations: 3
        },
        {
            description: 'change report format - csv',
            inputs: {
                'suffixes': 'UnitTests,IntegrationTests',
                'report_format': 'csv',
            },
            expectedOutput: 'success',
            expectedViolations: 3
        }
    ];

    test.each(inputConfigurations)('should handle $description', async ({ inputs, expectedOutput, expectedViolations }) => {
        mockInputs(inputs);

        await run();

        // const core = require('@actions/core');
        expect(core.getInput).toHaveBeenCalledWith('suffixes');
        expect(core.getInput).toHaveBeenCalledWith('include_directories');
        expect(core.getInput).toHaveBeenCalledWith('exclude_directories');
        expect(core.getInput).toHaveBeenCalledWith('exclude_files');
        expect(core.getInput).toHaveBeenCalledWith('case_sensitivity');
        expect(core.getInput).toHaveBeenCalledWith('logic');
        expect(core.getInput).toHaveBeenCalledWith('report_format');
        expect(core.getInput).toHaveBeenCalledWith('verbose_logging');
        expect(core.getInput).toHaveBeenCalledWith('fail_on_violations');

        if (expectedOutput === 'success') {
            expect(core.setOutput).toHaveBeenCalledWith('conventions_violations', expectedViolations);
            expect(core.setFailed).not.toHaveBeenCalled();
        } else {
            expect(core.setFailed).toHaveBeenCalled();
        }

        if (core.getInput("report_format") === 'json') {
            const violationsFilePath = path.resolve(process.cwd(), 'violations.json');
            if (fs.existsSync(violationsFilePath)) {
                const violationsContent = fs.readFileSync(violationsFilePath, 'utf8');
                const violations = JSON.parse(violationsContent);

                expect(Array.isArray(violations["violations"])).toBe(true);
                expect(violations["violations"].length).toBe(expectedViolations);

                violations["violations"].forEach(violation => {
                    expect(
                        violation.includes('AnotherUnitt') ||
                        violation.includes('t1.j') ||
                        violation.includes('t2.j')
                    ).toBe(true);
                });
            } else {
                throw new Error('violations.json file does not exist');
            }
        } else if (core.getInput("report_format") === 'csv') {
            const violationsFilePath = path.resolve(process.cwd(), 'violations.csv');
            if (fs.existsSync(violationsFilePath)) {
                const violationsContent = fs.readFileSync(violationsFilePath, 'utf8');
                const violations = violationsContent.split('\n').map(line => line.trim()).filter(line => line.length > 0);

                expect(Array.isArray(violations)).toBe(true);
                expect(violations.length).toBe(expectedViolations);

                violations.forEach(violation => {
                    expect(
                        violation.includes('AnotherUnitt') ||
                        violation.includes('t1.j') ||
                        violation.includes('t2.j')
                    ).toBe(true);
                });
            } else {
                throw new Error('violations.csv file does not exist');
            }
        }
    });
});
