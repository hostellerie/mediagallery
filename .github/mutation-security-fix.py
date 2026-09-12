from pathlib import Path

p = Path('.github/mutation-security-patch.py')
text = p.read_text(encoding='utf-8')

# Relax the Media Manager token insertion anchor.
start = text.index('# Media manager form token.')
end = text.index('# Manager save token check.')
replacement = '''# Media manager form token.\nneedle = "        'val_reset_cover'         => (($album_cover == '-1') ? ' checked=\\\"checked\\\"' : ''),\\n"\nif needle not in text:\n    raise SystemExit('media manager form token line not found')\ntext = text.replace(\n    needle,\n    needle + "        'gltoken_name'           => CSRF_TOKEN,\\n        'gltoken'                => SEC_createToken(),\\n",\n    1\n)\n\n'''
text = text[:start] + replacement + text[end:]

# include/mediamanage.php contains legacy non-UTF-8 bytes. Read/write it
# byte-safely through latin-1 so every pre-existing byte is preserved 1:1.
old = "p = Path('include/mediamanage.php')\ntext = p.read_text(encoding='utf-8')"
new = "p = Path('include/mediamanage.php')\ntext = p.read_bytes().decode('latin-1')"
if old not in text:
    raise SystemExit('mediamanage read anchor not found')
text = text.replace(old, new, 1)
old = "p.write_text(text, encoding='utf-8')\n\n# ------------------------------------------------------------------\n# public_html/admin.php"
new = "p.write_bytes(text.encode('latin-1'))\n\n# ------------------------------------------------------------------\n# public_html/admin.php"
if old not in text:
    raise SystemExit('mediamanage write anchor not found')
text = text.replace(old, new, 1)

p.write_text(text, encoding='utf-8')
print('Temporary patch anchors/encoding corrected.')
