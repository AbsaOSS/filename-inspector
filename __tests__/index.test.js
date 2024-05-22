const core = require('@actions/core');
const fs = require('fs');
const path = require('path');
const run = require('../index.js');

jest.mock('@actions/core');
jest.mock('fs', () => ({
    promises: {
        access: jest.fn()
    },
    readdirSync: jest.fn()
}));
jest.mock('path');

describe('run function', () => {
    let logOutput = [];

    beforeEach(() => {
        jest.clearAllMocks();
        logOutput = [];

        core.getInput = jest.fn().mockImplementation((key) => {
            const inputs = {
                'suffixes': 'UnitTests,IntegrationTests',
                'include_directories': 'src/test/java',
                'excludes': 'TestHelper,ResultReporter',
                'case_sensitivity': 'false',
                'logic': 'endsWith',
                'report_format': 'json',
                'verbose_logging': 'true',
                'fail_on_violations': 'true'
            };
            return inputs[key];
        });

        core.setOutput = jest.fn();
        core.setFailed = jest.fn();
        core.info = jest.fn((msg) => logOutput.push(msg));

        fs.readdirSync.mockImplementation((dir) => {
            const structure = {
                'src/test/java': [
                    { name: 'file1.js', isDirectory: () => false },
                    { name: 'file2.js', isDirectory: () => false },
                    { name: 'subdir', isDirectory: () => true }
                ],
                'src/test/java/subdir': [
                    { name: 'file3.js', isDirectory: () => false },
                    { name: 'file4.js', isDirectory: () => false }
                ]
            };
            return structure[dir] || [];
        });

        path.join = jest.fn((...args) => args.join('/'));
        path.relative = jest.fn((from, to) => {
            return to.replace(from, '');
        });
    });

    afterEach(() => {
        // console.log('Collected log output:', logOutput);
    });

    it('should call core.getInput with correct parameters', async () => {
        await run();

        expect(core.getInput).toHaveBeenCalledWith('suffixes');
        expect(core.getInput).toHaveBeenCalledWith('include_directories');
        expect(core.getInput).toHaveBeenCalledWith('excludes');
        expect(core.getInput).toHaveBeenCalledWith('case_sensitivity');
        expect(core.getInput).toHaveBeenCalledWith('logic');
        expect(core.getInput).toHaveBeenCalledWith('report_format');
        expect(core.getInput).toHaveBeenCalledWith('verbose_logging');
        expect(core.getInput).toHaveBeenCalledWith('fail_on_violations');

        // Check the final state (e.g., core.setOutput was called with 'status' and 'success')
        expect(core.setOutput).toHaveBeenCalledWith('conventions_violations', 0);
        expect(core.setFailed).not.toHaveBeenCalled();
    });

    // Add more tests here for different functionalities and edge cases
});
