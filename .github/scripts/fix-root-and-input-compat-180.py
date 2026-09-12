from pathlib import Path

# 1) Let Geeklog 2.2.x autoload its native Geeklog\Input class first.
path = Path('include/input_compat_180.php')
data = path.read_bytes()
old = b"if (!class_exists(__NAMESPACE__ . '\\\\Input', false)) {"
new = b"if (!class_exists(__NAMESPACE__ . '\\\\Input', true)) {"
if data.count(old) != 1:
    raise SystemExit('Expected Input class_exists guard exactly once, found %d' % data.count(old))
path.write_bytes(data.replace(old, new))

# 2) Root album is virtual and cannot contain media. Reject it centrally before
# any file is moved or database row is created.
path = Path('include/lib-upload.php')
data = path.read_bytes()
old = b"""    require_once $_CONF['path'] . 'plugins/mediagallery/include/classAlbum.php';\n    $album = new mgAlbum($album_id);\n    $root_album = new mgAlbum(0);\n\n    if ($_MG_CONF['verbose']) {\n"""
new = b"""    require_once $_CONF['path'] . 'plugins/mediagallery/include/classAlbum.php';\n    $album = new mgAlbum($album_id);\n    $root_album = new mgAlbum(0);\n\n    // Album 0 is MediaGallery's virtual root container. It can contain albums,\n    // but it is not a persistent mg_albums row and must never receive media.\n    if ((int) $album_id <= 0 || !isset($album->id) || !$album->valid) {\n        COM_errorLog('MediaGallery: refused media upload to invalid/root album id ' . intval($album_id), 1);\n        return array(false, $LANG_MG02['album_nonexist']);\n    }\n\n    if ($_MG_CONF['verbose']) {\n"""
if data.count(old) != 1:
    raise SystemExit('Expected MG_getFile album initialization block exactly once, found %d' % data.count(old))
path.write_bytes(data.replace(old, new))
