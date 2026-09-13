from pathlib import Path
import re

# Static declarations map to a small reusable MediaGallery presentation layer.
DECL_CLASSES = {
    'text-align:center': 'mg-text-center',
    'text-align:left': 'mg-text-left',
    'text-align:right': 'mg-text-right',
    'vertical-align:top': 'mg-valign-top',
    'vertical-align:middle': 'mg-valign-middle',
    'font-weight:bold': 'mg-fw-bold',
    'font-size:smaller': 'mg-text-small',
    'white-space:nowrap': 'mg-nowrap',
    'float:left': 'mg-float-left',
    'float:right': 'mg-float-right',
    'clear:both': 'mg-clear',
    'width:100%': 'mg-w-full',
    'width:80%': 'mg-w-80',
    'width:50%': 'mg-w-half',
    'width:25%': 'mg-w-quarter',
    'width:15%': 'mg-w-15',
    'width:10%': 'mg-w-10',
    'width:200px': 'mg-w-200',
    'width:180px': 'mg-w-180',
    'width:100px': 'mg-w-100',
    'width:80px': 'mg-w-80px',
    'width:50px': 'mg-select-column',
    'width:auto': 'mg-table-auto',
    'height:25px': 'mg-h-25',
    'height:20px': 'mg-h-20',
    'margin-top:5px': 'mg-mt-xs',
    'margin-top:10px': 'mg-mt-sm',
    'margin-bottom:6px': 'mg-mb-xs',
    'margin-bottom:10px': 'mg-mb-sm',
    'margin-bottom:0.5em': 'mg-mb-half-em',
    'margin:0 auto': 'mg-table-centered',
    'margin:0px auto': 'mg-table-centered',
    'margin:10px 0': 'mg-my-sm',
    'padding:5px 5px 0 0': 'mg-pad-admin-icon',
    'padding:10px': 'mg-pad-md',
    'padding:10px 0': 'mg-py-md',
    'padding-bottom:10px': 'mg-pb-md',
    'line-height:2em': 'mg-line-loose',
    'border:none': 'mg-border-none',
    'border: none': 'mg-border-none',
    'border-top:1px solid #000000': 'mg-border-top',
    'border-top: 1px solid #000000': 'mg-border-top',
}

# Some compound historical declarations are clearer as semantic classes.
EXACT = {
    'width:50%;text-align:center': 'mg-half-center',
    'width:200px;height:25px;margin:0px auto': 'mg-media-rotate-controls',
    'text-align:center;width:100%': 'mg-full-center',
    'white-space:nowrap;width:100px': 'mg-nowrap mg-w-100',
    'padding:10px;line-height:2em': 'mg-pad-md mg-line-loose',
    'font-weight:bold;width:25%;text-align:right': 'mg-fw-bold mg-w-quarter mg-text-right',
}

def canonical(style):
    s = style.strip().strip(';')
    s = re.sub(r'\s*:\s*', ':', s)
    s = re.sub(r'\s*;\s*', ';', s)
    return s

def classes_for(style):
    c = canonical(style)
    if c == '':
        return ''
    if c in EXACT:
        return EXACT[c]
    out = []
    for decl in c.split(';'):
        if decl in DECL_CLASSES:
            out.extend(DECL_CLASSES[decl].split())
        else:
            raise KeyError(decl)
    seen = set()
    return ' '.join(x for x in out if not (x in seen or seen.add(x)))

def convert_tag(match, path, line_hint):
    tag = match.group(0)
    sm = re.search(r'\sstyle="([^"]*)"', tag)
    if not sm:
        return tag
    style = sm.group(1)
    if '{' in style and '}' in style:
        return tag
    try:
        extra = classes_for(style)
    except KeyError as exc:
        raise SystemExit('Unmapped static declaration %s in %s near %s' % (exc.args[0], path, line_hint))
    tag = tag[:sm.start()] + tag[sm.end():]
    if extra:
        cm = re.search(r'\sclass="([^"]*)"', tag)
        if cm:
            merged = (cm.group(1).strip() + ' ' + extra).strip()
            tag = tag[:cm.start()] + ' class="' + merged + '"' + tag[cm.end():]
        else:
            pos = tag.rfind('>')
            before = tag[:pos]
            suffix = tag[pos:]
            if before.endswith('/'):
                before = before[:-1].rstrip() + ' class="' + extra + '"/'
            else:
                before += ' class="' + extra + '"'
            tag = before + suffix
    return tag

# Sweep all templates and frame templates. Dynamic runtime styles are intentionally retained.
paths = sorted(set(list(Path('templates').rglob('*.thtml')) + list(Path('public_html/frames').rglob('*.thtml'))))
for p in paths:
    text = p.read_text(encoding='utf-8', errors='strict')
    def repl(m):
        return convert_tag(m, str(p), text.count('\n', 0, m.start()) + 1)
    text = re.sub(r'<[^>]+\sstyle="[^"]*"[^>]*>', repl, text)
    p.write_text(text, encoding='utf-8')

# Add utility/semantic declarations only once.
p = Path('public_html/style.css')
css = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 residual inline-style utilities */'
if marker not in css:
    css += '''\n\n/* MediaGallery 1.8 residual inline-style utilities */\n.mg-text-right { text-align: right; }\n.mg-valign-top { vertical-align: top; }\n.mg-fw-bold { font-weight: bold; }\n.mg-text-small { font-size: smaller; }\n.mg-nowrap { white-space: nowrap; }\n.mg-float-left { float: left; }\n.mg-float-right { float: right; }\n.mg-w-full { width: 100%; }\n.mg-w-80 { width: 80%; }\n.mg-w-half { width: 50%; }\n.mg-w-quarter { width: 25%; }\n.mg-w-15 { width: 15%; }\n.mg-w-10 { width: 10%; }\n.mg-w-200 { width: 12.5rem; }\n.mg-w-180 { width: 11.25rem; }\n.mg-w-100 { width: 6.25rem; }\n.mg-w-80px { width: 5rem; }\n.mg-h-25 { height: 1.5625rem; }\n.mg-h-20 { height: 1.25rem; }\n.mg-mt-xs { margin-top: 0.3125rem; }\n.mg-mt-sm { margin-top: 0.625rem; }\n.mg-mb-xs { margin-bottom: 0.375rem; }\n.mg-mb-sm { margin-bottom: 0.625rem; }\n.mg-mb-half-em { margin-bottom: 0.5em; }\n.mg-my-sm { margin-top: 0.625rem; margin-bottom: 0.625rem; }\n.mg-pad-admin-icon { padding: 0.3125rem 0.3125rem 0 0; }\n.mg-pad-md { padding: 0.625rem; }\n.mg-py-md { padding-top: 0.625rem; padding-bottom: 0.625rem; }\n.mg-pb-md { padding-bottom: 0.625rem; }\n.mg-line-loose { line-height: 2; }\n.mg-border-none { border: 0; }\n.mg-border-top { border-top: 1px solid currentColor; }\n.mg-half-center { width: 50%; text-align: center; }\n.mg-full-center { width: 100%; text-align: center; }\n.mg-media-rotate-controls { width: 12.5rem; min-height: 1.5625rem; margin: 0 auto; }\n.mg-status-box { width: min(80%, 50rem); margin: 0 auto; }\n.mg-status-line { text-align: center; margin: 0.625rem 0; }\n\n@media (max-width: 34rem) {\n  .mg-w-80,\n  .mg-w-half,\n  .mg-half-center,\n  .mg-status-box { width: 100%; }\n  .mg-w-200,\n  .mg-w-180 { max-width: 100%; }\n  .mg-nowrap { white-space: normal; }\n}\n'''
p.write_text(css, encoding='utf-8')

# Close the review only if no static inline style remains.
static_left = []
for p in paths:
    text = p.read_text(encoding='utf-8')
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'\sstyle="([^"]*)"', line):
            if not ('{' in m.group(1) and '}' in m.group(1)):
                static_left.append((str(p), i, m.group(1)))
if static_left:
    for row in static_left:
        print('STATIC_LEFT %s:%d %s' % row)
    raise SystemExit('Static inline styles remain: %d' % len(static_left))

p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
text = text.replace('- [ ] Review remaining inline presentation styles.\n', '- [x] Review remaining inline presentation styles.\n', 1)
text = text.replace('  - [ ] Classify and resolve the residual inline-style inventory; retain only justified runtime dimensions.\n', '  - [x] Resolve all static inline presentation styles; retain only justified runtime dimensions used by responsive autotag/media sizing.\n', 1)
p.write_text(text, encoding='utf-8')
