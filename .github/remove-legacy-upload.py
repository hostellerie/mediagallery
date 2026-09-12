from pathlib import Path
import re

p = Path('include/newmedia.php')
text = p.read_text(encoding='utf-8')

pattern = re.compile(
    r"/\*\*\n \* Save upload\(s\) from the legacy upload endpoint\..*?\nfunction MG_saveUpload\(\$album_id\)\n\{.*?\n\}\n\n(?=/\*\*\n \* Browser upload form\.)",
    re.S,
)
text2, count = pattern.subn('', text, count=1)
if count != 1:
    raise SystemExit('MG_saveUpload block not found exactly once')
p.write_text(text2, encoding='utf-8')

p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
roadmap = roadmap.replace(
    '- [ ] Decide whether the legacy async upload endpoint can now be removed.',
    '- [x] Remove the orphaned legacy asynchronous upload endpoint and its dedicated `MG_saveUpload()` handler after confirming the active browser upload uses `admin.php` / `MG_saveUserUpload()`.'
)
roadmap = roadmap.replace(
    '- [ ] Decide fate of `functions_legacy.inc` and the legacy async endpoint.',
    '- [ ] Decide fate of `functions_legacy.inc`; the legacy async upload endpoint has been removed.'
)
p.write_text(roadmap, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
notes = notes.replace(
    '- whether the legacy async endpoint can be removed completely after live compatibility testing.',
    '- the orphaned legacy asynchronous `public_html/upload.php` endpoint and its dedicated `MG_saveUpload()` handler have been removed; the maintained browser upload path is `admin.php` / `MG_saveUserUpload()`.'
)
p.write_text(notes, encoding='utf-8')

print('Legacy async upload handler removed and docs updated.')
