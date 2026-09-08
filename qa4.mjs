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
  // open the category selectbox
  await page.locator('label:has-text("Category")').locator('..').click();
  await page.waitForTimeout(2000);
  out.dropdownHtml = (await page.evaluate(() => {
    const d = document.getElementById('st-selectbox-options');
    return d ? d.innerText.slice(0, 600) : 'NO st-selectbox-options; listbox count=' + document.querySelectorAll('[role="listbox"]').length;
  }));
  return out;
}
