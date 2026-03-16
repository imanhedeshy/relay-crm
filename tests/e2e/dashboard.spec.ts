import { expect, test } from '@playwright/test';

test('viewer role stays read-only', async ({ page }) => {
  await page.goto('/');
  const demoUserSelect = page.locator('select#demo-user');
  await expect(demoUserSelect).toBeEnabled();
  await demoUserSelect.selectOption({ label: 'Vic Viewer' });
  await page.waitForLoadState('networkidle');

  await expect(page.getByRole('heading', { name: 'Lead creation is unavailable for this role' })).toBeVisible();
  await expect(page.getByText('Read-only role')).toBeVisible();
  await expect(page.getByText(/this role cannot create new leads/i)).toBeVisible();
});

test('manager can create a lead and observe async completion', async ({ page }) => {
  const uniqueId = Date.now().toString();
  const title = `Interview Walkthrough ${uniqueId}`;
  const contactEmail = `interview-${uniqueId}@example.com`;

  await page.goto('/');
  const demoUserSelect = page.locator('select#demo-user');
  await expect(demoUserSelect).toBeEnabled();
  await demoUserSelect.selectOption({ label: 'Maya Manager' });
  await page.waitForLoadState('networkidle');

  await page.getByLabel('Lead title').fill(title);
  await page.getByLabel('Contact name').fill('Interview Contact');
  await page.getByLabel('Contact email').fill(contactEmail);
  await page.getByRole('button', { name: 'Create lead' }).click();

  const leadCard = page.locator('article.lead-card').filter({ hasText: title });
  await expect(leadCard).toBeVisible();
  await expect(leadCard.getByText('COMPLETED')).toBeVisible();
  await expect(leadCard.getByText(/FOLLOW_UP/i)).toBeVisible();
});
