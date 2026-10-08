#!/usr/bin/env python3
"""
Offline tests for update_prices.py. No internet, no Apify, no money.
All shop data below is MADE UP to exercise the rules; it is written to a temporary folder and thrown away.

Run:  python pipeline/tests/run_tests.py
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.dirname(HERE)
ROOT = os.path.dirname(PIPE)
sys.path.insert(0, PIPE)
import update_prices as U                       # noqa: E402

fails = []
def check(label, cond, extra=''):
    print(('PASS  ' if cond else 'FAIL  ') + label + (('   ' + str(extra)) if (extra and not cond) else ''))
    if not cond:
        fails.append(label)


# ------------------------------------------------------------------ unit tests: sizes and money
S = U.parse_sizes
check('500g', S('Beef Mince 500g') == {'g': 500.0})
check('1.5kg', S('Plain Flour 1.5kg')['g'] == 1500)
check('4 x 400g', S('Chopped Tomatoes 4 x 400g')['g'] == 1600)
check('4x400g no spaces', S('Baked Beans 4x410g')['g'] == 1640)
check('2 pints', abs(S('Semi Skimmed Milk 2 Pints')['ml'] - 1136.52) < 0.1)
check('4 pints', abs(S('Milk 4 pint')['ml'] - 2273.04) < 0.1)
check('2.27L', S('Milk 2.27L')['ml'] == 2270)
check('0.5l', S('Juice 0.5l')['ml'] == 500)
check('12 pack count', S('Free Range Eggs 12 Pack')['count'] == 12)
check('12s count', S('Large Eggs 12s')['count'] == 12)
check('pack of 6', S('Bread Rolls Pack of 6')['count'] == 6)
check('x6', S('Sausages x6')['count'] == 6)
check('8 sausages', S('8 British Pork Sausages')['count'] == 8)
check('kg not matched inside word', 'g' not in S('Organic Gardens'))
check('money £1.29', U.parse_money('£1.29') == 1.29)
check('money 89p', abs(U.parse_money('89p') - 0.89) < 1e-9)
check('money dict', U.parse_money({'value': 2.5, 'currency': 'GBP'}) == 2.5)
check('money int', U.parse_money(3) == 3.0)
up = U.parse_unit_price('£0.30/100g')
check('unit price 100g', up and abs(up[0] - 0.30) < 1e-9 and up[1] == 100 and up[2] == 'g')
up = U.parse_unit_price('£1.10 per litre')
check('unit price litre', up and up[2] in ('litre', 'litres') or (up and up[2] == 'l'))

# ------------------------------------------------------------------ fake shop data
def aldi(name, price, unit=None, was=None, size=None, url=None):
    d = {'name': name, 'brand': 'Testbrand', 'price': price, 'sku': 'x', 'notForSale': True,
         'url': url or ('https://groceries.aldi.co.uk/en-GB/p-' + name.lower().replace(' ', '-')), 'specs': {}}
    if unit: d['pricePerUnit'] = unit
    if was: d['originalPrice'] = was
    if size: d['specs']['sellingSize'] = size
    return d

def morr(name, price, unit=None, pack=None, promo=None, stock=True):
    return {'name': name, 'brand': 'Morrisons', 'price': price, 'pricePerUnit': unit, 'packSize': pack,
            'promotion': promo, 'availability': 'In stock' if stock else 'Out of stock', 'inStock': stock,
            'url': 'https://groceries.morrisons.com/products/' + name.lower().replace(' ', '-')}

FIX = {
    'aldi': {
        'beef_mince': [
            aldi('British Beef Mince 10% Fat', 4.39, '£0.88/100g', size='500g'),
            aldi('Steak Mince 5% Fat', 4.99, size='500g'),
            aldi('Beef Burgers 4 Pack', 2.49, size='454g'),
            aldi('Organic Beef Mince', 6.49, size='500g'),
            aldi('British Beef Mince 12% Fat', 6.29, size='750g'),
            aldi('Beef Mince 20% Fat', 3.49, size='500g'),
            aldi('Frozen Beef Mince', 3.99, size='500g'),
            aldi('British Beef Mince 12% Fat', 7.49, was=8.49, size='1kg'),
            aldi('Beef Mince Bolognese Sauce', 1.99, size='500g'),
        ],
        'spaghetti': [
            aldi('Spaghetti', 0.65, size='500g'),
            aldi('Wholewheat Spaghetti', 0.79, size='500g'),
            aldi('Spaghetti Hoops in Tomato Sauce', 0.45, size='400g'),
            aldi('Gluten Free Spaghetti', 1.29, size='500g'),
            aldi('Spaghetti', 1.15, size='1kg'),
            aldi('Spaghetti', 0.99, size='500g'),     # dearer than the 0.65 one for the same slot
        ],
        'chopped_tomatoes': [
            aldi('Chopped Tomatoes', 0.39, size='400g'),
            aldi('Chopped Tomatoes with Basil & Garlic', 0.55, size='400g'),
            aldi('Chopped Tomatoes', 1.35, size='4 x 400g'),
            aldi('Organic Chopped Tomatoes', 0.85, size='400g'),
        ],
        'onion': [
            aldi('Brown Onions', 0.85, size='1kg'),
            aldi('Brown Onions 3 Pack', 0.59),
            aldi('Red Onions 3 Pack', 0.79),
            aldi('Brown Onions Loose', 0.18, unit='£0.18/each'),
            aldi('Crispy Fried Onions', 1.25, size='100g'),
        ],
        'butter': [
            aldi('Salted Butter', 1.89, size='250g'),
            aldi('Unsalted Butter', 1.79, size='250g'),
            aldi('Spreadable Butter', 1.95, size='500g'),
            aldi('Garlic Butter', 1.19, size='100g'),
        ],
        'rice': [aldi('Microwave Rice', 1.0, size='250g')],             # nothing usable
        'eggs': [
            aldi('Free Range Eggs 12 Pack', 2.59),
            aldi('Free Range Medium Eggs 6 Pack', 1.49),
            aldi('Barn Eggs 12 Pack', 2.09),                               # cheaper but not free range -> preferred restriction
            aldi('Chocolate Egg', 1.0, size='100g'),
        ],
    },
    'morrisons': {
        'beef_mince': [morr('Beef Mince 12% Fat', 4.75, '£9.50/kg', pack='500g'),
                       morr('Beef Mince 15% Fat', 4.40, '£8.80/kg', pack='500g', stock=False)],
        'spaghetti': [morr('Spaghetti', 0.75, '£1.50/kg', pack='500g')],
        'eggs': [morr('Free Range Eggs', 2.85, '£0.24/each'),            # no size in the name: count from the unit price
                 morr('Free Range Medium Eggs 6 Pack', 1.65)],
        'milk': [morr('Semi Skimmed Milk 2 Pints', 1.25), morr('Semi Skimmed Milk 2.27L', 1.65),
                 morr('Whole Milk 2 Pints', 1.25), morr('Oat Milk', 1.0, pack='1L')],
        'cheddar': [morr('Mature Cheddar', 3.05, pack='400g'), morr('Medium Cheddar', 2.75, pack='400g'),
                    morr('Mature Cheddar Slices', 1.5, pack='200g')],
        'butter': [morr('Salted Butter', 2.05, pack='250g')],
    },
    'lidl': {   # guessed field names, different shape again: the loader must cope
        'beef_mince': [{'title': 'Beef Mince 12% fat 500g', 'price': {'price': 4.19, 'oldPrice': 4.99}, 'url': 'https://www.lidl.co.uk/p/beef-mince'}],
        'spaghetti': [{'productName': 'Spaghetti 500g', 'currentPrice': '£0.69', 'link': 'https://www.lidl.co.uk/p/spaghetti'},
                      {'productName': 'Spaghetti 1kg', 'currentPrice': 129, 'link': 'https://www.lidl.co.uk/p/spaghetti-1kg'}],   # 129 = pence
        'chopped_tomatoes': [{'name': 'Chopped Tomatoes', 'price': 0.35, 'packSize': '400g'}],
        'eggs': [{'name': 'Free range eggs 12 pack', 'price': 2.49}],
        'milk': [{'name': 'Semi skimmed milk 2 pints', 'price': 1.15}],
        'cheddar': [], 'onion': [], 'butter': [],
    },
}
PIDS = 'beef_mince,spaghetti,chopped_tomatoes,eggs,milk,cheddar,onion,butter,rice'


def write_fixtures(root, fix):
    for shop, prods in fix.items():
        os.makedirs(os.path.join(root, shop), exist_ok=True)
        for pid, items in prods.items():
            json.dump(items, open(os.path.join(root, shop, pid + '.json'), 'w'))


def run(tmp, fix, old_prices, today='2026-10-05', shops='aldi,lidl,morrisons', extra=()):
    fx = os.path.join(tmp, 'fx')
    shutil.rmtree(fx, ignore_errors=True); os.makedirs(fx)
    write_fixtures(fx, fix)
    prices = os.path.join(tmp, 'prices.json'); report = os.path.join(tmp, 'report.md')
    json.dump(old_prices, open(prices, 'w'))
    cmd = [sys.executable, os.path.join(PIPE, 'update_prices.py'), '--mode', 'live', '--fixtures', fx, '--prices', prices,
           '--report', report, '--today', today, '--only', PIDS, '--shops', shops, *extra]
    r = subprocess.run(cmd, capture_output=True, text=True)
    new = json.load(open(prices))
    return r, new, open(report).read() if os.path.exists(report) else ''


OLD = {'checked': '2026-09-30', 'label': '30 Sep 2026', 'prices': {
    'beef_mince': {'tesco': {'packs': [[500, 4.5]], 'product': 'Tesco Beef Mince', 'checked': '2026-09-30'},
                   'aldi': {'packs': [[500, 9.99]], 'product': 'old aldi mince', 'checked': '2026-09-30'}},
    'rice': {'aldi': {'packs': [[1000, 1.0]], 'product': 'old aldi rice', 'checked': '2026-08-01'},        # 65 days old, will be dropped
             'lidl': {'packs': [[1000, 1.1]], 'product': 'old lidl rice', 'checked': '2026-09-28'}},         # recent, kept
}}

with tempfile.TemporaryDirectory() as tmp:
    r, new, rep = run(tmp, FIX, OLD)
    print(r.stdout[-600:] if r.returncode else '')
    check('run succeeds', r.returncode == 0, r.stderr[-300:] + r.stdout[-300:])
    P = new['prices']
    a = P['beef_mince']['aldi']
    check('aldi beef mince: replaces the old 9.99 price', a['packs'][0][:2] == [500, 4.39], a)
    check('aldi beef mince: organic/steak/20%/frozen/burger/sauce rejected, 750g and sale 1kg kept',
          [p[0] for p in a['packs']] == [500, 750, 1000], a['packs'])
    check('aldi beef mince: sale stored as [size, was, now]', a['packs'][2] == [1000, 8.49, 7.49], a['packs'])
    check('aldi beef mince: per-pack names and links', all(i.get('u', '').startswith('https://') for i in a['items']) and len(a['items']) == 3)
    check('tesco entry untouched', P['beef_mince']['tesco'] == OLD['prices']['beef_mince']['tesco'])
    sp = P['spaghetti']['aldi']['packs']
    check('aldi spaghetti: cheapest per slot, wholewheat/hoops/gluten-free rejected', sp == [[500, 0.65], [1000, 1.15]], sp)
    ct = P['chopped_tomatoes']['aldi']['packs']
    check('aldi chopped tomatoes: plain only, multipack counted as 1600g', ct == [[400, 0.39], [1600, 1.35]], ct)
    on = P['onion']['aldi']['packs']
    check('aldi onions: 1kg fills the 7-onion slot, 3 pack, loose each', on == [[1, 0.18], [3, 0.59], [7, 0.85]], on)
    check('aldi butter: only plain salted', P['butter']['aldi']['packs'] == [[250, 1.89]], P['butter']['aldi']['packs'])
    eg = P['eggs']['aldi']['packs']
    check('aldi eggs: free-range preferred over cheaper barn eggs', eg == [[6, 1.49], [12, 2.59]], eg)
    m = P['beef_mince']['morrisons']['packs']
    check('morrisons: out-of-stock item ignored, unit-price size ok', m == [[500, 4.75]], m)
    me = P['eggs']['morrisons']['packs']
    check('morrisons eggs: size worked out from £/each', me == [[6, 1.65], [12, 2.85]], me)
    mk = P['milk']['morrisons']['packs']
    check('morrisons milk: 2 pints and 2.27L snap to catalogue sizes', mk == [[1136, 1.25], [2272, 1.65]], mk)
    ch = P['cheddar']['morrisons']['packs']
    check('morrisons cheddar: mature preferred, slices rejected', ch == [[400, 3.05]], ch)
    l = P['beef_mince']['lidl']['packs']
    check('lidl nested price with old price = sale', l == [[500, 4.99, 4.19]], l)
    ls = P['spaghetti']['lidl']['packs']
    check('lidl: price given in pence (129) understood', ls == [[500, 0.69], [1000, 1.29]], ls)
    check('lidl: size from packSize field', P['chopped_tomatoes']['lidl']['packs'] == [[400, 0.35]])
    check('lidl: empty searches leave nothing behind', 'lidl' not in P.get('cheddar', {}) and 'lidl' not in P.get('onion', {}))
    check('stale old price dropped when the shop returns no match', 'aldi' not in P.get('rice', {}))
    check('recent old price kept', P['rice']['lidl']['product'] == 'old lidl rice')
    check('top-level date and label updated', new['checked'] == '2026-10-05' and new['label'] == '5 Oct 2026')
    check('auto note present', 'Aldi' in new['autoNote'] and 'refreshed automatically' in new['autoNote'])
    check('report lists what was picked and what was rejected', 'What it picked' in rep and 'Searched but nothing usable found' in rep and 'Microwave Rice' in rep)
    check('report flags the large price move', 'Big price moves' in rep and 'Beef mince' in rep)

    # ---- a broken shop must not wipe its data
    broken = json.loads(json.dumps(FIX)); broken['aldi'] = {p: [] for p in FIX['aldi']}
    r2, new2, rep2 = run(tmp, broken, OLD)
    check('broken shop: run still succeeds (other shops worked)', r2.returncode == 0, r2.stdout[-300:])
    check('broken shop: old Aldi data left exactly as it was', new2['prices']['beef_mince']['aldi'] == OLD['prices']['beef_mince']['aldi']
          and new2['prices']['rice']['aldi'] == OLD['prices']['rice']['aldi'])
    check('broken shop: report says so', 'NO:' in rep2 and 'looks broken' in rep2)

    # ---- everything broken -> non-zero exit and prices.json untouched
    none = {s: {} for s in FIX}
    r3, new3, rep3 = run(tmp, none, OLD)
    check('all shops failing: exit code 1', r3.returncode == 1, r3.stdout[-200:])
    check('all shops failing: prices.json unchanged', new3 == OLD)

    # ---- spending limit
    r4, new4, rep4 = run(tmp, FIX, OLD, extra=['--max-spend', '0.02'])
    check('spending limit stops the run early and says so', 'spending limit' in rep4 or 'spending limit' in r4.stdout, r4.stdout[-300:])

    # ---- test mode never writes prices.json
    fx = os.path.join(tmp, 'fx'); prices = os.path.join(tmp, 'p2.json'); json.dump(OLD, open(prices, 'w'))
    r5 = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--mode', 'test', '--fixtures', fx, '--prices', prices,
                         '--report', os.path.join(tmp, 'r5.md'), '--only', 'beef_mince', '--shops', 'aldi'], capture_output=True, text=True)
    check('test mode leaves prices.json alone', json.load(open(prices)) == OLD, r5.stderr[-200:])

# ------------------------------------------------------------------ rules: plausible product names (made up) the rules should accept / refuse
cfg_real = json.load(open(os.path.join(PIPE, 'config.json')))
cat_site = U.read_catalogue(open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read())
cat_real = {p: c for p, c in cat_site.items() if p in cfg_real['products']}   # only products with rules are checked weekly
MATCH = U.Matcher(cfg_real, cat_real)

def slot_of(pid, name, price, **kw):
    raw = {'name': name, 'price': price}; raw.update(kw)
    picks, _ = MATCH.choose(pid, [U.normalise(raw)])
    return sorted(cat_real[pid]['packs'][s][0] for s in picks) or None

CASES = [   # (ingredient, product name, price, extra fields, expected pack size(s) or None = refused)
    ('chopped_tomatoes', 'Everyday Essentials Chopped Tomatoes in Tomato Juice 400g', 0.42, {}, [400]),
    ('chopped_tomatoes', 'Italian Chopped Tomatoes with Garlic 400g', 0.6, {}, None),
    ('beef_mince', 'Ashfields British Beef Mince 12% Fat 500g', 4.3, {}, [500]),
    ('beef_mince', 'British Beef Mince 5% Fat 500g', 4.9, {}, None),
    ('chicken_breast', 'British Chicken Breast Fillets 650g', 4.6, {}, [650]),
    ('chicken_breast', 'Southern Fried Chicken Breast Fillets 650g', 4.6, {}, None),
    ('chicken_thighs', 'Chicken Thigh Fillets 1kg', 5.4, {}, [1000]),
    ('chicken_thighs', 'Chicken Thighs Bone In 1kg', 3.2, {}, None),
    ('eggs', 'Free Range Large Eggs 12 Pack', 2.6, {}, [12]),
    ('eggs', 'Chocolate Egg Nest 6 Pack', 2.6, {}, None),
    ('milk', 'Semi-Skimmed Milk 4 Pints', 1.6, {}, [2272]),
    ('milk', 'Semi Skimmed Milk 2 Pint', 1.2, {}, [1136]),
    ('milk', 'Whole Milk 4 Pints', 1.6, {}, None),
    ('milk', 'Oat Semi Skimmed Style Milk 1L', 1.1, {}, None),
    ('rice', 'Long Grain Rice 1kg', 1.1, {}, [1000]),
    ('rice', 'Microwave Long Grain Rice 250g', 1.0, {}, None),
    ('baked_beans', 'Baked Beans in Tomato Sauce 410g', 0.4, {}, [410]),
    ('baked_beans', 'Baked Beans Reduced Sugar 410g', 0.6, {}, None),
    ('tuna', 'Tuna Chunks in Spring Water 4 x 145g', 3.3, {}, [580]),
    ('tuna', 'Tuna Chunks in Sunflower Oil 145g', 1.1, {}, None),
    ('butter', 'Salted British Butter 250g', 2.0, {}, [250]),
    ('bread', 'Toastie White Sliced Bread 800g', 0.85, {}, [1]),
    ('bread', 'Seeded Wholemeal Sliced Bread 800g', 1.2, {}, None),
    ('potatoes', 'White Potatoes 2.5kg', 1.6, {}, [2500]),
    ('potatoes', 'Sweet Potatoes 1kg', 1.3, {}, None),
    ('onion', 'Brown Onions 1kg', 0.9, {}, [7]),
    ('frozen_peas', 'Garden Peas 1kg', 1.3, {'name': 'Frozen Garden Peas 1kg'}, [1000]),
    ('frozen_peas', 'Garden Peas in Water 300g', 0.5, {}, None),
    ('sausages', 'British Pork Sausages 8 Pack', 2.1, {}, [8]),
    ('sausages', 'Vegetarian Sausages 8 Pack', 2.1, {}, None),
    ('plant_mince', 'Meat Free Mince 454g', 2.8, {'name': 'Frozen Meat Free Mince 454g'}, [454]),
    ('gf_spaghetti', 'Gluten Free Spaghetti 500g', 1.3, {}, [500]),
    ('spaghetti', 'Gluten Free Spaghetti 500g', 1.3, {}, None),
    ('parmesan', 'Specially Selected Parmigiano Reggiano 200g', 3.8, {}, [200]),
    ('lemons', 'Unwaxed Lemons 4 Pack', 1.2, {}, [4]),
    ('garlic', 'Garlic 4 Pack', 0.9, {}, [40]),
    ('garlic', 'Garlic Bread Baguette 2 Pack', 1.2, {}, None),
    # ---- the 96 ingredients added with My shop
    ('pork_mince', 'British Pork Mince 20% Fat 500g', 2.6, {}, [500]),
    ('pork_mince', 'Pork Mince Meatballs 400g', 2.6, {}, None),
    ('beef_burgers', '4 Quarter Pounder Beef Burgers 454g', 2.2, {'name': 'Beef Burgers 4 Pack 454g'}, [4]),
    ('beef_burgers', 'Beef Burgers in Brioche Buns 4 Pack', 3.0, {}, None),
    ('beef_burgers', 'Beef Burgers 454g', 2.0, {'name': '4 Beef Burgers 454g'}, [4]),
    ('bacon_rashers', 'Smoked Back Bacon 8 Rashers 300g', 2.0, {'name': '8 Smoked Back Bacon Rashers 300g'}, [8]),
    ('bacon_rashers', 'Smoked Bacon Lardons 200g', 1.8, {}, None),
    ('pork_steaks', 'British Pork Loin Steaks 2 Pack', 2.8, {}, [2]),
    ('salmon', 'Scottish Salmon Fillets 2 Pack', 3.9, {}, [2]),
    ('salmon', 'Smoked Salmon Slices 120g', 3.9, {}, None),
    ('cheese_slices', 'Cheese Slices 10 Pack', 1.1, {'name': '10 Cheese Slices'}, [10]),
    ('cheese_slices', 'Vegan Cheese Slices 10 Pack', 1.7, {}, None),
    ('whole_milk', 'Whole Milk 4 Pints', 1.6, {}, [2272]),
    ('whole_milk', 'Semi Skimmed Milk 4 Pints', 1.6, {}, None),
    ('double_cream', 'Double Cream 300ml', 1.2, {}, [300]),
    ('double_cream', 'Extra Thick Double Cream 300ml', 1.5, {}, None),
    ('basmati_rice', 'Basmati Rice 1kg', 1.9, {}, [1000]),
    ('basmati_rice', 'Microwave Basmati Rice 250g', 1.0, {}, None),
    ('olive_oil', 'Olive Oil 500ml', 4.5, {}, [500]),
    ('olive_oil', 'Extra Virgin Olive Oil 500ml', 5.5, {}, [500]),
    ('olive_oil', 'Olive Oil Spread 500g', 3.0, {}, None),
    ('ketchup', 'Tomato Ketchup 460g', 1.4, {}, [460]),
    ('ketchup', 'Spicy Tomato Ketchup 460g', 1.4, {}, None),
    ('honey', 'Clear Honey 340g', 2.2, {}, [340]),
    ('sugar', 'Granulated Sugar 1kg', 1.2, {}, [1000]),
    ('sugar', 'Icing Sugar 500g', 1.2, {}, None),
    ('apples', 'Gala Apples 6 Pack', 1.3, {}, [6]),
    ('apples', 'Apple Juice 1L', 1.0, {}, None),
    ('avocado', 'Ripe Avocados 2 Pack', 1.6, {}, [2]),
    ('broccoli', 'Broccoli 350g', 0.9, {}, [350]),
]
for pid, name, price, extra, want in CASES:
    kw = dict(extra); nm = kw.pop('name', name)
    got = slot_of(pid, nm, price, **kw)
    check(f'rules: {pid}: {nm[:48]} -> {"refused" if want is None else want}', got == want, f'got {got}')


# ------------------------------------------------------------------ "refresh every N weeks" and --scope due
import datetime as _dt
mondays = [_dt.date(2026, 10, 5) + _dt.timedelta(days=7 * i) for i in range(12)]
def due_count(pid, n):
    return sum(U.is_due(pid, {'refresh': n}, d) for d in mondays)
check('refresh 1 / missing = every week', all(U.is_due('milk', {}, d) for d in mondays) and all(U.is_due('milk', {'refresh': 1}, d) for d in mondays))
check('refresh 2 = every second week, exactly', due_count('pork_mince', 2) == 6 and all(
    U.is_due('pork_mince', {'refresh': 2}, mondays[i]) != U.is_due('pork_mince', {'refresh': 2}, mondays[i + 1]) for i in range(11)))
check('refresh 4 = every fourth week, exactly', due_count('paprika', 4) == 3 and all(
    U.is_due('paprika', {'refresh': 4}, mondays[i]) == U.is_due('paprika', {'refresh': 4}, mondays[i + 4]) for i in range(8)))
check('refresh works across new year (still every 2 weeks)', all(
    U.is_due('salmon', {'refresh': 2}, _dt.date(2026, 12, 14) + _dt.timedelta(days=14 * i)) == U.is_due('salmon', {'refresh': 2}, _dt.date(2026, 12, 14)) for i in range(6)))
spread = [sum(U.is_due(pid, {'refresh': 4}, mondays[0]) for pid in cat_real)]
check('ingredients are spread over the weeks, not all in one', 0.1 * len(cat_real) < spread[0] < 0.45 * len(cat_real), spread)
check('every new ingredient has a refresh setting except the skipped one',
      all(cfg_real['products'][p].get('refresh') in (2, 4) for p in list(cat_real)[88:] if not cfg_real['products'][p].get('skip')))
check('the 88 original ingredients refresh every week', all(not cfg_real['products'][p].get('refresh') for p in list(cat_real)[:88]))

def estimate(*args):
    return subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--mode', 'live', '--estimate', *args],
                          capture_output=True, text=True).stdout
e_all = estimate('--today', '2026-10-05')
e_due = estimate('--today', '2026-10-05', '--scope', 'due')
import re as _re
n_all = int(_re.search(r'(\d+) ingredients, (\d+) searches', e_all).group(2))
m_due = _re.search(r'(\d+) ingredients \((\d+) of (\d+) are due this week.*?, (\d+) searches', e_due)
check('estimate: scope due searches fewer ingredients than scope all', m_due and int(m_due.group(4)) < n_all and int(m_due.group(1)) < int(m_due.group(3)), e_due)
check('estimate: also prints the average weekly and monthly cost', 'average week' in e_all and 'a month' in e_all, e_all)

with tempfile.TemporaryDirectory() as tmp:
    fx = os.path.join(tmp, 'fx'); os.makedirs(os.path.join(fx, 'aldi'))
    for _pid in cat_real:      # something is returned for every search (so the shop does not look broken), but it matches nothing
        json.dump([{'name': 'Mixed Selection Box 1kg', 'price': 3.0}], open(os.path.join(fx, 'aldi', _pid + '.json'), 'w'))
    json.dump([{'name': 'Ashfields British Beef Mince 12% Fat 500g', 'price': 4.2}], open(os.path.join(fx, 'aldi', 'beef_mince.json'), 'w'))
    json.dump([{'name': 'British Pork Mince 20% Fat 500g', 'price': 2.5}], open(os.path.join(fx, 'aldi', 'pork_mince.json'), 'w'))
    # pick a Monday on which pork_mince (refresh 2) is NOT due and one on which it is
    off = next(d for d in mondays if not U.is_due('pork_mince', cfg_real['products']['pork_mince'], d))
    on = next(d for d in mondays if U.is_due('pork_mince', cfg_real['products']['pork_mince'], d))
    for label, day, want_pork in (('due', on, True), ('not due', off, False)):
        prices = os.path.join(tmp, 'p.json'); json.dump({'checked': '2026-09-30', 'label': '30 Sep 2026', 'prices': {}}, open(prices, 'w'))
        r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--mode', 'live', '--scope', 'due', '--shops', 'aldi',
                            '--fixtures', fx, '--prices', prices, '--report', os.path.join(tmp, 'r.md'), '--today', day.isoformat(),
                            '--workers', '1', '--max-spend', '100'], capture_output=True, text=True)
        got = json.load(open(prices))['prices']
        check(f'scope due ({label} week): beef mince (weekly) is searched', 'aldi' in got.get('beef_mince', {}), r.stdout[-300:] + r.stderr[-300:])
        check(f'scope due ({label} week): pork mince (every 2 weeks) is {"searched" if want_pork else "left alone"}',
              ('aldi' in got.get('pork_mince', {})) == want_pork, r.stdout[-300:])
        check(f'scope due ({label} week): report says how many were due', 'are due this week' in open(os.path.join(tmp, 'r.md')).read())


# ------------------------------------------------------------------ --check-config catches a stray "|" (it would reject every product)
with tempfile.TemporaryDirectory() as tmp:
    bad_cfg = json.load(open(os.path.join(PIPE, 'config.json')))
    bad_cfg['products']['sugar']['avoid'] += '|'
    bad_cfg['products']['cheese_slices']['count_nouns'] = 'slices?|'
    json.dump(bad_cfg, open(os.path.join(tmp, 'bad.json'), 'w'))
    r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--check-config', '--config', os.path.join(tmp, 'bad.json')],
                       capture_output=True, text=True)
    check('check-config refuses a pattern with a stray "|"', r.returncode == 1 and 'sugar' in r.stdout and 'cheese_slices' in r.stdout, r.stdout)
for pid, pc in cfg_real['products'].items():
    import re as _re2
    bad = [k for k in ('avoid', 'prefer') if pc.get(k) and _re2.search(pc[k], '')] + [k for k in pc.get('must', []) if _re2.search(k, '')]
    if bad:
        check(f'config: {pid} has no empty-matching pattern', False, bad)
check('config: no pattern anywhere matches the empty string', True)


# ------------------------------------------------------------------ every weight/volume ingredient: its own plain product name must be accepted
# (catches rules so strict they refuse everything, e.g. "raw" matching inside "prawns")
bad_own = []
for pid, c in cat_real.items():
    pc = cfg_real['products'][pid]
    if pc.get('skip') or c['unit'] not in ('g', 'ml'):
        continue
    for slot, price in c['packs']:
        size = (f'{slot / 1000:g}kg' if c['unit'] == 'g' else f'{slot / 1000:g}L') if slot >= 1000 else f'{int(slot)}{c["unit"]}'
        name = ('Frozen ' if pc.get('frozen') else '') + f'{pc["kw"].title()} {size}'
        picks, _ = MATCH.choose(pid, [U.normalise({'name': name, 'price': price})])
        if not picks:
            bad_own.append(name)
check('rules accept the plain product for every weight/volume ingredient and pack size', not bad_own, bad_own[:8])

# ------------------------------------------------------------------ the real config vs the real site
r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--check-config'], capture_output=True, text=True)
check(f'config.json matches the site ({len(cat_real)} checked weekly, {len(cat_site) - len(cat_real)} sample-price only)', r.returncode == 0, r.stdout + r.stderr)
check('check-config says how many use estimated prices', 'more products use estimated prices' in r.stdout, r.stdout)
check('every rule in config.json is for a product in the site', all(p in cat_site for p in cfg_real['products']))
check('the site has products the robot does not touch (new shelves)', len(cat_site) > len(cat_real) and 'kale' in cat_site and 'kale' not in cfg_real['products'])
r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--mode', 'live', '--only', 'kale', '--dry-run'], capture_output=True, text=True)
check('asking for an untracked product explains why it is not checked', r.returncode != 0 and 'has no rules in config.json' in (r.stdout + r.stderr), r.stdout + r.stderr)
r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--mode', 'live', '--scope', 'all', '--estimate'], capture_output=True, text=True)
check('estimate only counts the tracked ingredients', r.returncode == 0 and 'kale' not in r.stdout, r.stdout + r.stderr)
check('apostrophe in a product name is read (Goat\'s cheese)', cat_site.get('goats_cheese', {}).get('name') == "Goat's cheese log", cat_site.get('goats_cheese'))
r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--mode', 'live', '--estimate'], capture_output=True, text=True)
print(r.stdout.strip())
try:
    cfg = json.load(open(os.path.join(PIPE, 'config.json')))
    pj = json.load(open(os.path.join(ROOT, 'prices.json')))
    check('prices.json is valid and has prices', isinstance(pj.get('prices'), dict) and len(pj['prices']) > 0)
except Exception as e:     # pragma: no cover
    check('prices.json readable', False, e)

# ---- the home price checker (--source browser): loyalty-card prices, and shops it must not visit
import tempfile
with tempfile.TemporaryDirectory() as tmp:
    fix = {'tesco': {'beef_mince': [
        {'name': 'Tesco British Beef Mince 500G 12% Fat', 'price': 3.79, 'memberPrice': 3.29, 'pricePerUnit': '£7.58/kg', 'promotion': '£3.29 Clubcard Price'},
        {'name': 'Tesco Beef Mince 750G 12% Fat', 'price': 5.10, 'wasPrice': 6.00, 'promotion': 'Was £6.00'},
        {'name': 'Tesco Beef Mince 500G 12% Fat', 'price': 3.79, 'memberPrice': 9.99}]}}
    r, new, rep = run(tmp, fix, OLD, shops='tesco', extra=('--source', 'browser', '--only', 'beef_mince'))
    t = new['prices']['beef_mince']['tesco']
    check('home checker: a Clubcard price is stored as the 4th number of the pack', [500, 3.79, None, 3.29] in t['packs'], t)
    check('home checker: a was-price still becomes a sale', [750, 6.0, 5.1] in t['packs'], t)
    check('home checker: the report names the card price', 'Clubcard price £3.29' in rep, rep[:400])
    check('home checker: no cost is mentioned', 'no running cost' in rep, rep[:300])
r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--source', 'browser', '--shops', 'aldi', '--mode', 'test', '--estimate'], capture_output=True, text=True)
check('home checker refuses shops whose websites do not allow automated visits', r.returncode != 0 and 'cannot be checked by the home checker' in (r.stdout + r.stderr), r.stdout + r.stderr)
r = subprocess.run([sys.executable, os.path.join(PIPE, 'update_prices.py'), '--source', 'apify', '--shops', 'tesco', '--mode', 'test', '--estimate'], capture_output=True, text=True)
check('the Apify job refuses shops it has no robot for', r.returncode != 0 and 'has no Apify robot' in (r.stdout + r.stderr), r.stdout + r.stderr)

print()
print('ALL PASSED' if not fails else f'{len(fails)} FAILED: ' + '; '.join(fails))
sys.exit(1 if fails else 0)
