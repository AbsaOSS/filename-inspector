const path = require('path');

const mockPath = () => {
    jest.mock('path');
    path.join = jest.fn((...args) => args.join('/'));
    path.relative = jest.fn((from, to) => {
        return to.replace(from, '');
    });
};

module.exports = mockPath;
