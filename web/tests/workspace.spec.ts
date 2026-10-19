import { expect, test, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { readFile } from 'node:fs/promises';
async function editSettings(page: Page) {
  const button = page.getByRole('button', { name: 'Edit settings' });
  if (await button.isVisible()) await button.click();
}
test('complete research workflow, saved comparisons, exports and refresh', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'How your capital would have grown' }),
  ).toBeVisible();
  await editSettings(page);
  await page.getByLabel('Fast window').fill('30');
  await expect(
    page.getByText('Inputs changed. Run analysis to update these results.'),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Run analysis', exact: true }).click();
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await page.getByRole('button', { name: 'Save run' }).click();
  await page.getByLabel('Analysis name').fill('First idea');
  await page.getByRole('button', { name: 'Save analysis', exact: true }).click();
  await expect(page.getByRole('status').filter({ hasText: 'Run saved' })).toBeVisible();
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export', exact: true }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toContain('SPY-analysis');
  const exported = JSON.parse(await readFile((await download.path())!, 'utf8'));
  expect(exported.config.fast).toBe(30);
  expect(exported.assumptions).toContain('Signals use the previous session');
  expect(exported.trades.length).toBeGreaterThan(0);
  expect(exported.points.length).toBeGreaterThan(1000);
  await page.getByRole('tab', { name: 'Risk', exact: true }).click();
  await expect(page.getByText('Annualized strategy volatility')).toBeVisible();
  await page.getByRole('tab', { name: /^Trades/ }).click();
  await page.getByRole('textbox', { name: 'Search trades' }).fill('no match');
  await expect(page.getByText(/No trades match/)).toBeVisible();
  await page.getByLabel('Fast window').fill('40');
  await page.getByRole('button', { name: 'Run analysis', exact: true }).click();
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await page.getByRole('button', { name: 'Save run' }).click();
  await page.getByLabel('Analysis name').fill('Second idea');
  await page.getByRole('button', { name: 'Save analysis', exact: true }).click();
  await page.getByRole('button', { name: /Saved analyses/ }).click();
  await page.getByLabel('Compare', { exact: true }).nth(0).check();
  await page.getByLabel('Compare', { exact: true }).nth(1).check();
  await expect(page.getByRole('columnheader', { name: 'First idea' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Second idea' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Compare saved runs' })).toBeVisible();
  await page.getByRole('button', { name: 'Open analysis' }).first().click();
  await expect(page.getByLabel('Fast window')).toHaveValue('30');
  await page.getByLabel('Fast window').fill('');
  await page.reload();
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await editSettings(page);
  await expect(page.getByLabel('Fast window')).toHaveValue('30');
  await page.getByRole('button', { name: /Saved analyses/ }).click();
  await expect(page.getByRole('heading', { name: 'First idea', exact: true })).toBeVisible();
  expect(errors).toEqual([]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
test('failed refresh preserves the previous result and retry recovers', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await page.route('**/data/DIA.json', (route) => route.abort());
  await editSettings(page);
  await page.getByLabel('Ticker', { exact: true }).selectOption('DIA');
  await page.getByRole('button', { name: 'Run analysis', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('previous result is still shown');
  await expect(
    page.getByRole('heading', { name: 'How your capital would have grown' }),
  ).toBeVisible();
  await page.unroute('**/data/DIA.json');
  await page.getByRole('button', { name: 'Retry', exact: true }).click();
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
});
test('validation, chart trade links, keyboard tabs and accessible dialog', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await editSettings(page);
  await page.getByLabel('Fast window').fill('150');
  await expect(page.getByRole('alert')).toContainText('fast window below');
  await expect(page.getByRole('button', { name: 'Run analysis', exact: true })).toBeDisabled();
  await page.getByLabel('Fast window').fill('20');
  await page.getByRole('tab', { name: 'Performance', exact: true }).focus();
  await page.keyboard.press('ArrowRight');
  await expect(page.getByRole('tab', { name: 'Risk', exact: true })).toBeFocused();
  await page.getByRole('tab', { name: 'Performance', exact: true }).click();
  const marker = page.getByRole('button', { name: /Buy on .*view trade/ }).first();
  await marker.focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('tab', { name: /^Trades/ })).toHaveAttribute('aria-selected', 'true');
  await expect(page.getByRole('textbox', { name: 'Search trades' })).toBeFocused();
  await expect(page.locator('tbody tr')).toHaveCount(1);
  await page.getByRole('button', { name: 'Save run' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).not.toBeVisible();
});
test('blocked storage still allows analysis', async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, 'localStorage', {
      get() {
        throw new Error('Unavailable');
      },
    });
  });
  await page.goto('/');
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await expect(page.getByText(/Browser storage is unavailable/)).toBeVisible();
  await page.getByRole('button', { name: 'Save run' }).click();
  await page.getByRole('button', { name: 'Save analysis', exact: true }).click();
  await page.getByRole('button', { name: /Saved analyses/ }).click();
  await expect(page.getByRole('heading', { name: /SPY · 20\/100 crossover/ })).toBeVisible();
});
test('initial failure can retry and mobile layout has no overflow', async ({ page }) => {
  await page.route('**/data/SPY.json', (route) =>
    route.fulfill({ status: 503, body: 'Unavailable' }),
  );
  await page.goto('/');
  await expect(page.getByRole('alert')).toContainText('Could not load SPY');
  await page.unroute('**/data/SPY.json');
  await page.getByRole('button', { name: 'Retry', exact: true }).click();
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('workspace and dialogs meet automated accessibility checks', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await editSettings(page);
  const scan = () => new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect((await scan()).violations).toEqual([]);
  await page.getByRole('button', { name: 'Save run' }).click();
  expect((await scan()).violations).toEqual([]);
});

test('historical dashboard URL serves the full app with relative assets', async ({ page }) => {
  await page.goto('/dashboard/');
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'How your capital would have grown' }),
  ).toBeVisible();
});

test('a stalled data request times out and can be retried', async ({ page }) => {
  await page.clock.install();
  await page.route('**/data/SPY.json', () => {});
  await page.goto('/');
  await expect(page.getByText('Running your analysis…')).toBeVisible();
  await page.clock.fastForward(16000);
  await expect(page.getByRole('alert')).toContainText('took too long');
  await page.unroute('**/data/SPY.json');
  await page.getByRole('button', { name: 'Retry', exact: true }).click();
  await expect(page.getByText('Analysis complete', { exact: false })).toBeVisible();
});
