import { afterEach, expect, it, vi } from 'vitest';
import { readStorage, writeStorage } from './storage';
import { DEFAULT } from './engine';
afterEach(() => vi.unstubAllGlobals());
it('recovers from corrupt or unavailable storage', () => {
  for (const raw of [
    '{broken',
    JSON.stringify({
      draft: DEFAULT,
      saved: [{ id: 'x', name: 'Broken', result: { config: DEFAULT } }],
    }),
  ]) {
    vi.stubGlobal('localStorage', { getItem: () => raw });
    expect(readStorage().state).toBeNull();
    expect(readStorage().warning).not.toBe('');
  }
  vi.stubGlobal('localStorage', {
    getItem: () => {
      throw new Error();
    },
    setItem: () => {
      throw new Error();
    },
  });
  expect(readStorage().state).toBeNull();
  expect(writeStorage({ draft: DEFAULT, saved: [] })).toBe(false);
});
it('round trips settings without browser-specific dependencies', () => {
  let raw: string | null = null;
  vi.stubGlobal('localStorage', {
    getItem: () => raw,
    setItem: (_key: string, value: string) => {
      raw = value;
    },
  });
  expect(writeStorage({ draft: DEFAULT, saved: [] })).toBe(true);
  expect(readStorage().state?.draft).toEqual(DEFAULT);
});
