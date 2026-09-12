from pathlib import Path

path = Path('include/common.php')
text = path.read_text()
old = """                $album_last_image = $_MG_CONF['mediaobjects_url'] . '/missing.png';
                $mediasize = @getimagesize($_MG_CONF['path_mediaobjects'] . 'missing.png');"""
new = """                $album_last_image = $_MG_CONF['site_url'] . '/mediaobjects/missing.png';
                $mediasize = @getimagesize($_MG_CONF['path_html'] . 'mediaobjects/missing.png');"""
count = text.count(old)
assert count == 2, f'expected 2 legacy missing.png fallbacks, found {count}'
text = text.replace(old, new)
path.write_text(text)
