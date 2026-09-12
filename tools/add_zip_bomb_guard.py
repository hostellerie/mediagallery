from pathlib import Path

p = Path('include/lib-upload.php')
text = p.read_text()

old = """    foreach ($entries as $entry) {
        if (!MG_isSafeZipEntryName($entry)) {
            COM_errorLog('MediaGallery: rejected unsafe ZIP member: ' . $entry, 1);
            return $LANG_MG02['generic_error'];
        }
    }

    if (!is_dir($tmpBase) || !is_writable($tmpBase)) {"""

new = """    foreach ($entries as $entry) {
        if (!MG_isSafeZipEntryName($entry)) {
            COM_errorLog('MediaGallery: rejected unsafe ZIP member: ' . $entry, 1);
            return $LANG_MG02['generic_error'];
        }
    }

    // Bound declared uncompressed content before extraction to reduce ZIP-bomb
    // risk. Info-ZIP's listing contains numeric length rows and a final total;
    // taking the largest first-column value is therefore a conservative total.
    $sizeCmd = escapeshellarg($zipBinary) . ' -l ' . escapeshellarg($filename);
    list($sizeLines, $sizeStatus) = MG_exec($sizeCmd);
    $declaredUncompressed = 0;
    if ($sizeStatus != 0) {
        COM_errorLog('MediaGallery: unable to inspect ZIP uncompressed size.', 1);
        return $LANG_MG02['generic_error'];
    }
    foreach ($sizeLines as $line) {
        if (preg_match('/^\\s*(\\d+)\\s+/', $line, $match)) {
            $declaredUncompressed = max($declaredUncompressed, (float) $match[1]);
        }
    }
    if ($declaredUncompressed <= 0 || $declaredUncompressed > 1073741824) {
        COM_errorLog('MediaGallery: rejected ZIP archive with invalid or excessive uncompressed size.', 1);
        return $LANG_MG02['generic_error'];
    }

    if (!is_dir($tmpBase) || !is_writable($tmpBase)) {"""

if text.count(old) != 1:
    raise SystemExit('ZIP member validation block not found exactly once')

p.write_text(text.replace(old, new))
