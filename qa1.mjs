export default async function run(page, ui) {
  await page.waitForSelector('input[aria-label="Email"]', { timeout: 30000 });
  await page.fill('input[aria-label="Email"]', 'admin@company.com');
  await page.waitForTimeout(500);
  await page.fill('input[type="password"]', 'admin123');
  await page.waitForTimeout(500);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(9000);
  const text = await page.evaluate(() => document.body.innerText);
  return { text: text.slice(0, 2500) };
}
