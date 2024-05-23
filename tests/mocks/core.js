const core = require('@actions/core');

const mockCore = () => {
    jest.mock('@actions/core');
    core.setOutput = jest.fn();
    core.setFailed = jest.fn();
    core.info = jest.fn();
};

const mockInputs = (inputs) => {
    core.getInput = jest.fn().mockImplementation((key) => inputs[key]);
};

module.exports = {
    mockCore,
    mockInputs
};
