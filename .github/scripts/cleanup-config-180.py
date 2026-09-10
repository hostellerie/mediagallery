from pathlib import Path
import re

p = Path('install_defaults.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')

patterns = [
    r"^\s*'use_flowplayer'\s*=>\s*'0',\s*$",
    r"^\s*\$c->add\('use_flowplayer'.*$",
]
for pattern in patterns:
    text, count = re.subn(pattern, '', text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit('expected use_flowplayer line not found exactly once: ' + pattern)

swf_names = [
    'swf_play', 'swf_menu', 'swf_scale', 'swf_wmode', 'swf_allowscriptaccess',
    'swf_quality', 'swf_loop', 'swf_bgcolor', 'swf_width', 'swf_height',
    'swf_flashvars', 'swf_version'
]
for name in swf_names:
    default_pattern = r"^\s*'" + re.escape(name) + r"'\s*=>.*$"
    text, count = re.subn(default_pattern, '', text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit('SWF default not found exactly once: ' + name)

    add_pattern = r"^\s*\$c->add\('" + re.escape(name) + r"'.*$"
    text, count = re.subn(add_pattern, '', text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit('SWF config entry not found exactly once: ' + name)

for structural in ('tab_flashmedia', 'fs_flashmedia'):
    pattern = r"^\s*\$c->add\('" + structural + r"'.*$"
    text, count = re.subn(pattern, '', text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit('Flash config structure not found exactly once: ' + structural)

text = text.replace('    // Flash Media Player\n', '', 1)

p.write_text(text, encoding='utf-8', errors='surrogateescape')
