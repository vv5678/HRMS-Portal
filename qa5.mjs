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
  // dump everything around the Category widget
  out.categoryArea = await page.evaluate(() => {
    const labels = [...document.querySelectorAll('label')].filter(l => l.textContent.includes('Category'));
    if (!labels.length) return 'no label with Category';
    let el = labels[0];
    let chain = [];
    for (let i = 0; i < 4 && el.parentElement; i++) { el = el.parentElement; chain.push(el.outerHTML.slice(0, 500)); }
    return chain;
  });
  return out;
}
