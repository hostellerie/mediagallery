from pathlib import Path

p = Path('include/lib-upload.php')
text = p.read_text(encoding='utf-8')

old = """    $mimeInfo = MG_getMediaMetaData($filename);\n    $mimeExt = strtolower(substr(strrchr($file, '.'), 1));\n    $mimeInfo['type'] = $mimeExt;\n\n    // override the determination for some filetypes\n    $filetype = MG_getFileTypeFromExt($mimeExt, $filetype);\n\n    if (empty($mimeInfo['mime_type'])) {\n        COM_errorLog(\"MG Upload: getID3 was unable to detect mime type - using PHP detection\");\n        $mimeInfo['mime_type'] = $filetype;\n    }\n"""
new = """    $mimeInfo = MG_getMediaMetaData($filename);\n    $mimeExt = strtolower(substr(strrchr($file, '.'), 1));\n    $mimeInfo['type'] = $mimeExt;\n\n    // Prefer content-derived MIME information. If getID3 cannot identify the\n    // file, use PHP fileinfo before falling back to browser/import metadata.\n    $localMime = MG_detectLocalMime180($filename);\n    $detectedMime = isset($mimeInfo['mime_type']) ? strtolower(trim($mimeInfo['mime_type'])) : '';\n    if (($detectedMime === '' || $detectedMime === 'application/octet-stream')\n        && $localMime !== '' && $localMime !== 'application/octet-stream') {\n        $mimeInfo['mime_type'] = $localMime;\n        $detectedMime = $localMime;\n        if ($_MG_CONF['verbose']) {\n            COM_errorLog('MG Upload: fileinfo detected mime type: ' . $localMime);\n        }\n    }\n\n    // override the determination for some filetypes\n    $filetype = MG_getFileTypeFromExt($mimeExt, $filetype);\n\n    if (empty($mimeInfo['mime_type'])) {\n        COM_errorLog(\"MG Upload: content MIME detection was inconclusive - using upload/import metadata\");\n        $mimeInfo['mime_type'] = $filetype;\n    }\n"""
if old not in text:
    raise SystemExit('MIME detection anchor not found')
text = text.replace(old, new, 1)

anchor = """    switch ($mimeInfo['mime_type']) {\n        case 'audio/mpeg' :\n"""
insert = """    if (!MG_validateMimeExtension180($file, $mimeInfo['mime_type'])) {\n        COM_errorLog(\n            'MediaGallery 1.8: rejected MIME/extension mismatch for ' . basename($file)\n            . ' (detected ' . $mimeInfo['mime_type'] . ', extension .' . $mimeExt . ')',\n            1\n        );\n        @unlink($tmpPath);\n        return array(false, $LANG_MG02['format_not_allowed']);\n    }\n\n""" + anchor
if anchor not in text:
    raise SystemExit('format switch anchor not found')
text = text.replace(anchor, insert, 1)

p.write_text(text, encoding='utf-8')

p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
roadmap = roadmap.replace(
    '- [ ] Review MIME/extension consistency for ambiguous generic files.',
    '- [x] Prefer content-derived MIME (`getID3`, then `fileinfo`) and validate MIME/extension coherence for explicitly handled formats while leaving unknown extensions generic.\n- [ ] Live-test MIME mismatch rejection and generic-file compatibility on Geeklog 2.1.1 and 2.2.2.'
)
p.write_text(roadmap, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
needle = '- MIME/extension consistency for ambiguous generic files;'
replacement = '- MIME/extension consistency now prefers getID3, falls back to local PHP fileinfo when getID3 is inconclusive, and rejects known-extension mismatches while preserving generic unknown-extension files;\n- live regression tests remain for mismatch rejection and generic-file compatibility;'
if needle in notes:
    notes = notes.replace(needle, replacement, 1)
else:
    marker = 'Still review before RC:\n\n'
    if marker not in notes:
        raise SystemExit('Implementation notes anchor not found')
    notes = notes.replace(marker, marker + replacement + '\n', 1)
p.write_text(notes, encoding='utf-8')

print('MIME consistency patch prepared.')
