from pathlib import Path
import re

roots = [Path('templates'), Path('public_html/frames')]
files = sorted(set(p for root in roots for p in root.rglob('*.thtml')))

print('PUBLIC_MARKUP_AUDIT')

# Inventory headings, images, anchors, layout tables and legacy presentational attrs.
for p in files:
    text = p.read_text(encoding='utf-8', errors='strict')
    rel = str(p)
    issues = []

    # headings
    h1 = len(re.findall(r'<h1\b', text, re.I))
    h2 = len(re.findall(r'<h2\b', text, re.I))
    if h1:
        issues.append('H1=%d' % h1)
    if h2:
        issues.append('H2=%d' % h2)

    # img without alt attribute
    for m in re.finditer(r'<img\b[^>]*>', text, re.I | re.S):
        tag = m.group(0)
        if not re.search(r'\balt\s*=', tag, re.I):
            line = text.count('\n', 0, m.start()) + 1
            issues.append('IMG_NO_ALT@%d:%s' % (line, re.sub(r'\s+', ' ', tag)[:180]))

    # anchors with no textual/template-variable/image content
    for m in re.finditer(r'<a\b[^>]*>(.*?)</a>', text, re.I | re.S):
        inner = re.sub(r'<!--.*?-->', '', m.group(1), flags=re.S).strip()
        visible = re.sub(r'<[^>]+>', '', inner).strip()
        if not visible and not re.search(r'\{[^}]+\}|<img\b|aria-label\s*=|title\s*=', inner, re.I):
            line = text.count('\n', 0, m.start()) + 1
            issues.append('EMPTY_LINK@%d:%s' % (line, re.sub(r'\s+', ' ', m.group(0))[:180]))

    # legacy presentational markup / likely layout tables
    for pat, label in [
        (r'<table\b[^>]*(?:cellpadding|cellspacing|border)\s*=', 'TABLE_PRESENTATION_ATTR'),
        (r'<(?:td|th)\b[^>]*(?:align|valign|width|height)\s*=', 'CELL_PRESENTATION_ATTR'),
        (r'<br\{xhtml\}>\s*<br\{xhtml\}>', 'DOUBLE_BR'),
        (r'<center\b', 'CENTER_TAG'),
    ]:
        for m in re.finditer(pat, text, re.I):
            line = text.count('\n', 0, m.start()) + 1
            issues.append('%s@%d' % (label, line))

    # potentially risky fixed width/height attributes in public templates
    for m in re.finditer(r'<(?:table|div|iframe|object|embed|video|audio)\b[^>]*(?:width|height)="(?:[4-9]\d\d|\d{4,})"[^>]*>', text, re.I):
        line = text.count('\n', 0, m.start()) + 1
        issues.append('FIXED_LARGE_DIM@%d:%s' % (line, re.sub(r'\s+', ' ', m.group(0))[:180]))

    if issues:
        print('\n' + rel)
        for issue in issues:
            print('  ' + issue)
