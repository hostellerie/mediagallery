from pathlib import Path
import re

root = Path('templates')
controls = []
for path in sorted(root.rglob('*.thtml')):
    text = path.read_text(encoding='utf-8', errors='replace')
    for m in re.finditer(r'<(input|select|textarea)\b[^>]*>', text, re.I | re.S):
        tag = re.sub(r'\s+', ' ', m.group(0)).strip()
        if re.search(r'type\s*=\s*["\'](?:hidden|submit|button|reset|image)["\']', tag, re.I):
            continue
        name = re.search(r'\bname\s*=\s*["\']([^"\']+)', tag, re.I)
        ident = re.search(r'\bid\s*=\s*["\']([^"\']+)', tag, re.I)
        controls.append((str(path), m.start(), m.group(1).lower(), name.group(1) if name else '', ident.group(1) if ident else '', tag[:220]))

print('FORM_CONTROL_COUNT=%d' % len(controls))
for path, pos, kind, name, ident, tag in controls:
    status = 'HAS_ID' if ident else 'NO_ID'
    print('%s\t%s\t%s\tname=%s\tid=%s\t%s' % (status, path, kind, name, ident, tag))
