from pathlib import Path

p = Path('.github/mutation-security-patch.py')
text = p.read_text(encoding='utf-8')

# Relax the Media Manager token insertion anchor.
start = text.index('# Media manager form token.')
end = text.index('# Manager save token check.')
replacement = '''# Media manager form token.\nneedle = "        'val_reset_cover'         => (($album_cover == '-1') ? ' checked=\\\"checked\\\"' : ''),\\n"\nif needle not in text:\n    raise SystemExit('media manager form token line not found')\ntext = text.replace(\n    needle,\n    needle + "        'gltoken_name'           => CSRF_TOKEN,\\n        'gltoken'                => SEC_createToken(),\\n",\n    1\n)\n\n'''
text = text[:start] + replacement + text[end:]

# Legacy source files can contain non-UTF-8 bytes. Latin-1 is used only as
# a 1:1 byte transport here; inserted source is ASCII, so no re-encoding occurs.
for path, next_marker in (
    ('include/mediamanage.php', '# ------------------------------------------------------------------\n# public_html/admin.php'),
    ('include/lib-media.php', '# ------------------------------------------------------------------\n# Documentation'),
):
    old = "p = Path('%s')\ntext = p.read_text(encoding='utf-8')" % path
    new = "p = Path('%s')\ntext = p.read_bytes().decode('latin-1')" % path
    if old not in text:
        raise SystemExit(path + ' read anchor not found')
    text = text.replace(old, new, 1)

    old = "p.write_text(text, encoding='utf-8')\n\n" + next_marker
    new = "p.write_bytes(text.encode('latin-1'))\n\n" + next_marker
    if old not in text:
        raise SystemExit(path + ' write anchor not found')
    text = text.replace(old, new, 1)

p.write_text(text, encoding='utf-8')
print('Temporary patch anchors/legacy byte handling corrected.')
