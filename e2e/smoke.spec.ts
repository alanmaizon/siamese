import { expect, test } from '@playwright/test';

test('landing page enters workspace and shows validation error without files', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('button', { name: /enter workspace/i })).toBeVisible();
  await page.getByRole('button', { name: /enter workspace/i }).click();

  await expect(page.getByRole('heading', { name: /artifacts/i })).toBeVisible();
  await expect(page.getByRole('button', { name: /start analysis/i })).toBeVisible();

  await page.getByRole('button', { name: /start analysis/i }).click();

  await expect(page.getByText('Analysis Failed')).toBeVisible();
  await expect(page.getByText('Please upload at least one file to analyze.')).toBeVisible();
});
