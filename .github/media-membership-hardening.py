from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(label + ' anchor not found')
    return text.replace(old, new, 1)

# ------------------------------------------------------------------
# include/batch.php
# ------------------------------------------------------------------
p = Path('include/batch.php')
text = p.read_text(encoding='utf-8')

# Batch process: only register media actually linked to the authorized album.
old = """            for ($i=0; $i < $numItems; $i++) {\n                $media_id = COM_applyFilter($media_id_array[$i]);\n                MG_registerSession(array(\n                    'session_id' => $session_id,\n                    'mid'        => $media_id,\n                    'aid'        => $album_id,\n                    'data'       => $direction\n                ));\n            }"""
new = """            for ($i=0; $i < $numItems; $i++) {\n                $media_id = COM_applyFilter($media_id_array[$i]);\n                if (DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n                    COM_errorLog('MediaGallery: ignored batch rotate media ' . $media_id . ' because it is not in album ' . intval($album_id), 1);\n                    continue;\n                }\n                MG_registerSession(array(\n                    'session_id' => $session_id,\n                    'mid'        => $media_id,\n                    'aid'        => $album_id,\n                    'data'       => $direction\n                ));\n            }"""
text = replace_once(text, old, new, 'batch rotate membership')

old = """            for ($i=0; $i < $numItems; $i++) {\n                $media_id = COM_applyFilter($media_id_array[$i]);\n                MG_registerSession(array(\n                    'session_id' => $session_id,\n                    'mid'        => $media_id,\n                    'aid'        => $album_id\n                ));\n            }"""
new = """            for ($i=0; $i < $numItems; $i++) {\n                $media_id = COM_applyFilter($media_id_array[$i]);\n                if (DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n                    COM_errorLog('MediaGallery: ignored batch watermark media ' . $media_id . ' because it is not in album ' . intval($album_id), 1);\n                    continue;\n                }\n                MG_registerSession(array(\n                    'session_id' => $session_id,\n                    'mid'        => $media_id,\n                    'aid'        => $album_id\n                ));\n            }"""
text = replace_once(text, old, new, 'batch watermark membership')

old = """    $numItems = count($media_id_array);\n    for ($i=0; $i < $numItems; $i++) {\n        MG_deleteMedia($media_id_array[$i]);\n        $mediaCount--;\n    }"""
new = """    $numItems = count($media_id_array);\n    for ($i=0; $i < $numItems; $i++) {\n        $media_id = COM_applyFilter($media_id_array[$i]);\n        if (DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n            COM_errorLog('MediaGallery: refused deletion of media ' . $media_id . ' because it is not in album ' . intval($album_id), 1);\n            continue;\n        }\n        MG_deleteMedia($media_id);\n        $mediaCount--;\n    }"""
text = replace_once(text, old, new, 'batch delete membership')

old = """    for ($i=0; $i < $numItems; $i++) {\n        $media_id = $media_id_array[$i];\n        $sql = \"UPDATE {$_TABLES['mg_media_albums']} \"\n             . \"SET album_id=\" . intval($destination) . \", media_order=\" . intval($media_seq)\n             . \" WHERE album_id=\" . intval($album_id) . \" AND media_id='\" . DB_escapeString($media_id) . \"'\";\n        DB_query($sql);\n        $media_seq += 10;\n\n        // update the media count in both albums...\n        $aMediaCount--;\n        $dMediaCount++;\n    }"""
new = """    for ($i=0; $i < $numItems; $i++) {\n        $media_id = COM_applyFilter($media_id_array[$i]);\n        if (DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n            COM_errorLog('MediaGallery: refused move of media ' . $media_id . ' because it is not in source album ' . intval($album_id), 1);\n            continue;\n        }\n        $sql = \"UPDATE {$_TABLES['mg_media_albums']} \"\n             . \"SET album_id=\" . intval($destination) . \", media_order=\" . intval($media_seq)\n             . \" WHERE album_id=\" . intval($album_id) . \" AND media_id='\" . DB_escapeString($media_id) . \"'\";\n        DB_query($sql);\n        $media_seq += 10;\n\n        // update the media count in both albums...\n        $aMediaCount--;\n        $dMediaCount++;\n    }"""
text = replace_once(text, old, new, 'batch move membership')
p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# include/mediamanage.php -- legacy bytes preserved 1:1
# ------------------------------------------------------------------
p = Path('include/mediamanage.php')
text = p.read_bytes().decode('latin-1')

# Manage-media save: never update metadata for an id not linked to this album.
old = """    for ($i=0; $i < $numItems; $i++) {\n        $media_title_safe = substr($media[$i]['title'], 0, 254);"""
new = """    for ($i=0; $i < $numItems; $i++) {\n        $media_id = COM_applyFilter($media[$i]['mid']);\n        if (DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n            COM_errorLog('MediaGallery: ignored media-manager update for media ' . $media_id . ' because it is not in album ' . intval($album_id), 1);\n            continue;\n        }\n        $media[$i]['mid'] = $media_id;\n        $media_title_safe = substr($media[$i]['title'], 0, 254);"""
text = replace_once(text, old, new, 'media manager membership')

# Cover id must also belong to the current album.
old = """    if ($cover != -1) {\n\n        $sql = \"SELECT media_type,media_tn_attached,media_filename \"\n             . \"FROM {$_TABLES['mg_media']} WHERE media_id='\" . DB_escapeString($cover) . \"'\";"""
new = """    if ($cover != -1) {\n\n        if ($cover > 0 && DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $cover)) < 1) {\n            COM_errorLog('MediaGallery: ignored album cover media ' . intval($cover) . ' because it is not in album ' . intval($album_id), 1);\n            $cover = -1;\n        }\n\n        $sql = \"SELECT media_type,media_tn_attached,media_filename \"\n             . \"FROM {$_TABLES['mg_media']} WHERE media_id='\" . DB_escapeString($cover) . \"'\";"""
text = replace_once(text, old, new, 'cover membership')

# Editor display: normal media must be linked to the requested album. Moderation queue remains separate.
old = """    $result = DB_query($sql);\n    $row = DB_fetchArray($result);\n\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && $row['media_user_id'] != $_USER['uid']) {"""
new = """    $result = DB_query($sql);\n    $row = DB_fetchArray($result);\n\n    if (!$mqueue && DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n        COM_errorLog('MediaGallery: media edit rejected because media ' . DB_escapeString($media_id) . ' is not in album ' . intval($album_id), 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && $row['media_user_id'] != $_USER['uid']) {"""
text = replace_once(text, old, new, 'media editor display membership')

# Reset rating/view normal media association.
old = """    $owner_id = DB_getItem($table, 'media_user_id', \"media_id='\" . DB_escapeString($media_id) . \"'\");\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && intval($owner_id) != intval($_USER['uid'])) {"""
new = """    $owner_id = DB_getItem($table, 'media_user_id', \"media_id='\" . DB_escapeString($media_id) . \"'\");\n    if (!$mqueue && DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && intval($owner_id) != intval($_USER['uid'])) {"""
text = replace_once(text, old, new, 'rating reset membership')
# Same source block occurs in views reset after first replacement.
text = replace_once(text, old, new, 'view reset membership')

# Save edit: normal media association before any upload/replacement.
old = """    $owner_id = DB_getItem($table, 'media_user_id', \"media_id='\" . DB_escapeString($media_id) . \"'\");\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && intval($owner_id) != intval($_USER['uid'])) {\n        COM_errorLog('MediaGallery: media edit save rejected because of insufficient access.', 1);"""
new = """    $owner_id = DB_getItem($table, 'media_user_id', \"media_id='\" . DB_escapeString($media_id) . \"'\");\n    if (!$queue && DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array(intval($album_id), $media_id)) < 1) {\n        COM_errorLog('MediaGallery: media edit save rejected because media ' . DB_escapeString($media_id) . ' is not in album ' . intval($album_id), 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && intval($owner_id) != intval($_USER['uid'])) {\n        COM_errorLog('MediaGallery: media edit save rejected because of insufficient access.', 1);"""
text = replace_once(text, old, new, 'media edit save membership')

p.write_bytes(text.encode('latin-1'))

# ------------------------------------------------------------------
# Documentation
# ------------------------------------------------------------------
p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
needle = '- [x] Revalidate media edit/reset mutations server-side and correct reset handlers to read their posted album id.\n'
addition = needle + '- [x] Bind posted media IDs to the authorized album before manager edits, batch delete/move/rotate/watermark, cover selection and normal media editing.\n'
if needle not in roadmap:
    raise SystemExit('roadmap anchor not found')
roadmap = roadmap.replace(needle, addition, 1)
p.write_text(roadmap, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
needle = '- direct rotation now uses POST and verifies both album write access and the requested album/media association before touching files;\n'
addition = needle + '- posted media IDs are now checked against `mg_media_albums` before manager edits, batch delete/move/rotate/watermark, cover selection and normal media editing;\n'
if needle not in notes:
    raise SystemExit('implementation notes anchor not found')
notes = notes.replace(needle, addition, 1)
p.write_text(notes, encoding='utf-8')

print('Media membership hardening prepared.')
