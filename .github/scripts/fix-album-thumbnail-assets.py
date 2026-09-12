from pathlib import Path

path = Path('include/common.php')
text = path.read_text()
start = text.index('function MG_albumThumbnail($album_id)')
end = text.index('\nfunction ', start + 1)
block = text[start:end]

replacements = {
    "$_MG_CONF['mediaobjects_url'] . '/empty.png'": "$_MG_CONF['site_url'] . '/mediaobjects/empty.png'",
    "$_MG_CONF['path_mediaobjects'] . 'empty.png'": "$_MG_CONF['path_html'] . 'mediaobjects/empty.png'",
    "$_MG_CONF['mediaobjects_url'] . '/missing.png'": "$_MG_CONF['site_url'] . '/mediaobjects/missing.png'",
    "$_MG_CONF['path_mediaobjects'] . 'missing.png'": "$_MG_CONF['path_html'] . 'mediaobjects/missing.png'",
}

expected = {
    "$_MG_CONF['mediaobjects_url'] . '/empty.png'": 3,
    "$_MG_CONF['path_mediaobjects'] . 'empty.png'": 3,
    "$_MG_CONF['mediaobjects_url'] . '/missing.png'": 3,
    "$_MG_CONF['path_mediaobjects'] . 'missing.png'": 3,
}

for old, count in expected.items():
    found = block.count(old)
    assert found == count, f'expected {count} occurrences of {old}, found {found}'

for old, new in replacements.items():
    block = block.replace(old, new)

text = text[:start] + block + text[end:]
path.write_text(text)
