module.exports = {
    testEnvironment: "jest-environment-jsdom",
    roots: ["<rootDir>/src"],
    transform: {
        "^.+\\.jsx?$": "babel-jest"
    },
    setupFilesAfterSetup: ["<rootDir>/src/setupTests.js"]
};
