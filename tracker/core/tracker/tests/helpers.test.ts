import { waitForPromise } from '../src';

describe('helpers', () => {
  describe('waitForPromise', () => {
    it('resolves - immediate', () => {
      return expect(
        waitForPromise({
          predicate: () => true,
          intervalMs: 1,
          timeoutMs: 1,
        })
      ).resolves.toBe(undefined);
    });

    it('resolves - async', () => {
      return expect(
        waitForPromise({
          predicate: jest.fn().mockReturnValueOnce(false).mockReturnValueOnce(true),
          intervalMs: 1,
          timeoutMs: 1,
        })
      ).resolves.toBe(undefined);
    });

    it('rejects - timeout', () => {
      return expect(
        waitForPromise({
          predicate: () => false,
          intervalMs: 1,
          timeoutMs: 1,
        })
      ).rejects.toBe(undefined);
    });
  });
});
