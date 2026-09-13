from pathlib import Path
import re
from collections import Counter, defaultdict

rows = []
for path in sorted(Path('templates').rglob('*.thtml')):
    text = path.read_text(encoding='utf-8', errors='replace')
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'\sstyle="([^"]*)"', line):
            style = m.group(1).strip()
            dynamic = '{' in style and '}' in style
            rows.append((str(path), i, 'DYNAMIC' if dynamic else 'STATIC', style))
for path in sorted(Path('public_html/frames').rglob('*.thtml')):
    text = path.read_text(encoding='utf-8', errors='replace')
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r'\sstyle="([^"]*)"', line):
            style = m.group(1).strip()
            dynamic = '{' in style and '}' in style
            rows.append((str(path), i, 'DYNAMIC' if dynamic else 'STATIC', style))

print('INLINE_STYLE_COUNT=%d' % len(rows))
print('STATIC=%d' % sum(1 for r in rows if r[2] == 'STATIC'))
print('DYNAMIC=%d' % sum(1 for r in rows if r[2] == 'DYNAMIC'))
print('\nBY_FILE')
counts = Counter(r[0] for r in rows)
for path, count in counts.most_common():
    print('%4d %s' % (count, path))
print('\nDETAIL')
for row in rows:
    print('%s:%d\t%s\t%s' % row)
