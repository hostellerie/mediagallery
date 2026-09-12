from pathlib import Path
import re

roots = [Path('templates'), Path('public_html/frames')]
attrs = ('href', 'src', 'title', 'alt', 'value', 'action', 'onclick', 'style')
pattern = re.compile(r'\b(' + '|'.join(attrs) + r')\s*=\s*(["\'])(.*?)\2', re.I | re.S)
var_pattern = re.compile(r'\{([A-Za-z0-9_]+)\}')

results = []
for root in roots:
    for p in sorted(root.rglob('*.thtml')):
        text = p.read_text(encoding='utf-8', errors='replace')
        for m in pattern.finditer(text):
            value = m.group(3)
            vars_ = sorted(set(var_pattern.findall(value)))
            if vars_:
                line = text.count('\n', 0, m.start()) + 1
                results.append((str(p), line, m.group(1).lower(), value.replace('\n', ' '), ','.join(vars_)))

print('DYNAMIC_ATTRIBUTE_COUNT=%d' % len(results))
for path, line, attr, value, vars_ in results:
    print('%s:%d\t%s\t%s\tvars=%s' % (path, line, attr, value, vars_))

print('\nUNIQUE_VARIABLES_BY_ATTRIBUTE')
for attr in attrs:
    names = sorted(set(v for _, _, a, _, vs in results if a == attr for v in vs.split(',') if v))
    if names:
        print('%s: %s' % (attr, ', '.join(names)))
