from pathlib import Path

p = Path('include/lib-media.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')
start = text.find('function MG_displayMP3(')
end = text.find('function MG_displayGeneric(', start)
if start == -1 or end == -1 or end <= start:
    raise SystemExit('unable to isolate MG_displayMP3')
block = text[start:end]
old = """    $retval = MG_getFramedImage($opt['display_skin'], $I['media_title'],
                  $u_pic, $u_image, $media_size_disp[0], $media_size_disp[1]);

    return array($retval, $u_image, $media_size_disp[0], $media_size_disp[1], $u_pic);
"""
new = """    $retval = MG_getFramedImage($opt['display_skin'], $I['media_title'],
                  $u_pic, $u_image, $media_size_orig[0], $media_size_orig[1]);

    return array($retval, $u_image, $media_size_orig[0], $media_size_orig[1], $u_pic);
"""
if block.count(old) != 1:
    raise SystemExit('MP3 final size block not found exactly once')
block = block.replace(old, new, 1)
text = text[:start] + block + text[end:]
p.write_text(text, encoding='utf-8', errors='surrogateescape')
