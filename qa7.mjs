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
  const sel = page.locator('.element-container.st-key-cat_select div[data-baseweb="select"]').first();
  await sel.evaluate((el) => el.scrollIntoView());
  await sel.click({ force: true });
  await page.waitForTimeout(2000);
  out.afterClick = await page.evaluate(() => {
    const lb = document.querySelector('[role="listbox"]');
    return lb ? [...lb.querySelectorAll('[role="option"], li')].map(o => o.textContent.trim()).slice(0, 15) : 'no listbox';
  });
  // if no listbox, try keyboard
  if (out.afterClick === 'no listbox') {
    await sel.focus();
    await page.keyboard.press('Enter');
    await page.waitForTimeout(1500);
    out.afterKey = await page.evaluate(() => {
      const lb = document.querySelector('[role="listbox"]');
      return lb ? [...lb.querySelectorAll('[role="option"], li')].map(o => o.textContent.trim()).slice(0, 15) : 'no listbox';
    });
  }
  return out;
}
