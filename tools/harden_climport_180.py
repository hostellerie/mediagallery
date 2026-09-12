from pathlib import Path

p = Path('climport.php')
text = p.read_text()

old = """        $srcFile = $directory . $file;
        $baseSrcFile = basename($file);

        if (is_dir($srcFile)) {
            if ($parse_sub) {
                require_once $_CONF['path'] . 'plugins/mediagallery/include/albumedit.php';
                $new_aid = MG_quickCreate($album_id, $baseSrcFile);
                $retmsg .= _processDirectory($album_id, $srcFile, $parse_sub, $delete, $userid) . LB;
            }
        } else {
"""
new = """        $srcFile = $directory . $file;
        $baseSrcFile = basename($file);

        // Do not follow symbolic links during recursive CLI imports. Import
        // sources are administrator-provided, but following a link could make
        // a recursive scan escape the intended source tree.
        if (is_link($srcFile)) {
            $retmsg .= $baseSrcFile . ' - Symbolic links are not imported' . LB;
            continue;
        }

        if (is_dir($srcFile)) {
            if ($parse_sub) {
                require_once $_CONF['path'] . 'plugins/mediagallery/include/albumedit.php';
                $new_aid = MG_quickCreate($album_id, $baseSrcFile);
                if ($new_aid > 0) {
                    $retmsg .= _processDirectory($new_aid, $srcFile, $parse_sub, $delete, $userid) . LB;
                } else {
                    $retmsg .= $baseSrcFile . ' - Unable to create destination album' . LB;
                }
            }
        } else {
"""

if text.count(old) != 1:
    raise SystemExit('CLI recursion block not found exactly once')
text = text.replace(old, new)
p.write_text(text)
