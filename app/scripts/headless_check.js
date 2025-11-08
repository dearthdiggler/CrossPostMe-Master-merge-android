const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
  });
  const page = await context.newPage();

  const results = [];
  async function checkPath(path) {
    const url = path.startsWith("http")
      ? path
      : `https://www.crosspostme.com${path}`;
    let resp = null;
    try {
      resp = await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    } catch (e) {
      // navigation failed
      return { path: url, status: null, error: String(e) };
    }
    const status = resp ? resp.status() : null;
    // evaluate presence/visibility of nav
    const navInfo = await page.evaluate(() => {
      const sel = document.querySelector(
        'nav, header[role="banner"], [role="navigation"], .navbar, .site-nav',
      );
      if (!sel) return { found: false };
      const rect = sel.getBoundingClientRect();
      const visible = rect.width > 0 && rect.height > 0;
      return {
        found: true,
        visible,
        text: sel.innerText ? sel.innerText.trim().slice(0, 200) : "",
      };
    });
    // capture a short screenshot for debugging
    // await page.screenshot({ path: `./screenshot-${path.replace(/\W/g,'_')}.png`, fullPage: false });
    return { path: url, status, nav: navInfo };
  }

  results.push(await checkPath("/"));
  results.push(await checkPath("/pricing"));
  results.push(await checkPath("/company"));
  // also check the JS and CSS URLs
  results.push(await checkPath("/static/js/main.0cc87e10.js"));
  results.push(await checkPath("/static/css/main.18c039cd.css"));

  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})();
