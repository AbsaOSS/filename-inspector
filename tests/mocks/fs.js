const fs = require('fs');

const mockFs = () => {
    jest.mock('fs', () => {
        const originalModule = jest.requireActual('fs');
        return {
            ...originalModule,
            promises: {
                access: jest.fn()
            }
        };
    });
};

module.exports = mockFs;
