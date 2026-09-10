from pathlib import Path

p = Path('include/lib-media.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')
old = """    $retval = MG_getFramedImage($opt['display_skin'], $I['media_title'],
                  $u_pic, $u_image, $media_size_disp[0], $media_size_disp[1]);

    return array($retval, $u_image, $media_size_disp[0], $media_size_disp[1],"""
new = """    $retval = MG_getFramedImage($opt['display_skin'], $I['media_title'],
                  $u_pic, $u_image, $media_size_orig[0], $media_size_orig[1]);

    return array($retval, $u_image, $media_size_orig[0], $media_size_orig[1],"""
count = text.count(old)
if count != 2:
    raise SystemExit('expected ASF/MOV return block twice, found %d' % count)
text = text.replace(old, new)
p.write_text(text, encoding='utf-8', errors='surrogateescape')
