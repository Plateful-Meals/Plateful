"""
Plateful's own price checker: reads search results from the shops' websites in a normal browser on your computer.

It is used by update_prices.py when it runs with  --source browser  (check_prices.py does this for you).
No Apify, no paid service. It only visits shop pages that the shops' robots.txt rules allow (Tesco, Sainsbury's,
Morrisons, Lidl), one page at a time, with a pause of several seconds between visits.

It does NOT try to get round anything a shop puts in the way: no hidden browser tricks, no fake identities,
no CAPTCHA solving, no clicking through cookie banners. If a shop refuses a visit or shows a "prove you are
human" page, that shop is stopped for the rest of the run and its old prices are kept.
"""
import os, random, re, time, urllib.parse

# Text that means the shop refused us. If any appears, the shop is stopped for this run.
BLOCK_RX = re.compile(r'access denied|are you a robot|verify (?:that )?you are (?:a )?human|unusual traffic|'
                      r'captcha|request (?:was )?blocked|pardon our interruption|temporarily unavailable', re.I)

# Runs inside the shop's page. Finds one tile per product link and reads name, price, was-price,
# loyalty-card price, unit price and offer text from what the page shows.
EXTRACT_JS = r"""
([linkSrc, max]) => {
  const linkRx = new RegExp(linkSrc);
  const key = h => h.split('#')[0].split('?')[0];
  const isProd = a => a && a.href && linkRx.test(a.href);
  const out = [], seen = new Set();
  const money = s => { const m = /£\s?(\d+(?:\.\d{1,2})?)/.exec(s) || /(?<![\d.£])(\d{1,3})p\b(?!\s*\/)/.exec(s); if (!m) return null; return m[0].includes('£') ? parseFloat(m[1]) : parseInt(m[1], 10) / 100; };
  const CARD = '(?:clubcard\\s*price|with\\s*clubcard|nectar\\s*price|with\\s*nectar|lidl\\s*plus(?:\\s*price)?|with\\s*lidl\\s*plus|more\\s*card\\s*price|with\\s*more\\s*card)';
  const PRICE = '(?:£\\s?\\d+(?:\\.\\d{1,2})?|\\d{1,3}p)';
  for (const a of document.querySelectorAll('a[href]')){
    if (!isProd(a)) continue;
    const k = key(a.href); if (seen.has(k)) continue;
    // climb to the biggest box that still holds only this one product
    let t = a, tile = null;
    for (let i = 0; i < 9 && t.parentElement && t.parentElement !== document.body; i++){
      t = t.parentElement;
      const ks = new Set([...t.querySelectorAll('a[href]')].filter(isProd).map(x => key(x.href)));
      if (ks.size > 1) break;
      if (/£\s?\d|\d\s?p\b/.test(t.innerText || '')) tile = t;
    }
    if (!tile) continue;
    seen.add(k);
    const links = [...tile.querySelectorAll('a[href]')].filter(isProd);
    let name = links.map(x => (x.innerText || '').trim()).filter(x => x && !/£|\d+p\b/.test(x)).sort((x, y) => y.length - x.length)[0] || '';
    if (!name){ const img = tile.querySelector('img[alt]'); name = img ? img.alt.trim() : (a.getAttribute('aria-label') || '').trim(); }
    let text = (tile.innerText || '').replace(/\s+/g, ' ');
    const promo = [];
    // multi-buys ("Any 3 for £10", "2 for £5") are offer text, not the price of one. Read them first:
    // they can carry the card name too ("Any 2 for £7.50 Clubcard Price")
    const mb = /\b(?:any\s+)?\d+\s+for\s+(?:£\s?\d+(?:\.\d{1,2})?|\d{1,3}p)/i.exec(text);
    if (mb){ promo.push(mb[0]); text = text.replace(mb[0], ' '); }
    // loyalty-card price, either "£1.50 Clubcard Price" or "Clubcard Price £1.50"
    let member = null;
    const c1 = new RegExp('(' + PRICE + ')\\s*' + CARD, 'i').exec(text) || new RegExp(CARD + '[:\\s]*(' + PRICE + ')', 'i').exec(text);
    if (c1){ member = money(c1[1]); promo.push(c1[0]); text = text.replace(c1[0], ' '); }
    // was-price
    let was = null;
    const w = /\bwas[:\s]*(£\s?\d+(?:\.\d{1,2})?|\d{1,3}p)/i.exec(text);
    if (w){ was = money(w[1]); promo.push(w[0]); text = text.replace(w[0], ' '); }
    // unit prices: "£1.75/kg", "(£0.35 per 100g)", "35p/100g"
    let unit = '';
    const u = /\(?(?:£\s?\d+(?:\.\d{1,2})?|\d{1,3}(?:\.\d+)?p)\s*(?:\/|per)\s*(?:\d+\s*)?(?:kg|g|l|ltr|litre|ml|cl|each|ea|100g|100ml|75cl|sht|sheet|wash|unit)\b\)?/ig;
    const units = text.match(u) || [];
    if (units.length){ unit = units[0].replace(/[()]/g, ''); units.forEach(x => { text = text.replace(x, ' '); }); }
    const price = money(text);
    if (!name || price == null) continue;
    out.push({name, price, wasPrice: was, memberPrice: member, pricePerUnit: unit, promotion: promo.join(' | ').slice(0, 80), url: k});
    if (out.length >= max) break;
  }
  return out;
}
"""


class ShopRefused(Exception):
    pass


class BrowserShops:
    """One real browser window, one tab per shop. Use as a context manager."""

    def __init__(self, shops_cfg, profile_dir, hidden=False, pause=(4.0, 8.0), log=print):
        self.cfg, self.profile_dir, self.hidden, self.pause, self.log = shops_cfg, profile_dir, hidden, pause, log
        if os.environ.get('PF_TEST_NO_PAUSE'):      # only for Plateful's own tests against a local copy of a page
            self.pause = (0.0, 0.0)
        self.pages, self.last_visit = {}, {}

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise SystemExit('Playwright is not installed. Run:  python3 -m pip install playwright   then   python3 -m playwright install chromium')
        self.pw = sync_playwright().start()
        os.makedirs(self.profile_dir, exist_ok=True)
        # A persistent profile: the shops see the same ordinary browser each time, like a person coming back.
        self.ctx = self.pw.chromium.launch_persistent_context(self.profile_dir, headless=self.hidden, locale='en-GB',
                                                              timezone_id='Europe/London', viewport={'width': 1280, 'height': 900})
        return self

    def __exit__(self, *exc):
        try:
            self.ctx.close()
        finally:
            self.pw.stop()

    def _page(self, shop):
        if shop not in self.pages:
            self.pages[shop] = self.ctx.pages[0] if (not self.pages and self.ctx.pages) else self.ctx.new_page()
        return self.pages[shop]

    def search(self, shop, kw, n):
        b = self.cfg[shop]['browser']
        # be polite: never visit the same shop more often than the pause allows
        wait = self.last_visit.get(shop, 0) + random.uniform(*self.pause) - time.time()
        if wait > 0:
            time.sleep(wait)
        url = b['search_url'].replace('{kwpath}', urllib.parse.quote(kw)).replace('{kw}', urllib.parse.quote_plus(kw))
        pg = self._page(shop)
        try:
            resp = pg.goto(url, wait_until='domcontentloaded', timeout=45000)
        finally:
            self.last_visit[shop] = time.time()
        status = resp.status if resp else 0
        if status in (401, 403, 429) or status >= 500:
            raise ShopRefused(f'the website answered {status}')
        try:
            pg.wait_for_function('src => [...document.querySelectorAll("a[href]")].some(a => new RegExp(src).test(a.href))',
                                 arg=b['link'], timeout=15000)
        except Exception:
            pass                                   # no product links: either no results or a refusal page (checked below)
        pg.wait_for_timeout(1200)                  # let prices and offers finish drawing
        body = pg.evaluate('() => (document.title + " " + (document.body ? document.body.innerText.slice(0, 3000) : ""))')
        items = pg.evaluate(EXTRACT_JS, [b['link'], max(n, 1)])
        if not items and BLOCK_RX.search(body):
            raise ShopRefused('the website showed a "prove you are human" or "access denied" page')
        return items
