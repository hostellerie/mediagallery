from pathlib import Path

p = Path('include/lib-upload.php')
text = p.read_text(encoding='utf-8')

old = """        if ($rc == false) {
            COM_errorLog(\"MG_createThumbnail: Error resizing uploaded image to thumbnail size.\");
            @unlink($srcImage);
            return array(false, $msg);
        }
    }

    return array(true, '');
}
"""
new = """        if ($rc == false) {
            COM_errorLog(\"MG_createThumbnail: Error resizing uploaded image to thumbnail size.\");
            @unlink($srcImage);
            if ($tmpImage != '') {
                @unlink($tmpImage);
            }
            return array(false, $msg);
        }
    }

    if ($tmpImage != '') {
        @unlink($tmpImage);
    }

    return array(true, '');
}
"""
if old not in text:
    raise SystemExit('thumbnail cleanup anchor not found')
text = text.replace(old, new, 1)

old = """    if (!($album->valid_formats & $format_type)) {
        return array(false, $LANG_MG02['format_not_allowed']);
    }
"""
new = """    if (!($album->valid_formats & $format_type)) {
        @unlink($tmpPath);
        return array(false, $LANG_MG02['format_not_allowed']);
    }
"""
if old not in text:
    raise SystemExit('format rejection cleanup anchor not found')
text = text.replace(old, new, 1)

p.write_text(text, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
needle = "- MIME/extension consistency for ambiguous generic files;\n- temporary-file naming and cleanup on interrupted processing;"
replacement = "- MIME/extension consistency for ambiguous generic files;\n- deterministic upload failure paths now remove the main `tmpPath`, and special-image thumbnail conversion removes its `wip*.jpg` file on success/failure;\n- still define a stale-temp policy for genuinely interrupted/killed PHP requests;"
if needle not in notes:
    raise SystemExit('implementation notes cleanup anchor not found')
notes = notes.replace(needle, replacement, 1)
p.write_text(notes, encoding='utf-8')

p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
needle = "- [ ] Review temporary-file cleanup after interrupted processing."
replacement = "- [x] Clean deterministic upload-failure and special-image `wip` temporary files.\n- [ ] Define safe stale-temp cleanup for genuinely interrupted/killed requests."
if needle not in roadmap:
    raise SystemExit('roadmap cleanup anchor not found')
roadmap = roadmap.replace(needle, replacement, 1)
p.write_text(roadmap, encoding='utf-8')

print('Temporary-file cleanup patch prepared.')
