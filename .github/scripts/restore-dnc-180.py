from pathlib import Path

p = Path('include/lib-upload.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')

old_forced = """    $successfulWatermark        = 0;\n    $dnc                        = 1; // What is this?\n    $errors                     = 0;\n"""
new_forced = """    $successfulWatermark        = 0;\n    $dnc                        = ((int) $dnc === 1) ? 1 : 0;\n    $errors                     = 0;\n"""
if text.count(old_forced) != 1:
    raise SystemExit('forced DNC assignment not found exactly once')
text = text.replace(old_forced, new_forced, 1)

old_block = """                    if ($dnc != 1) {\n                        if (!in_array($mimeType, $_SPECIAL_IMAGES_MIMETYPE)) {\n                            $mimeExt = 'jpg';\n                            $mimeType = 'image/jpeg';\n                        }\n                    }\n"""
new_block = """                    if ($dnc != 1 && $_MG_CONF['discard_original'] != 1\n                        && !in_array($mimeType, $_SPECIAL_IMAGES_MIMETYPE)) {\n                        $jpegOriginal = MG_getFilePath('orig', $media_filename, 'jpg');\n                        list($convertRc, $convertMsg) = MG_convertImageFormat(\n                            $media_orig,\n                            $jpegOriginal,\n                            'image/jpeg',\n                            0\n                        );\n\n                        if ($convertRc == false) {\n                            @unlink($jpegOriginal);\n                            $errors++;\n                            $errMsg .= $convertMsg;\n                        } else {\n                            @chmod($jpegOriginal, 0644);\n                            if ($jpegOriginal != $media_orig) {\n                                @unlink($media_orig);\n                            }\n                            $media_orig = $jpegOriginal;\n                            $mimeExt = 'jpg';\n                            $mimeType = 'image/jpeg';\n                        }\n                    }\n"""
if text.count(old_block) != 1:
    raise SystemExit('legacy DNC metadata-only block not found exactly once')
text = text.replace(old_block, new_block, 1)

p.write_text(text, encoding='utf-8', errors='surrogateescape')
