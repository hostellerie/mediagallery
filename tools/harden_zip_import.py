from pathlib import Path

path = Path('include/lib-upload.php')
text = path.read_text()

start = text.index('function MG_processZip($filename, $album_id, $purgefiles, $tmpdir)')
end = text.index('\nfunction MG_processDir(', start)

new = r'''function MG_isSafeZipEntryName($entry)
{
    $entry = str_replace('\\', '/', (string) $entry);

    if ($entry === '' || strlen($entry) > 1024 || strpos($entry, "\0") !== false) {
        return false;
    }
    if ($entry[0] === '/' || preg_match('/^[A-Za-z]:\//', $entry)) {
        return false;
    }

    foreach (explode('/', $entry) as $segment) {
        if ($segment === '..') {
            return false;
        }
    }

    return true;
}

function MG_pathIsInside($path, $root)
{
    $path = realpath($path);
    $root = realpath($root);
    if ($path === false || $root === false) {
        return false;
    }

    $root = rtrim($root, '/\\');
    if (PHP_OS === 'WINNT') {
        $path = strtolower($path);
        $root = strtolower($root);
    }

    return $path === $root || strpos($path, $root . DIRECTORY_SEPARATOR) === 0;
}

function MG_validateExtractedZipTree($root)
{
    if (!is_dir($root) || is_link($root)) {
        return false;
    }

    $handle = @opendir($root);
    if ($handle === false) {
        return false;
    }

    while (($entry = readdir($handle)) !== false) {
        if ($entry === '.' || $entry === '..') {
            continue;
        }

        $path = $root . DIRECTORY_SEPARATOR . $entry;
        if (is_link($path) || !MG_pathIsInside($path, $root)) {
            closedir($handle);
            return false;
        }

        if (is_dir($path) && !MG_validateExtractedZipTree($path)) {
            closedir($handle);
            return false;
        }
    }

    closedir($handle);
    return true;
}

function MG_processZip($filename, $album_id, $purgefiles, $tmpdir)
{
    global $_MG_CONF, $LANG_MG02;

    $zipBinary = rtrim($_MG_CONF['zip_path'], '/\\') . DIRECTORY_SEPARATOR . 'unzip';
    $tmpBase = rtrim($_MG_CONF['tmp_path'], '/\\') . DIRECTORY_SEPARATOR;
    $tmpLeaf = basename((string) $tmpdir);

    if ($tmpLeaf === '' || $tmpLeaf === '.' || $tmpLeaf === '..' || $tmpLeaf !== (string) $tmpdir) {
        COM_errorLog('MediaGallery: rejected unsafe ZIP temporary directory name.', 1);
        return $LANG_MG02['generic_error'];
    }

    // Inspect member names before extraction to prevent Zip Slip while
    // preserving the configured external unzip backend.
    $listCmd = escapeshellarg($zipBinary) . ' -Z1 ' . escapeshellarg($filename);
    list($entries, $listStatus) = MG_exec($listCmd);
    if ($listStatus != 0 || empty($entries) || count($entries) > 1000) {
        COM_errorLog('MediaGallery: rejected ZIP archive because its member list is invalid or too large.', 1);
        return $LANG_MG02['generic_error'];
    }

    foreach ($entries as $entry) {
        if (!MG_isSafeZipEntryName($entry)) {
            COM_errorLog('MediaGallery: rejected unsafe ZIP member: ' . $entry, 1);
            return $LANG_MG02['generic_error'];
        }
    }

    if (!is_dir($tmpBase) || !is_writable($tmpBase)) {
        return $LANG_MG02['error_create_tmp'];
    }

    $extractDir = $tmpBase . $tmpLeaf;
    if (file_exists($extractDir) || !@mkdir($extractDir, 0700)) {
        return $LANG_MG02['error_create_tmp'];
    }

    $extractCmd = escapeshellarg($zipBinary)
                . ' -qq -o ' . escapeshellarg($filename)
                . ' -d ' . escapeshellarg($extractDir);
    $rc = MG_execWrapper($extractCmd);
    if (!$rc || !MG_validateExtractedZipTree($extractDir)) {
        COM_errorLog('MediaGallery: ZIP extraction failed validation; extracted data was discarded.', 1);
        MG_deleteDir($extractDir);
        return $LANG_MG02['generic_error'];
    }

    $status = MG_processDir($extractDir, $album_id, $purgefiles, 1);
    MG_deleteDir($extractDir);
    return $status;
}
'''

text = text[:start] + new + text[end:]

old = """function MG_processDir($dir, $album_id, $purgefiles, $recurse)
{
    global $_TABLES, $LANG_MG02;

    if (!@is_dir($dir)) {"""
new = """function MG_processDir($dir, $album_id, $purgefiles, $recurse)
{
    global $_TABLES, $LANG_MG02;

    $statusMsg = '';

    if (!@is_dir($dir) || is_link($dir)) {"""
if text.count(old) != 1:
    raise SystemExit('MG_processDir start not found exactly once')
text = text.replace(old, new)

old = """        if (is_dir($filetmp)) {
            if ($recurse) {
                $statusMsg .= MG_processDir($filetmp, $album_id, $purgefiles, $recurse);
            }
        } else {"""
new = """        if (is_link($filetmp)) {
            COM_errorLog('MediaGallery: skipped symbolic link while importing directory: ' . $filetmp, 1);
            continue;
        }
        if (is_dir($filetmp)) {
            if ($recurse) {
                $statusMsg .= MG_processDir($filetmp, $album_id, $purgefiles, $recurse);
            }
        } else {"""
if text.count(old) != 1:
    raise SystemExit('MG_processDir loop not found exactly once')
text = text.replace(old, new)

old = """           if ($obj != '.' && $obj != '..') {
               if (is_dir($dir.$obj)) {
                   if (!MG_deleteDir($dir.$obj))
                       return false;
               } elseif (is_file($dir.$obj)) {
                   if (!unlink($dir.$obj))
                       return false;
               }
           }"""
new = """           if ($obj != '.' && $obj != '..') {
               $path = $dir . $obj;
               if (is_link($path)) {
                   if (!@unlink($path))
                       return false;
               } elseif (is_dir($path)) {
                   if (!MG_deleteDir($path))
                       return false;
               } elseif (is_file($path)) {
                   if (!@unlink($path))
                       return false;
               }
           }"""
if text.count(old) != 1:
    raise SystemExit('MG_deleteDir block not found exactly once')
text = text.replace(old, new)

path.write_text(text)
