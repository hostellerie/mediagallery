from pathlib import Path

p = Path('.github/mutation-security-patch.py')
text = p.read_text(encoding='utf-8')
start = text.index('# Media manager form token.')
end = text.index('# Manager save token check.')
replacement = '''# Media manager form token.\nneedle = "        'val_reset_cover'         => (($album_cover == '-1') ? ' checked=\\\"checked\\\"' : ''),\\n"\nif needle not in text:\n    raise SystemExit('media manager form token line not found')\ntext = text.replace(\n    needle,\n    needle + "        'gltoken_name'           => CSRF_TOKEN,\\n        'gltoken'                => SEC_createToken(),\\n",\n    1\n)\n\n'''
text = text[:start] + replacement + text[end:]
p.write_text(text, encoding='utf-8')
print('Temporary patch anchor corrected.')
