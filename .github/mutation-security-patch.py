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

old = """function MG_batchProcess($album_id, $media_id_array, $action, $actionURL = '')\n{\n    global $_CONF, $_TABLES, $_MG_CONF, $LANG_MG01;\n\n    $numItems = count($media_id_array);\n\n    $album_data = MG_getAlbumData($album_id, array('album_title', 'wm_id'), false);\n\n    switch ($action) {"""
new = """function MG_batchProcess($album_id, $media_id_array, $action, $actionURL = '')\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01;\n\n    $album_data = MG_getAlbumData($album_id, array('album_title', 'wm_id'), true);\n    if (!isset($album_data['access']) || ($album_data['access'] != 3 && !SEC_hasRights('mediagallery.admin'))) {\n        COM_errorLog('MediaGallery: batch mutation rejected because the user has no write access to album ' . intval($album_id), 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: batch mutation rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $numItems = count($media_id_array);\n\n    switch ($action) {"""
text = replace_once(text, old, new, 'batch process guard')

for marker in ("'action'        => 'doresize',", "'action'        => 'dorebuild',"):
    old = marker + "\n        's_form_action' => $actionURL,"
    new = marker + "\n        's_form_action' => $actionURL,\n        'gltoken_name'  => CSRF_TOKEN,\n        'gltoken'       => SEC_createToken(),"
    text = replace_once(text, old, new, marker)

old = """    if ($album_data['access'] != 3) {\n        COM_redirect($actionURL);\n    }\n\n    if ($_MG_CONF['discard_original'] == 1) {"""
new = """    if ($album_data['access'] != 3) {\n        COM_redirect($actionURL);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: album resize rejected because of an invalid CSRF token.', 1);\n        COM_redirect($actionURL);\n    }\n\n    if ($_MG_CONF['discard_original'] == 1) {"""
text = replace_once(text, old, new, 'resize token guard')

old = """function MG_albumRebuildThumbs($aid, $actionURL)\n{\n    global $_CONF, $_TABLES, $_MG_CONF, $LANG_MG01;\n\n    $album_data = MG_getAlbumData($aid, array('album_title'), true);\n\n    if ($album_data['access'] != 3) {\n        COM_redirect($actionURL);\n    }\n\n    require_once"""
new = """function MG_albumRebuildThumbs($aid, $actionURL)\n{\n    global $_CONF, $_TABLES, $_MG_CONF, $LANG_MG01;\n\n    $album_data = MG_getAlbumData($aid, array('album_title'), true);\n\n    if ($album_data['access'] != 3) {\n        COM_redirect($actionURL);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: thumbnail rebuild rejected because of an invalid CSRF token.', 1);\n        COM_redirect($actionURL);\n    }\n\n    require_once"""
text = replace_once(text, old, new, 'rebuild token guard')

old = """    if ($access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally delete items from album in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    $mediaCount"""
new = """    if ($access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally delete items from album in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: media deletion rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    $mediaCount"""
text = replace_once(text, old, new, 'batch delete token')

old = """    if ($access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally delete items from album in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    // make sure they are not the same..."""
new = """    if ($access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally delete items from album in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: media move rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    // make sure they are not the same..."""
text = replace_once(text, old, new, 'batch move token')

old = """        'lang_album_delete_help' => $LANG_MG01['album_delete_help']\n    ));"""
new = """        'lang_album_delete_help' => $LANG_MG01['album_delete_help'],\n        'gltoken_name'          => CSRF_TOKEN,\n        'gltoken'               => SEC_createToken()\n    ));"""
text = replace_once(text, old, new, 'delete album form token')

old = """    if ($album->access != 3) {\n        COM_errorLog(\"MediaGallery: Someone has tried to illegally delete an album in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    if ($target_id == 0) {"""
new = """    if ($album->access != 3) {\n        COM_errorLog(\"MediaGallery: Someone has tried to illegally delete an album in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: album deletion rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    if ($target_id == 0) {"""
text = replace_once(text, old, new, 'delete album save token')

p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# templates/confirm.thtml + mediamanage.thtml + mediaedit + deletealbum
# ------------------------------------------------------------------
p = Path('templates/confirm.thtml')
t = p.read_text(encoding='utf-8')
anchor = '<input type="hidden" name="action" value="{action}"{xhtml}>\n'
t = replace_once(t, anchor, anchor + '<input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n', 'confirm token')
p.write_text(t, encoding='utf-8')

p = Path('templates/mediamanage.thtml')
t = p.read_text(encoding='utf-8')
anchor = '    <input type="hidden" name="action" value="media"{xhtml}>\n'
t = replace_once(t, anchor, anchor + '    <input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n', 'mediamanage token')
p.write_text(t, encoding='utf-8')

p = Path('templates/mediaedit.thtml')
t = p.read_text(encoding='utf-8')
anchor1 = '    <input type="hidden" value="{queue}" name="queue"{xhtml}>\n  </div>\n</form>'
new1 = '    <input type="hidden" value="{queue}" name="queue"{xhtml}>\n    <input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n  </div>\n</form>'
t = replace_once(t, anchor1, new1, 'mediaedit reset form token')
anchor2 = '      <input type="hidden" name="action" value="savemedia"{xhtml}>\n'
t = replace_once(t, anchor2, anchor2 + '      <input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n', 'mediaedit main form token')
p.write_text(t, encoding='utf-8')

p = Path('templates/deletealbum.thtml')
t = p.read_text(encoding='utf-8')
anchor = '<input type="hidden" name="action" value="confalbum">\n'
t = replace_once(t, anchor, anchor + '<input type="hidden" name="{gltoken_name}" value="{gltoken}">\n', 'delete album token')
p.write_text(t, encoding='utf-8')

# ------------------------------------------------------------------
# include/mediamanage.php
# ------------------------------------------------------------------
p = Path('include/mediamanage.php')
text = p.read_text(encoding='utf-8')

# Media manager form token.
old = """        'val_reset_cover'        => (($album_cover == '-1') ? ' checked=\"checked\"' : ''),\n    ));"""
new = """        'val_reset_cover'        => (($album_cover == '-1') ? ' checked=\"checked\"' : ''),\n        'gltoken_name'           => CSRF_TOKEN,\n        'gltoken'                => SEC_createToken(),\n    ));"""
text = replace_once(text, old, new, 'media manager form token vars')

# Manager save token check.
old = """    if ($access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally manage (save) Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $numItems"""
new = """    if ($access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally manage (save) Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: media manager save rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $numItems"""
text = replace_once(text, old, new, 'media manager save token guard')

# Replace direct GET rotate links by compact POST forms with CSRF token.
old = """    $rotate_right = '';\n    $rotate_left  = '';\n    if ($row['media_type'] == 0 && ($_CONF['image_lib'] != 'gdlib' || function_exists(\"imagerotate\"))) {\n        $rotate_right = '<a href=\"' . $_MG_CONF['site_url']\n                      . '/admin.php?mode=rotate&amp;action=right&amp;media_id='\n                      . $row['media_id'] . '&amp;album_id=' . $album_id . '\">'\n                      . '<img src=\"' . $_MG_CONF['site_url'] . '/images/rotate_right_icon.gif\" alt=\"'\n                      . $LANG_MG01['rotate_left']  . '\" style=\"border:none;\"' . XHTML . '></a>';\n        $rotate_left  = '<a href=\"' . $_MG_CONF['site_url']\n                      . '/admin.php?mode=rotate&amp;action=left&amp;media_id='\n                      . $row['media_id'] . '&amp;album_id=' . $album_id . '\">'\n                      . '<img src=\"' . $_MG_CONF['site_url'] . '/images/rotate_left_icon.gif\" alt=\"'\n                      . $LANG_MG01['rotate_right'] . '\" style=\"border:none;\"' . XHTML . '></a>';\n    }"""
new = """    $rotate_right = '';\n    $rotate_left  = '';\n    if ($row['media_type'] == 0 && ($_CONF['image_lib'] != 'gdlib' || function_exists(\"imagerotate\"))) {\n        $rotation_token = SEC_createToken();\n        $rotation_common = '<input type=\"hidden\" name=\"mode\" value=\"rotate\"' . XHTML . '>'\n                         . '<input type=\"hidden\" name=\"media_id\" value=\"' . intval($row['media_id']) . '\"' . XHTML . '>'\n                         . '<input type=\"hidden\" name=\"album_id\" value=\"' . intval($album_id) . '\"' . XHTML . '>'\n                         . '<input type=\"hidden\" name=\"' . CSRF_TOKEN . '\" value=\"' . $rotation_token . '\"' . XHTML . '>';\n        $rotate_right = '<form method=\"post\" action=\"' . $_MG_CONF['site_url'] . '/admin.php\" style=\"display:inline\">'\n                      . $rotation_common\n                      . '<input type=\"hidden\" name=\"action\" value=\"right\"' . XHTML . '>'\n                      . '<button type=\"submit\" style=\"border:0;background:transparent;padding:0;cursor:pointer\">'\n                      . '<img src=\"' . $_MG_CONF['site_url'] . '/images/rotate_right_icon.gif\" alt=\"'\n                      . $LANG_MG01['rotate_right'] . '\" style=\"border:none;\"' . XHTML . '></button></form>';\n        $rotate_left  = '<form method=\"post\" action=\"' . $_MG_CONF['site_url'] . '/admin.php\" style=\"display:inline\">'\n                      . $rotation_common\n                      . '<input type=\"hidden\" name=\"action\" value=\"left\"' . XHTML . '>'\n                      . '<button type=\"submit\" style=\"border:0;background:transparent;padding:0;cursor:pointer\">'\n                      . '<img src=\"' . $_MG_CONF['site_url'] . '/images/rotate_left_icon.gif\" alt=\"'\n                      . $LANG_MG01['rotate_left'] . '\" style=\"border:none;\"' . XHTML . '></button></form>';\n    }"""
text = replace_once(text, old, new, 'rotate post forms')

# Media edit template token vars.
old = """        'genre'              => $row['genre'],\n    ));"""
new = """        'genre'              => $row['genre'],\n        'gltoken_name'       => CSRF_TOKEN,\n        'gltoken'            => SEC_createToken(),\n    ));"""
text = replace_once(text, old, new, 'media edit token vars')

# Reset functions: server-side permission and token validation.
old = """function MG_mediaResetRating($album_id, $media_id, $mqueue)\n{\n    global $_MG_CONF, $_TABLES;\n\n    DB_change"""
new = """function MG_mediaResetRating($album_id, $media_id, $mqueue)\n{\n    global $_USER, $_MG_CONF, $_TABLES, $LANG_MG00;\n\n    $album = new mgAlbum($album_id);\n    $table = $mqueue ? $_TABLES['mg_mediaqueue'] : $_TABLES['mg_media'];\n    $owner_id = DB_getItem($table, 'media_user_id', \"media_id='\" . DB_escapeString($media_id) . \"'\");\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && intval($owner_id) != intval($_USER['uid'])) {\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: rating reset rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    DB_change"""
text = replace_once(text, old, new, 'rating reset security')

old = """function MG_mediaResetViews($album_id, $media_id, $mqueue)\n{\n    global $_MG_CONF, $_TABLES;\n\n    DB_change"""
new = """function MG_mediaResetViews($album_id, $media_id, $mqueue)\n{\n    global $_USER, $_MG_CONF, $_TABLES, $LANG_MG00;\n\n    $album = new mgAlbum($album_id);\n    $table = $mqueue ? $_TABLES['mg_mediaqueue'] : $_TABLES['mg_media'];\n    $owner_id = DB_getItem($table, 'media_user_id', \"media_id='\" . DB_escapeString($media_id) . \"'\");\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && intval($owner_id) != intval($_USER['uid'])) {\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: view reset rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    DB_change"""
text = replace_once(text, old, new, 'view reset security')

# Save media edit: revalidate same policy as editor before any file replacement/mutation.
old = """function MG_saveMediaEdit($album_id, $media_id, $actionURL)\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG03;\n\n    $back"""
new = """function MG_saveMediaEdit($album_id, $media_id, $actionURL)\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG03;\n\n    $queue = isset($_POST['queue']) ? COM_applyFilter($_POST['queue'], true) : 0;\n    $table = $queue ? $_TABLES['mg_mediaqueue'] : $_TABLES['mg_media'];\n    $album = new mgAlbum($album_id);\n    $owner_id = DB_getItem($table, 'media_user_id', \"media_id='\" . DB_escapeString($media_id) . \"'\");\n    if ($album->access != 3 && !SEC_inGroup($album->mod_group_id) && intval($owner_id) != intval($_USER['uid'])) {\n        COM_errorLog('MediaGallery: media edit save rejected because of insufficient access.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: media edit save rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $back"""
text = replace_once(text, old, new, 'media edit save security')
# Remove the now duplicate queue assignment later in the function.
text = replace_once(text, """    $queue = COM_applyFilter($_POST['queue'], true);\n\n    $replacefile""", """    $replacefile""", 'duplicate queue assignment')

p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# public_html/admin.php
# ------------------------------------------------------------------
p = Path('public_html/admin.php')
text = p.read_text(encoding='utf-8')

text = replace_once(text,
"""    $album_id = (int) Input::fGet('album_id', 0);\n    $mid      = Input::fPost('mid', '');\n    $mqueue   = Input::fPost('queue');\n    $display = MG_mediaResetRating""",
"""    $album_id = (int) Input::fPost('album_id', 0);\n    $mid      = Input::fPost('mid', '');\n    $mqueue   = Input::fPost('queue');\n    $display = MG_mediaResetRating""",
'rating reset POST album')
text = replace_once(text,
"""    $album_id = (int) Input::fGet('album_id', 0);\n    $mid      = Input::fPost('mid', '');\n    $mqueue   = Input::fPost('queue');\n    $display = MG_mediaResetViews""",
"""    $album_id = (int) Input::fPost('album_id', 0);\n    $mid      = Input::fPost('mid', '');\n    $mqueue   = Input::fPost('queue');\n    $display = MG_mediaResetViews""",
'views reset POST album')

old = """} elseif ($mode === 'rotate') {\n    $album_id = (int) Input::fGet('album_id', -1);\n    $media_id = (int) Input::fGet('media_id', -1);\n    $direction = Input::fGet('action');\n\n    if (($album_id < 0) || ($media_id < 0) ||\n            empty($direction) || (($direction !== 'left') && ($direction !== 'right'))) {\n        MG_invalidRequest();\n    }\n\n    require_once $include . 'lib-media.php';\n    $actionURL = $_MG_CONF['site_url'] . '/admin.php?mode=mediaedit&mid=' . $media_id . '&album_id=' . $album_id;\n    $display = MG_rotateMedia($album_id, $media_id, $direction, $actionURL);"""
new = """} elseif ($mode === 'rotate') {\n    $album_id = (int) Input::fPost('album_id', -1);\n    $media_id = (int) Input::fPost('media_id', -1);\n    $direction = Input::fPost('action');\n\n    if (($album_id < 0) || ($media_id < 0) ||\n            empty($direction) || (($direction !== 'left') && ($direction !== 'right')) ||\n            !SEC_checkToken()) {\n        MG_invalidRequest();\n    }\n\n    require_once $include . 'lib-media.php';\n    $actionURL = $_MG_CONF['site_url'] . '/admin.php?mode=mediaedit&mid=' . $media_id . '&album_id=' . $album_id;\n    $display = MG_rotateMedia($album_id, $media_id, $direction, $actionURL);"""
text = replace_once(text, old, new, 'rotate route POST/token')
p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# include/lib-media.php: validate write access and album/media binding
# ------------------------------------------------------------------
p = Path('include/lib-media.php')
text = p.read_text(encoding='utf-8')
old = """function MG_rotateMedia($album_id, $media_id, $direction, $actionURL = '')\n{\n    global $_TABLES, $_MG_CONF;\n\n    $album_id = (int) $album_id;\n    $media_id = (int) $media_id;\n    $sql = \"SELECT media_filename, media_mime_ext FROM {$_TABLES['mg_media']} \"\n         . \"WHERE media_id = \" . $media_id;\n    $result = DB_query($sql);\n    list($filename, $mime_ext) = DB_fetchArray($result);"""
new = """function MG_rotateMedia($album_id, $media_id, $direction, $actionURL = '')\n{\n    global $_TABLES, $_MG_CONF;\n\n    $album_id = (int) $album_id;\n    $media_id = (int) $media_id;\n\n    $album = new mgAlbum($album_id);\n    if (!isset($album->id) || !$album->valid || ($album->access != 3 && !SEC_hasRights('mediagallery.admin'))) {\n        COM_errorLog('MediaGallery: rotate rejected because the user has no write access to album ' . $album_id, 1);\n        if ($actionURL == -1 || $actionURL == '') {\n            return false;\n        }\n        COM_redirect($_MG_CONF['site_url'] . '/index.php');\n    }\n\n    $linkCount = DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array($album_id, $media_id));\n    if ($linkCount < 1) {\n        COM_errorLog('MediaGallery: rotate rejected because media ' . $media_id . ' is not in album ' . $album_id, 1);\n        if ($actionURL == -1 || $actionURL == '') {\n            return false;\n        }\n        COM_redirect($_MG_CONF['site_url'] . '/album.php?aid=' . $album_id);\n    }\n\n    $sql = \"SELECT media_filename, media_mime_ext, media_type FROM {$_TABLES['mg_media']} \"\n         . \"WHERE media_id = \" . $media_id;\n    $result = DB_query($sql);\n    list($filename, $mime_ext, $media_type) = DB_fetchArray($result);\n    if ((int) $media_type !== 0) {\n        COM_errorLog('MediaGallery: rotate rejected for non-image media ' . $media_id, 1);\n        if ($actionURL == -1 || $actionURL == '') {\n            return false;\n        }\n        COM_redirect($_MG_CONF['site_url'] . '/album.php?aid=' . $album_id);\n    }"""
text = replace_once(text, old, new, 'rotate access/binding guard')
p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# Documentation
# ------------------------------------------------------------------
p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
roadmap = roadmap.replace(
    '- [ ] Continue mutation audit for resize/rebuild/batch/rotate paths and confirm owner/admin permission boundaries.',
    '- [x] Harden resize/rebuild confirmations, media manager save/delete/move/batch actions and direct rotation with Geeklog CSRF tokens; direct rotation now uses POST and revalidates album write access plus album/media membership.\n- [x] Revalidate media edit/reset mutations server-side and correct reset handlers to read their posted album id.\n- [ ] Continue audit of remaining caption/moderation/delete-session mutations before RC.'
)
p.write_text(roadmap, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
needle = '- continue permission/CSRF audit for resize/rebuild/batch/rotate mutation paths;'
replacement = '- resize/rebuild, media-manager save/delete/move/batch, direct rotation, media-edit save and rating/view resets now use Geeklog CSRF validation;\n- direct rotation now uses POST and verifies both album write access and the requested album/media association before touching files;\n- continue audit of remaining caption/moderation/delete-session mutations before RC;'
if needle in notes:
    notes = notes.replace(needle, replacement, 1)
else:
    marker = 'Still review before RC:\n\n'
    notes = notes.replace(marker, marker + replacement + '\n', 1)
p.write_text(notes, encoding='utf-8')

print('Mutation security hardening patch prepared.')
