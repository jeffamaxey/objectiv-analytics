/*
 * Copyright 2021-2022 Objectiv B.V.
 */

module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  reporters: ['jest-standard-reporter'],
  collectCoverageFrom: ['src/**/*.{ts,tsx}'],
  moduleNameMapper: {
    '@objectiv/testing-tools': '<rootDir>../../core/testing-tools/src',
  },
};
