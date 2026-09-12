from pathlib import Path

path = Path('include/lib-media.php')
text = path.read_text(encoding='latin-1')
old = """                if ($media_size_disp == false) {\n                    $fname = 'missing.png';\n                    $u_image = $_MG_CONF['mediaobjects_url'] . '/' . $fname;\n                    $p_image = $_MG_CONF['path_mediaobjects']      . $fname;\n                    $media_size_disp = @getimagesize($pimage);\n                }\n"""
new = """                if ($media_size_disp == false) {\n                    /* Built-in fallback image is a plugin asset, not site media. */\n                    $fname = 'missing.png';\n                    $u_image = $_MG_CONF['site_url'] . '/mediaobjects/' . $fname;\n                    $p_image = $_MG_CONF['path_html'] . 'mediaobjects/' . $fname;\n                    $media_size_disp = @getimagesize($p_image);\n                }\n"""
if text.count(old) != 1:
    raise SystemExit('Expected JPEG fallback block exactly once, found %d' % text.count(old))
path.write_text(text.replace(old, new), encoding='latin-1')
