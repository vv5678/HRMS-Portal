export default async function run(page, ui) {
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
  const dashBtn = page.locator('section[data-testid="stSidebar"] button', { hasText: 'Employee Dashboard' }).first();
  await dashBtn.evaluate((el) => el.scrollIntoView());
  await dashBtn.dispatchEvent('click');
  await page.waitForTimeout(5000);
  // click the actual baseweb select control inside the st-key-cat_select element
  const sel = page.locator('.element-container.st-key-cat_select div[data-baseweb="select"]').first();
  await sel.evaluate((el) => el.scrollIntoView());
  await sel.dispatchEvent('click');
  await page.waitForTimeout(2000);
  // dump open listbox options
  out.options = await page.evaluate(() => {
    const lb = document.querySelector('[role="listbox"]');
    if (!lb) return 'no listbox open';
    return [...lb.querySelectorAll('[role="option"], li')].map(o => o.textContent.trim()).slice(0, 15);
  });
  // click the Time & Work option
  const opt = page.locator('[role="listbox"] [role="option"], [role="listbox"] li').filter({ hasText: 'Time & Work' }).first();
  await opt.click();
  await page.waitForTimeout(5000);
  out.afterCategorySwitch = (await page.evaluate(() => document.body.innerText)).slice(0, 800);
  return out;
}
