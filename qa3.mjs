export default async function run(page, ui) {
  // login
  const email = page.locator('input[aria-label="Email"]').first();
  await email.scrollIntoViewIfNeeded();
  await email.click();
  await page.keyboard.type('admin@company.com');
  await page.waitForTimeout(500);
  const pwd = page.locator('input[type="password"]').first();
  await pwd.scrollIntoViewIfNeeded();
  await pwd.click();
  await page.keyboard.type('admin123');
  await page.waitForTimeout(300);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(10000);
  const out = {};
  out.afterLogin = (await page.evaluate(() => document.body.innerText)).slice(0, 300);

  // 1) click My Profile button in sidebar
  const profBtn = page.locator('section[data-testid="stSidebar"] button', { hasText: 'Profile' }).first();
  await profBtn.evaluate((el) => el.scrollIntoView());
  await profBtn.dispatchEvent('click');
  await page.waitForTimeout(6000);
  out.afterProfileClick = (await page.evaluate(() => document.body.innerText)).slice(0, 900);

  // 2) back to dashboard, change category dropdown
  const dashBtn = page.locator('section[data-testid="stSidebar"] button', { hasText: 'Employee Dashboard' }).first();
  await dashBtn.evaluate((el) => el.scrollIntoView());
  await dashBtn.dispatchEvent('click');
  await page.waitForTimeout(4000);
  await page.locator('label:has-text("Category")').locator('..').click();
  await page.waitForTimeout(1000);
  await page.locator('div[id="st-selectbox-options"] li, [role="listbox"] [role="option"]').filter({ hasText: '⏰ Time & Work' }).first().click();
  await page.waitForTimeout(4000);
  out.afterCategorySwitch = (await page.evaluate(() => document.body.innerText)).slice(0, 800);
  return out;
}
