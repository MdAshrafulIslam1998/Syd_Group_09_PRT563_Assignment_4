# PRT563 Assessment 4 - Syd_Group_09 - generates extension_data.sql from the Assessment 2 database (a2_base.db)
import random, sqlite3, datetime as dt, math

rng = random.Random(563)
D = dt.date
def d2s(d): return d.isoformat()

con = sqlite3.connect('a2_base.db')
q = lambda s: con.execute(s).fetchall()

rows = {}
def add(table, *vals): rows.setdefault(table, []).append(vals)

STORES = ['W1042', 'W1067', 'W1188']
STORE_DEPTS = {s: {d for (d,) in q(f"select DeptID from STORE_DEPARTMENT where StoreID='{s}'")} for s in STORES}
PERIOD = [D(2026, 9, 7) + dt.timedelta(days=i) for i in range(14)]
DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

hours = {s: {} for s in STORES}
for s, day, o, c in q("select StoreID, DayOfWeek, OpenTime, CloseTime from STORE_TRADING_HOURS"):
    hours[s][day] = (o, c)
NEW_HOURS = {'W1042': ('07:00', '22:00'), 'W1067': ('07:00', '21:00'), 'W1188': ('06:00', '21:00')}
for s in STORES:
    for day in ['Tue', 'Wed', 'Thu', 'Fri']:
        o, c = NEW_HOURS[s]
        hours[s][day] = (o, c)
        add('STORE_TRADING_HOURS', s, day, o, c)

for cid, name, level, parent in [
    ('A14', 'Aisle 14 - Frozen', 'Aisle', None),
    ('C12', 'Cheese', 'Category', 'A10'),
    ('C13', 'Eggs & Butter', 'Category', 'A10'),
    ('C21', 'Pastries', 'Category', 'A11'),
    ('C41', 'Pasta & Sauces', 'Category', 'A13'),
    ('C42', 'Spreads', 'Category', 'A13'),
    ('C43', 'Coffee & Tea', 'Category', 'A13'),
    ('C50', 'Frozen Vegetables', 'Category', 'A14'),
    ('C51', 'Ice Cream', 'Category', 'A14'),
    ('C52', 'Frozen Meals', 'Category', 'A14'),
    ('S31', 'Apples', 'SubCategory', 'C30'),
]:
    add('CATEGORY', cid, name, level, parent)

for sid, name, abn, email, direct in [
    ('SUP05', 'Polar Fresh Foods', '55666777888', 'orders@polarfresh.example', 0),
    ('SUP06', 'Bean Street Roasters', '66777888999', 'trade@beanstreet.example', 0),
    ('SUP07', 'Sunny Hens Farms', '77888999000', None, 0),
]:
    add('SUPPLIER', sid, name, abn, email, direct)
DIRECT = {'SUP01', 'SUP02'}

def gtin(base12):
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(base12))
    return base12 + str((10 - s % 10) % 10)

NEW_PRODUCTS = [
    ('P104', 'Tasty Cheese Block 500g', 'Meadow Gold', '500g', 'Each', 0, 'Perishable', 'C12', 'D03', 8.00, (60, 3.0, 1), ('SUP01', 'DC02', 4.60, 12, 2)),
    ('P105', 'Free Range Eggs 12pk', 'Sunny Hens', '12pk', 'Each', 0, 'Perishable', 'C13', 'D03', 6.90, (28, 4.0, 0), ('SUP07', 'DC02', 4.10, 15, 2)),
    ('P106', 'Salted Butter 250g', 'Valley Fresh', '250g', 'Each', 0, 'Perishable', 'C13', 'D03', 4.20, (90, 3.0, 0), ('SUP01', 'DC02', 2.30, 24, 2)),
    ('P107', 'Own Brand Greek Yoghurt 1kg', 'Everyday Value', '1kg', 'Kg', 1, 'Perishable', 'C11', 'D03', 4.50, (21, 3.0, 1), ('SUP01', 'DC02', 2.50, 12, 2)),
    ('P202', 'Butter Croissants 4pk', 'Golden Crust', '4pk', 'Each', 0, 'Perishable', 'C21', 'D02', 5.50, (3, 18.0, 1), ('SUP02', 'DC01', 2.90, 10, 1)),
    ('P203', 'Own Brand White Bread 700g', 'Everyday Value', '700g', 'Each', 1, 'Perishable', 'C20', 'D02', 2.20, (5, 18.0, 1), ('SUP02', 'DC01', 1.15, 12, 1)),
    ('P204', 'Wholemeal Wraps 8pk', 'Golden Crust', '8pk', 'Each', 0, 'Perishable', 'C20', 'D02', 4.00, (14, 18.0, 1), ('SUP02', 'DC01', 2.10, 12, 1)),
    ('P303', 'Pink Lady Apples 1kg', 'Farm Select', '1kg', 'Kg', 0, 'Perishable', 'S31', 'D01', 5.90, (21, 4.0, 1), ('SUP03', 'DC02', 2.95, 18, 3)),
    ('P304', 'Hass Avocados 4pk', 'Farm Select', '4pk', 'Each', 0, 'Perishable', 'C31', 'D01', 6.50, (7, 10.0, 1), ('SUP03', 'DC01', 3.40, 12, 3)),
    ('P305', 'Brushed Potatoes 2kg', 'Farm Select', '2kg', 'Kg', 0, 'Perishable', 'C31', 'D01', 4.80, (30, 10.0, 0), ('SUP03', 'DC01', 2.20, 10, 3)),
    ('P306', 'Carrots 1kg', 'Farm Select', '1kg', 'Kg', 0, 'Perishable', 'C31', 'D01', 2.50, (21, 4.0, 1), ('SUP03', 'DC02', 1.05, 20, 3)),
    ('P406', 'Pasta Sauce Tomato Basil 500g', 'Delta Harvest', '500g', 'Each', 0, 'Packaged', 'C41', 'D04', 3.80, (18, 'Italy'), ('SUP04', 'DC01', 1.90, 12, 5)),
    ('P407', 'Crunchy Peanut Butter 375g', 'Sunrise Foods', '375g', 'Each', 0, 'Packaged', 'C42', 'D04', 4.70, (12, 'Australia'), ('SUP04', 'DC01', 2.45, 12, 5)),
    ('P408', 'Ground Coffee Espresso 200g', 'Bean Street', '200g', 'Each', 0, 'Packaged', 'C43', 'D04', 9.50, (12, 'Australia'), ('SUP06', 'DC01', 5.20, 12, 4)),
    ('P409', 'English Breakfast Tea 100pk', 'Bean Street', '100pk', 'Each', 0, 'Packaged', 'C43', 'D04', 6.00, (24, 'Sri Lanka'), ('SUP06', 'DC01', 3.10, 12, 4)),
    ('P410', 'Own Brand Spaghetti 500g', 'Everyday Value', '500g', 'Each', 1, 'Packaged', 'C41', 'D04', 1.30, (24, 'Australia'), ('SUP04', 'DC01', 0.65, 24, 5)),
    ('P411', 'Diced Tomatoes 400g', 'Delta Harvest', '400g', 'Each', 0, 'Packaged', 'A13', 'D04', 1.60, (24, 'Italy'), ('SUP04', 'DC01', 0.80, 24, 5)),
    ('P500', 'Frozen Garden Peas 1kg', 'Polar Fresh', '1kg', 'Kg', 0, 'Packaged', 'C50', 'D05', 3.50, (18, 'New Zealand'), ('SUP05', 'DC02', 1.75, 12, 4)),
    ('P501', 'Vanilla Ice Cream 2L', 'Polar Fresh', '2L', 'Litre', 0, 'Packaged', 'C51', 'D05', 7.00, (12, 'Australia'), ('SUP05', 'DC02', 3.60, 6, 4)),
    ('P502', 'Margherita Pizza 400g', 'Polar Fresh', '400g', 'Each', 0, 'Packaged', 'C52', 'D05', 6.50, (9, 'Australia'), ('SUP05', 'DC02', 3.30, 8, 4)),
    ('P503', 'Own Brand Mixed Vegetables 1kg', 'Everyday Value', '1kg', 'Kg', 1, 'Packaged', 'C50', 'D05', 2.80, (18, 'Australia'), ('SUP05', 'DC02', 1.30, 12, 4)),
]
for i, p in enumerate(NEW_PRODUCTS):
    pid, desc, brand, pack, uom, own, ptype, cat, dept, price, sub, sa = p
    add('PRODUCT', pid, gtin('931234500' + pid[1:]), desc, brand, pack, uom, own, ptype, cat, dept)
    if ptype == 'Perishable':
        add('PERISHABLE_PRODUCT', pid, *sub)
    else:
        add('PACKAGED_PRODUCT', pid, *sub)
    sup, dc, cost, carton, lead = sa
    add('SUPPLY_ARRANGEMENT', sup, pid, dc, cost, carton, lead, '2025-09-01')

for sup, pid, dc, cost, carton, lead in [('SUP01', 'P102', 'DC02', 2.90, 12, 2), ('SUP04', 'P401', 'DC01', 3.40, 12, 5),
                                         ('SUP04', 'P402', 'DC01', 1.60, 12, 5), ('SUP04', 'P404', 'DC01', 0.95, 24, 5)]:
    add('SUPPLY_ARRANGEMENT', sup, pid, dc, cost, carton, lead, '2025-09-01')

PRODUCTS = {}
for pid, desc, dept, ptype, own in q("select ProductID, Description, DeptID, ProductType, IsOwnBrand from PRODUCT"):
    PRODUCTS[pid] = dict(desc=desc, dept=dept, type=ptype, own=own)
for p in NEW_PRODUCTS:
    PRODUCTS[p[0]] = dict(desc=p[1], dept=p[8], type=p[6], own=p[5])
SA = {}
for sup, pid, dc, cost, carton, lead in q("select SupplierID, ProductID, DCID, CostPriceExGST, CartonQty, LeadTimeDays from SUPPLY_ARRANGEMENT"):
    SA[pid] = dict(sup=sup, dc=dc, cost=cost, carton=carton, lead=lead)
for r in rows['SUPPLY_ARRANGEMENT']:
    SA[r[1]] = dict(sup=r[0], dc=r[2], cost=r[3], carton=r[4], lead=r[5])
A2_SHELF = {}
for pid, amt in q("select ProductID, Amount from PRICE where PriceType='Shelf' and StoreID='W1042'"):
    A2_SHELF[pid] = amt
BASE_PRICE = dict(A2_SHELF)
BASE_PRICE.update({'P103': 3.90, 'P201': 4.90, 'P302': 2.90, 'P401': 6.50, 'P402': 3.00, 'P404': 1.90})
for p in NEW_PRODUCTS:
    BASE_PRICE[p[0]] = p[9]

existing_sh = {(s, p) for s, p in q("select StoreID, ProductID from STOCK_HOLDING")}
RANGE = {s: set() for s in STORES}
for s, p in existing_sh:
    RANGE[s].add(p)
AISLE = {'D03': 'A10', 'D02': 'A11', 'D01': 'A12', 'D04': 'A13', 'D05': 'A14'}
METRO_SKIP = {'P103', 'P305', 'P403', 'P405', 'P411', 'P410', 'P406'}
for s in STORES:
    for pid, info in sorted(PRODUCTS.items()):
        if info['dept'] not in STORE_DEPTS[s]:
            continue
        if s == 'W1188' and pid in METRO_SKIP:
            continue
        if (s, pid) in existing_sh:
            continue
        RANGE[s].add(pid)
        cap = rng.choice([40, 60, 80, 100, 120]) if s != 'W1188' else rng.choice([24, 30, 36, 40])
        qty = rng.randint(int(cap * 0.2), cap)
        mind = int(round(cap * rng.uniform(0.25, 0.35)))
        if s == 'W1188':
            loc = f"M{rng.randint(1, 4)}-{rng.randint(1, 12):02d}"
        else:
            loc = f"{AISLE[info['dept']]}-{rng.choice('ABCDEFG')}{rng.randint(1, 6)}"
        counted = f"2026-09-20 0{rng.randint(5, 6)}:{rng.choice(['05', '10', '15', '20', '30', '40', '45'])}"
        add('STOCK_HOLDING', s, pid, qty, cap, loc, mind, counted)

price_rows = []
for r in q("select PriceID, StoreID, ProductID, PriceType, Amount, EffectiveFrom, EffectiveTo from PRICE"):
    price_rows.append(tuple(r))
next_pr = [23]
def new_price(s, p, ptype, amt, frm, to):
    pr = f"PR{next_pr[0]:03d}"; next_pr[0] += 1
    row = (pr, s, p, ptype, round(amt, 2), frm, to)
    price_rows.append(row); add('PRICE', *row)
    return pr
have_shelf = {(r[1], r[2]) for r in price_rows if r[3] == 'Shelf'}
def store_price(s, p):
    base = BASE_PRICE[p]
    return round(base * 1.10, 1) if s == 'W1188' else base
for s in STORES:
    for p in sorted(RANGE[s]):
        if (s, p) not in have_shelf:
            new_price(s, p, 'Shelf', store_price(s, p), '2026-07-01', None)

SPECIALS = [('2026-09-09', '2026-09-15', {'P401': 0.75, 'P407': 0.80, 'P501': 0.70, 'P408': 0.75, 'P104': 0.80, 'P303': 0.80}),
            ('2026-09-16', '2026-09-22', {'P400': 0.75, 'P406': 0.70, 'P502': 0.70, 'P105': 0.85, 'P202': 0.80, 'P304': 0.75})]
for frm, to, items in SPECIALS:
    for p, factor in items.items():
        for s in STORES:
            if p in RANGE[s]:
                new_price(s, p, 'Promotional', store_price(s, p) * factor, frm, to)

for day in PERIOD:
    for s in STORES:
        for p in rng.sample(sorted(RANGE[s] & {'P200', 'P201', 'P202', 'P203', 'P300', 'P301', 'P302', 'P304'}), 2):
            new_price(s, p, 'Markdown', store_price(s, p) * 0.5, d2s(day), d2s(day))

def price_for(s, p, when):
    day = d2s(when.date())
    valid = [r for r in price_rows if r[1] == s and r[2] == p and r[5] <= day and (r[6] is None or day <= r[6])]
    promo = [r for r in valid if r[3] == 'Promotional']
    mark = [r for r in valid if r[3] == 'Markdown' and r[6] is not None and when.hour >= 17]
    shelf = [r for r in valid if r[3] == 'Shelf']
    if mark: return mark[0]
    if promo: return promo[0]
    return shelf[0] if shelf else None

NEW_EMP = [
    ('E009', 'Sophie', 'Nguyen', 'W1042', 'D06', 'Team Member', 'Casual', '2025-03-10', 'E001'),
    ('E010', 'Jack', 'Thompson', 'W1067', 'D06', 'Team Member', 'Casual', '2024-07-22', 'E005'),
    ('E011', 'Olivia', 'Brown', 'W1188', 'D06', 'Team Member', 'PartTime', '2023-02-13', 'E007'),
    ('E013', 'Emily', 'Clarke', 'W1042', 'D04', 'Department Manager', 'Permanent', '2017-04-18', 'E001'),
    ('E012', 'Ravi', 'Kumar', 'W1042', 'D05', 'Team Member', 'PartTime', '2022-10-03', 'E013'),
    ('E014', 'Lucas', 'Martin', 'W1067', 'D01', 'Team Member', 'PartTime', '2021-11-29', 'E005'),
    ('E015', 'Isabella', 'Lee', 'W1067', 'D03', 'Team Member', 'Casual', '2025-05-05', 'E005'),
    ('E016', 'Noah', 'Walker', 'W1188', 'D01', 'Team Member', 'Casual', '2024-12-02', 'E007'),
]
for e in NEW_EMP:
    add('EMPLOYEE', *e)
EMP = {}
for r in q("select EmployeeID, HomeStoreID, DeptID, Role from EMPLOYEE"):
    EMP[r[0]] = dict(store=r[1], dept=r[2], role=r[3])
for e in NEW_EMP:
    EMP[e[0]] = dict(store=e[3], dept=e[4], role=e[5])

ROSTER = {
    'E001': {0: ('08:00', '17:00'), 1: ('08:00', '17:00'), 2: ('08:00', '17:00'), 3: ('08:00', '17:00'), 4: ('08:00', '17:00')},
    'E002': {0: ('06:00', '14:00'), 1: ('06:00', '14:00'), 3: ('06:00', '14:00'), 4: ('06:00', '14:00'), 5: ('06:00', '14:00')},
    'E003': {0: ('07:00', '13:00'), 2: ('07:00', '13:00'), 4: ('07:00', '13:00'), 6: ('07:00', '15:00')},
    'E004': {0: ('14:00', '22:00'), 2: ('14:00', '22:00'), 4: ('14:00', '22:00'), 5: ('12:00', '20:00'), 6: ('12:00', '20:00')},
    'E009': {0: ('07:00', '15:00'), 1: ('07:00', '15:00'), 3: ('14:00', '22:00'), 5: ('07:00', '15:00'), 6: ('08:00', '16:00')},
    'E012': {1: ('08:00', '14:00'), 3: ('08:00', '14:00'), 5: ('08:00', '14:00')},
    'E013': {0: ('08:00', '16:00'), 1: ('08:00', '16:00'), 2: ('08:00', '16:00'), 3: ('08:00', '16:00'), 4: ('08:00', '16:00')},
    'E005': {0: ('08:00', '17:00'), 1: ('08:00', '17:00'), 2: ('08:00', '17:00'), 3: ('08:00', '17:00'), 4: ('08:00', '17:00')},
    'E006': {0: ('05:00', '11:00'), 1: ('05:00', '11:00'), 2: ('05:00', '11:00'), 3: ('05:00', '11:00'), 4: ('05:00', '11:00'), 5: ('05:00', '11:00')},
    'E010': {0: ('07:00', '15:00'), 1: ('13:00', '21:00'), 2: ('07:00', '15:00'), 3: ('13:00', '21:00'), 4: ('07:00', '15:00'), 5: ('08:00', '16:00'), 6: ('08:00', '16:00')},
    'E014': {0: ('06:00', '12:00'), 2: ('06:00', '12:00'), 4: ('06:00', '12:00'), 5: ('06:00', '12:00')},
    'E015': {1: ('14:00', '20:00'), 3: ('14:00', '20:00'), 5: ('14:00', '20:00'), 6: ('14:00', '20:00')},
    'E007': {0: ('08:00', '17:00'), 1: ('08:00', '17:00'), 2: ('08:00', '17:00'), 3: ('08:00', '17:00'), 4: ('08:00', '17:00')},
    'E008': {0: ('08:00', '16:00'), 2: ('08:00', '16:00'), 4: ('08:00', '16:00'), 5: ('09:00', '17:00')},
    'E011': {0: ('06:30', '14:30'), 1: ('06:30', '14:30'), 2: ('12:30', '20:30'), 3: ('06:30', '14:30'), 4: ('12:30', '20:30')},
    'E016': {0: ('06:00', '12:00'), 1: ('06:00', '12:00'), 3: ('06:00', '12:00'), 5: ('08:00', '14:00'), 6: ('09:00', '15:00')},
}
shifts = []
n_sh = 9
for day in PERIOD:
    wd = day.weekday()
    for emp, plan in ROSTER.items():
        for key, (st, en) in plan.items():
            if key != wd:
                continue

            if EMP[emp]['role'] == 'Team Member' and rng.random() < 0.12:
                continue
            hrs = (dt.datetime.strptime(en, '%H:%M') - dt.datetime.strptime(st, '%H:%M')).seconds / 3600
            brk = 30 if hrs > 6 else 20
            sid = f"SH{n_sh:03d}"; n_sh += 1
            shifts.append((sid, emp, EMP[emp]['store'], EMP[emp]['dept'], d2s(day), st, en, brk))
for s in shifts:
    add('SHIFT', *s)

def on_shift(store, when, dept=None, front_end=False):
    out = []
    for sid, emp, st, dp, day, a, b, brk in shifts:
        if st != store or day != d2s(when.date()):
            continue
        if not (a <= when.strftime('%H:%M') < b):
            continue
        if front_end and not (dp == 'D06' and EMP[emp]['role'] == 'Team Member'):
            continue
        if dept and dp != dept:
            continue
        out.append(emp)
    return out

FIRST = ['Olivia', 'Liam', 'Mia', 'Ethan', 'Zoe', 'Lucas', 'Grace', 'Henry', 'Isla', 'Jacob', 'Ruby', 'Oscar', 'Amelia', 'Leo',
         'Sienna', 'Mason', 'Priya', 'Thomas', 'Hannah', 'Kai', 'Layla', 'Samuel', 'Anika', 'Daniel', 'Ella', 'Omar', 'Sofia',
         'William', 'Mei', 'James', 'Fatima', 'Harrison', 'Jasmine', 'Ryan', 'Nadia', 'Tariq', 'Emma', 'Hugo', 'Yuki', 'Bella',
         'Charlotte', 'Max', 'Aria', 'Felix']
LAST = ['Nguyen', 'Smith', 'Williams', 'Brown', 'Wilson', 'Taylor', 'Johnson', 'White', 'Martin', 'Anderson', 'Le', 'Walker',
        'Harris', 'Lee', 'Ryan', 'Robinson', 'Kelly', 'King', 'Chen', 'Singh', 'Ali', 'Khan', 'Murphy', 'Wright', 'Hughes',
        'Patel', 'Wang', 'Zhang', 'Rossi', 'Haddad', 'Ahmed', 'Sato', 'Kim', 'Park', 'Fernando', 'Silva', 'Novak', 'Kowalczyk',
        'Murray', 'Bennett', 'Gill', 'Tran', 'Morris', 'Reid']
assert len(FIRST) >= 44 and len(LAST) >= 44, (len(FIRST), len(LAST))
SEGMENTS = ['family', 'health', 'budget', 'breakfast', 'cook']
MEMBER_SEG = {'M0001': 'family', 'M0002': 'breakfast', 'M0003': 'family', 'M0004': 'cook', 'M0005': 'health', 'M0006': 'family'}
MEMBER_HOME = {m: h for m, h in q("select MemberID, HomeStoreID from LOYALTY_MEMBER")}
lasts = LAST[:]; rng.shuffle(lasts)
for i in range(44):
    mid = f"M{7 + i:04d}"
    seg = SEGMENTS[i % 5]
    if seg == 'breakfast':
        home = rng.choices(STORES, [0.3, 0.2, 0.5])[0]
    else:
        home = rng.choices(STORES, [0.5, 0.35, 0.15])[0]
    fn, ln = FIRST[i], lasts[i]
    email = None if rng.random() < 0.2 else f"{fn[0].lower()}.{ln.lower()}{rng.randint(1, 99)}@example.com"
    join = D(2018, 1, 1) + dt.timedelta(days=rng.randint(0, 3100))
    pts = rng.randint(0, 120) * 100 + rng.randint(0, 99)
    add('LOYALTY_MEMBER', mid, fn, ln, email, d2s(join), pts, home)
    MEMBER_SEG[mid] = seg; MEMBER_HOME[mid] = home

PREF = {
    'family':    {'P100': 9, 'P103': 4, 'P200': 5, 'P203': 4, 'P300': 8, 'P303': 6, 'P400': 6, 'P105': 6, 'P106': 4, 'P404': 4,
                  'P406': 4, 'P501': 4, 'P502': 4, 'P104': 5},
    'health':    {'P102': 7, 'P302': 7, 'P304': 7, 'P301': 6, 'P306': 5, 'P401': 6, 'P402': 4, 'P200': 4, 'P204': 5, 'P303': 5,
                  'P101': 6, 'P105': 3},
    'budget':    {'P103': 9, 'P402': 6, 'P203': 8, 'P410': 7, 'P107': 6, 'P503': 5, 'P305': 5, 'P300': 5, 'P411': 5, 'P404': 2},
    'breakfast': {'P408': 8, 'P409': 6, 'P202': 6, 'P101': 8, 'P102': 6, 'P300': 6, 'P401': 6, 'P201': 4, 'P407': 4, 'P200': 3},
    'cook':      {'P403': 6, 'P405': 6, 'P411': 7, 'P404': 6, 'P406': 6, 'P305': 6, 'P306': 6, 'P301': 6, 'P104': 5, 'P106': 4,
                  'P410': 3, 'P500': 3},
}
POPULAR = {'P100': 10, 'P101': 6, 'P200': 7, 'P203': 5, 'P300': 9, 'P303': 5, 'P105': 5, 'P400': 4, 'P102': 4, 'P301': 4,
           'P408': 3, 'P404': 3, 'P305': 3, 'P302': 3, 'P501': 3, 'P202': 3, 'P406': 3, 'P104': 3}

def pick_products(store, seg, n):
    ranged = RANGE[store]
    chosen = []
    for _ in range(n * 4):
        if len(chosen) >= n: break
        if seg and rng.random() < 0.8:
            pool = {p: w for p, w in PREF[seg].items() if p in ranged}
        else:
            pool = {p: w for p, w in POPULAR.items() if p in ranged}
        if not pool: continue
        p = rng.choices(list(pool), list(pool.values()))[0]
        if p not in chosen: chosen.append(p)
    return chosen

def rand_time(store, day):
    o, c = hours[store][DOW[day.weekday()]]
    oh, om = map(int, o.split(':')); ch, cm = map(int, c.split(':'))
    start = oh * 60 + om; end = ch * 60 + cm - 10
    peaks = [(8 * 60 + 30, 70), (12 * 60 + 30, 60), (17 * 60 + 45, 75)]
    while True:
        mu, sd = rng.choice(peaks)
        m = int(rng.gauss(mu, sd))
        if start <= m <= end:
            return dt.datetime.combine(day, dt.time(m // 60, m % 60))

PER_DAY = {'W1042': 13, 'W1067': 7, 'W1188': 5}
members_by_home = {s: [m for m, h in MEMBER_HOME.items() if h == s] for s in STORES}
all_members = list(MEMBER_HOME)
sales = []
n_sale = 13
for day in PERIOD:
    weekend = day.weekday() >= 5
    for store in STORES:
        count = PER_DAY[store] + (2 if weekend and store != 'W1188' else 0) + rng.randint(-2, 2)
        for _ in range(count):
            when = rand_time(store, day)
            member = None
            if rng.random() < 0.72:
                member = rng.choice(members_by_home[store]) if rng.random() < 0.85 else rng.choice(all_members)
            channel = 'Online' if store != 'W1188' and rng.random() < 0.12 else 'InStore'
            operator = None
            if channel == 'InStore':
                fe = on_shift(store, when, front_end=True)
                if fe and rng.random() < 0.55:
                    operator = rng.choice(fe)
            tender = 'Card' if channel == 'Online' or rng.random() < 0.86 else 'Cash'
            n_lines = rng.choices([1, 2, 3, 4, 5, 6], [10, 20, 25, 22, 14, 9])[0]
            prods = pick_products(store, MEMBER_SEG.get(member), n_lines)
            lines = []
            for p in prods:
                pr = price_for(store, p, when)
                if pr is None: continue
                qty = rng.choices([1, 2, 3, 4], [62, 26, 9, 3])[0]
                lines.append((p, qty, pr[4], pr[0]))
            if not lines: continue
            sid = f"SA{n_sale:04d}"; n_sale += 1
            sales.append((sid, store, when.strftime('%Y-%m-%d %H:%M'), channel, operator, member, tender, lines))
sales.sort(key=lambda s: s[2])

for i, s in enumerate(sales):
    sid = f"SA{13 + i:04d}"
    add('SALE', sid, s[1], s[2], s[3], s[4], s[5], s[6])
    for ln, (p, qty, amt, pr) in enumerate(s[7], start=1):
        add('SALE_LINE', sid, ln, p, qty, amt, pr)

orders = []
n_ro = 7
for day in PERIOD[:-1]:
    for store in STORES:
        for p in rng.sample(sorted(RANGE[store]), 2):
            info = SA[p]
            required = day + dt.timedelta(days=min(info['lead'], 2))
            qty = info['carton'] * rng.randint(2, 6)
            if required >= D(2026, 9, 20):
                status = 'Open'
            else:
                status = rng.choices(['Filled', 'PartFilled', 'Cancelled'], [80, 14, 6])[0]
            oid = f"RO{n_ro:03d}"; n_ro += 1
            orders.append((oid, store, p, qty, d2s(day) + ' 18:00', d2s(required), status))
for o in orders:
    add('REPLENISHMENT_ORDER', *o)

CONSIGNOR_OF_DC = {'DC01': 'CN01', 'DC02': 'CN02'}
DIRECT_CN = {'SUP01': 'CN03', 'SUP02': 'CN04'}
deliveries = {}
for oid, store, p, qty, raised, required, status in orders:
    if status == 'Cancelled':
        continue
    info = SA[p]
    cn = DIRECT_CN[info['sup']] if info['sup'] in DIRECT and rng.random() < 0.5 else CONSIGNOR_OF_DC[info['dc']]
    if status == 'PartFilled':
        dq = max(info['carton'], int(qty * rng.uniform(0.5, 0.85)) // info['carton'] * info['carton'])
    else:
        dq = qty
    rej = 0 if rng.random() < 0.9 else rng.randint(1, 3)
    deliveries.setdefault((store, required, cn), []).append((p, dq, rej, oid))

for day in PERIOD:
    for store in STORES:
        if rng.random() < 0.35:
            p = rng.choice([x for x in ['P200', 'P201', 'P203', 'P204', 'P202'] if x in RANGE[store]] or ['P200'])
            deliveries.setdefault((store, d2s(day), 'CN04'), []).append((p, SA[p]['carton'] * rng.randint(1, 3), 0, None))
        if rng.random() < 0.2:
            p = rng.choice([x for x in ['P100', 'P101', 'P103'] if x in RANGE[store]])
            deliveries.setdefault((store, d2s(day), 'CN03'), []).append((p, SA[p]['carton'] * rng.randint(1, 3), 0, None))
n_dlv = 8
for (store, day, cn), lines in sorted(deliveries.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])):
    did = f"DLV{n_dlv:03d}"; n_dlv += 1
    in_transit = day >= '2026-09-20'
    arrival = None if in_transit else f"{day} 0{rng.randint(4, 6)}:{rng.choice(['05', '15', '25', '35', '45', '55'])}"
    status = 'InTransit' if in_transit else 'Received'
    cartons = sum(math.ceil(dq / SA[p]['carton']) for p, dq, rej, oid in lines)
    add('DELIVERY', did, cn, store, day, arrival, status, cartons)
    for ln, (p, dq, rej, oid) in enumerate(lines, start=1):
        add('DELIVERY_LINE', did, ln, p, dq, rej if not in_transit else 0, oid)

n_ws = 8
shortlife = ['P200', 'P201', 'P202', 'P203', 'P204', 'P300', 'P301', 'P302', 'P303', 'P304', 'P306', 'P102', 'P107', 'P105', 'P104', 'P501']
for _ in range(34):
    sid, emp, store, dept, day, a, b, brk = rng.choice([s for s in shifts if EMP[s[1]]['role'] != 'Store Manager' and s[3] != 'D06'])
    cands = [p for p in shortlife if p in RANGE[store] and PRODUCTS[p]['dept'] == dept] or [p for p in shortlife if p in RANGE[store]]
    p = rng.choice(cands)
    reason = rng.choices(['Expired', 'Spoilage', 'Damaged', 'Recall'], [45, 35, 18, 2])[0]
    qty = rng.randint(1, 9)
    ah, am = map(int, a.split(':')); bh, bm = map(int, b.split(':'))
    m = rng.randint(max(ah * 60 + am, (bh * 60 + bm) - 120), bh * 60 + bm - 5)
    when = f"{day} {m // 60:02d}:{m % 60:02d}"
    add('WASTAGE', f"WS{n_ws:03d}", store, p, emp, when, qty, reason, round(qty * SA[p]['cost'], 2))
    n_ws += 1

ORDER = ['STORE_TRADING_HOURS', 'CATEGORY', 'SUPPLIER', 'PRODUCT', 'PERISHABLE_PRODUCT', 'PACKAGED_PRODUCT',
         'SUPPLY_ARRANGEMENT', 'STOCK_HOLDING', 'EMPLOYEE', 'SHIFT', 'LOYALTY_MEMBER', 'PRICE', 'SALE', 'SALE_LINE',
         'REPLENISHMENT_ORDER', 'DELIVERY', 'DELIVERY_LINE', 'WASTAGE']
def lit(v):
    if v is None: return 'NULL'
    if isinstance(v, str): return "'" + v.replace("'", "''") + "'"
    if isinstance(v, float): return f"{v:.2f}"
    return str(v)
with open('extension_data.sql', 'w') as f:
    f.write("-- PRT563 Assessment 4 - Syd_Group_09 - extra sample data added to the Assessment 2 database\n"
            "PRAGMA foreign_keys = ON;\n\n")
    for t in ORDER:
        rs = rows.get(t, [])
        for i in range(0, len(rs), 50):
            chunk = rs[i:i + 50]
            f.write(f"INSERT INTO {t} VALUES\n" + ",\n".join(" (" + ",".join(lit(v) for v in r) + ")" for r in chunk) + ";\n")
        f.write("\n")
print({t: len(rows.get(t, [])) for t in ORDER})
