"""pokecrystal's phone-rematch trainers: for each, the map, the trainer's object position, the fight count's
address (JP = US - $0D), the ready flag (JP), and the party loaded for each fight count when every story condition is
met (post-game), with the party's (species, level) from data/trainers/parties.asm"""
import re, os, json
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ref', 'pokecrystal')

def consts(path, start_pat='const_def'):
    d = {}; i = 0
    for l in open(path):
        s = l.split(';')[0].strip()
        m = re.match(r'const_def\s*(\S+)?', s)
        if m: i = int(m.group(1).replace('$', '0x'), 0) if m.group(1) else 0; continue
        if s.startswith('const_skip'): i += 1; continue
        m = re.match(r'const\s+(\w+)', s)
        if m: d[m.group(1)] = i; i += 1
    return d

def parties():
    """{(CLASS_GROUP_label, idx): [(species, level)]} by trainer class constant name"""
    cls = consts(R + '/constants/trainer_constants.asm')
    # trainer ids per class: the trainerclass blocks list ids in order (const_def 1 inside each)
    ids = {}; cur = None
    for l in open(R + '/constants/trainer_constants.asm'):
        s = l.split(';')[0].strip()
        m = re.match(r'trainerclass\s+(\w+)', s)
        if m: cur = m.group(1); n = 1; continue
        m = re.match(r'const\s+(\w+)', s)
        if m and cur: ids[(cur, m.group(1))] = n; n += 1
    sp = consts(R + '/constants/pokemon_constants.asm')
    groups = {}; g = None; party = None
    order = [x.split()[1].rstrip(',') for x in re.findall(r'dw\s+\w+Group', open(R + '/data/trainers/party_pointers.asm').read())]
    for l in open(R + '/data/trainers/parties.asm'):
        s = l.split(';')[0].strip()
        m = re.match(r'(\w+)Group:', s)
        if m: g = m.group(1) + 'Group'; groups[g] = []; continue
        m = re.match(r'db\s+"[^"]*@",\s*(\w+)', s)
        if m and g: party = []; groups[g].append(party); continue
        m = re.match(r'db\s+(\d+),\s*(\w+)', s)
        if m and party is not None: party.append((sp.get(m.group(2)), int(m.group(1)), m.group(2)))
    return ids, groups, order

def sim(lines, start, count):
    """from 'readmem wXFightCount': follow with every check true; -> (CLASS, ID)"""
    labels = {}; scope = ''
    for i, l in enumerate(lines):
        m = re.match(r'(\.?\w+):', l.strip())
        if m:
            if not m.group(1).startswith('.'): scope = m.group(1)
            labels[(scope if m.group(1).startswith('.') else '', m.group(1))] = i
    scope = ''
    for j in range(start, -1, -1):
        m = re.match(r'(\w+):', lines[j].strip())
        if m: scope = m.group(1); break
    def lab(n): return labels[(scope, n)] if n.startswith('.') else labels[('', n)]
    i = start + 1; steps = 0
    while i < len(lines) and steps < 200:
        s = lines[i].split(';')[0].strip(); steps += 1
        m = re.match(r'ifequal\s+(\d+),\s*(\S+)', s)
        if m:
            if int(m.group(1)) == count: i = lab(m.group(2)); continue
            i += 1; continue
        m = re.match(r'(iftrue|sjump)\s+(\S+)', s)
        if m: i = lab(m.group(2)); continue
        m = re.match(r'loadtrainer\s+(\w+),\s*(\w+)', s)
        if m: return m.group(1), m.group(2)
        i += 1
    return None

def table():
    ids, groups, order = parties()
    fl = consts(R + '/constants/engine_flags.asm')
    out = []
    for f in sorted(x for x in os.listdir(R + '/maps') if x.endswith('.asm')):
        L = open(R + '/maps/' + f).read().split('\n')
        for i, l in enumerate(L):
            m = re.match(r'\s*readmem\s+w(\w+)FightCount', l)
            if not m: continue
            who = m.group(1)
            counts = sorted({int(x) for x in re.findall(r'loadmem\s+w%sFightCount,\s*(\d+)' % who, '\n'.join(L))} | {0})
            fights = {}
            for c in counts:
                r = sim(L, i, c)
                if r:
                    cl, tid = r; gname = cl.title().replace('_', '') + 'Group'
                    fights[c] = (cl, tid, ids.get((cl, tid)))
            # the object of this trainer
            ready = 'ENGINE_%s_READY_FOR_REMATCH' % who.upper()
            out.append({'map': f[:-4], 'who': who, 'count_us': None, 'ready': ready, 'fights': fights})
    return out, ids, groups

if __name__ == '__main__':
    t, ids, groups = table()
    for e in t: print(e['map'], e['who'], e['fights'])

US_FIGHTCOUNT = {'Jack': 0xd9f2, 'Beverly': 0xd9f3, 'Huey': 0xd9f4, 'Gaven': 0xd9f5, 'Beth': 0xd9f6, 'Jose': 0xd9f7,
                 'Reena': 0xd9f8, 'Joey': 0xd9f9, 'Wade': 0xd9fa, 'Ralph': 0xd9fb, 'Liz': 0xd9fc, 'Anthony': 0xd9fd,
                 'Todd': 0xd9fe, 'Gina': 0xd9ff, 'Irwin': 0xda00, 'Arnie': 0xda01, 'Alan': 0xda02, 'Dana': 0xda03,
                 'Chad': 0xda04, 'Derek': 0xda05, 'Tully': 0xda06, 'Brent': 0xda07, 'Tiffany': 0xda08, 'Vance': 0xda09,
                 'Wilton': 0xda0a, 'Kenji': 0xda0b, 'Parry': 0xda0c, 'Erin': 0xda0d}
READY_JP = {}            # who -> (addr, mask): ENGINE_JACK.. from $DC3F bit 0 on, in engine_flags order
_ORDER = ['Jack', 'Huey', 'Gaven', 'Beth', 'Jose', 'Reena', 'Joey', 'Wade', 'Ralph', 'Liz', 'Anthony', 'Todd', 'Gina',
          'Arnie', 'Alan', 'Dana', 'Chad', 'Tully', 'Brent', 'Tiffany', 'Vance', 'Wilton', 'Parry', 'Erin']
for _i, _w in enumerate(_ORDER): READY_JP[_w] = (0xDC12 + _i // 8, 1 << (_i % 8))   # (JP EngineFlags table, 20:4462: $DC12..)

def full():
    t, ids, groups = table()
    _, _, order = parties()
    cls = {}; k = 0
    for l in open(R + '/constants/trainer_constants.asm'):
        m = re.match(r'\s*trainerclass\s+(\w+)', l)
        if m: cls[m.group(1)] = k; k += 1
    res = []
    for e in t:
        L = open(R + '/maps/%s.asm' % e['map']).read()
        m = re.search(r'object_event\s+(\d+),\s*(\d+),[^\n]*Trainer\w*%s\d?\b' % e['who'], L)
        pos = (int(m.group(1)), int(m.group(2))) if m else None
        fights = {}
        for c, (cl, tid, n) in e['fights'].items():
            gname = order[cls[cl] - 1]
            fights[c] = (cl, tid, [(s, l) for s, l, _ in groups[gname][n - 1]])
        nxt = {}
        for c in fights:
            mm = None
        res.append({'map': e['map'], 'who': e['who'], 'pos': pos, 'count': US_FIGHTCOUNT[e['who']] - 0xD,
                    'ready': READY_JP[e['who']], 'fights': fights})
    return res

def group(name):
    """[(species, level), ...] per party of e.g. 'BrockGroup'"""
    _, groups, _ = parties()
    return [[(s, l) for s, l, _ in p] for p in groups[name]]
