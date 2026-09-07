import test from 'node:test';
import assert from 'node:assert/strict';
import { safeAssetPath } from './server.js';

test('serves only assets inside dashboard/public', () => {
  assert.ok(safeAssetPath('/index.html').endsWith('/dashboard/public/index.html'));
  assert.equal(safeAssetPath('/../../source-data/impact-summary.json'), null);
});

test('normalizes the root route to the editable index', () => {
  assert.ok(safeAssetPath('/').endsWith('/dashboard/public/index.html'));
});

