export default {
  testEnvironment: 'node',
  transform: {},
  testMatch: ['**/server/__tests__/**/*.test.js'],
  // Jest 30 supports ESM natively with --experimental-vm-modules
  // Node 24 has good ESM support
};
