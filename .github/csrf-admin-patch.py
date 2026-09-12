from pathlib import Path

# ------------------------------------------------------------------
# include/global.php
# ------------------------------------------------------------------
p = Path('include/global.php')
text = p.read_text(encoding='utf-8')

# Add token variables to global permission editor.
old = """        'lang_email_mods_on_submission' => $LANG_MG01['email_mods_on_submission']\n    ));"""
new = """        'lang_email_mods_on_submission' => $LANG_MG01['email_mods_on_submission'],\n        'gltoken_name'          => CSRF_TOKEN,\n        'gltoken'               => SEC_createToken()\n    ));"""
if old not in text:
    raise SystemExit('global permission template variables anchor not found')
text = text.replace(old, new, 1)

# Add token validation to permission save.
old = """    if (!SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Media Gallery user attempted to edit global album attributes without proper access.\");\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $A['group_id']"""
new = """    if (!SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Media Gallery user attempted to edit global album attributes without proper access.\");\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: global album permission update rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $A['group_id']"""
if old not in text:
    raise SystemExit('global permission save guard anchor not found')
text = text.replace(old, new, 1)

# Add token vars to global attribute editor at the end of its variable map.
old = """        'lang_tnwidth'          => $LANG_MG01['tn_width'],\n    ));"""
new = """        'lang_tnwidth'          => $LANG_MG01['tn_width'],\n        'gltoken_name'         => CSRF_TOKEN,\n        'gltoken'              => SEC_createToken(),\n    ));"""
if old not in text:
    raise SystemExit('global attribute template variables anchor not found')
text = text.replace(old, new, 1)

# Add token validation to attribute save (same legacy rights block occurs later).
old = """function MG_saveGlobalAlbumAttr()\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01;\n\n    if (!SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Media Gallery user attempted to edit global album attributes without proper access.\");\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $startaid"""
new = """function MG_saveGlobalAlbumAttr()\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01;\n\n    if (!SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Media Gallery user attempted to edit global album attributes without proper access.\");\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: global album attribute update rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $startaid"""
if old not in text:
    raise SystemExit('global attribute save guard anchor not found')
text = text.replace(old, new, 1)

p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# templates/global_album_perm.thtml + global_album_attr.thtml
# ------------------------------------------------------------------
for filename in ('templates/global_album_perm.thtml', 'templates/global_album_attr.thtml'):
    p = Path(filename)
    text = p.read_text(encoding='utf-8')
    anchor = '<input type="hidden" name="admin_menu" value="{admin_menu}"{xhtml}>\n'
    token = anchor + '<input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n'
    if anchor not in text:
        raise SystemExit(filename + ': hidden field anchor not found')
    text = text.replace(anchor, token, 1)
    p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# include/lib-watermark.php
# ------------------------------------------------------------------
p = Path('include/lib-watermark.php')
text = p.read_text(encoding='utf-8')

# Management form gets a token.
old = """        'lang_watermark_manage_help' => $LANG_MG01['watermark_manage_help'],\n    ));"""
new = """        'lang_watermark_manage_help' => $LANG_MG01['watermark_manage_help'],\n        'gltoken_name' => CSRF_TOKEN,\n        'gltoken'      => SEC_createToken(),\n    ));"""
if old not in text:
    raise SystemExit('watermark manage template variables anchor not found')
text = text.replace(old, new, 1)

# Save mutation token guard.
old = """    if ($root_album->access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally save a watermark image in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $numItems"""
new = """    if ($root_album->access != 3 && !SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"Someone has tried to illegally save a watermark image in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: watermark update rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $numItems"""
if old not in text:
    raise SystemExit('watermark save guard anchor not found')
text = text.replace(old, new, 1)

# Delete mutation token guard. Match unique function prefix.
old = """function MG_watermarkDelete($actionURL = '')\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG03;\n\n    $root_album = new mgAlbum(0);\n\n    // check permissions...\n    if ($root_album->access != 3 && !$root_album->owner_id/*SEC_hasRights('mediagallery.admin')*/) {\n        COM_errorLog(\"Someone has tried to illegally save a watermark image in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $numItems"""
new = """function MG_watermarkDelete($actionURL = '')\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG03;\n\n    $root_album = new mgAlbum(0);\n\n    // check permissions...\n    if ($root_album->access != 3 && !$root_album->owner_id/*SEC_hasRights('mediagallery.admin')*/) {\n        COM_errorLog(\"Someone has tried to illegally save a watermark image in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: watermark deletion rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $numItems"""
if old not in text:
    raise SystemExit('watermark delete guard anchor not found')
text = text.replace(old, new, 1)

# Upload form gets a token.
old = """        'lang_warning'          => $warning,\n    ));"""
new = """        'lang_warning'          => $warning,\n        'gltoken_name'          => CSRF_TOKEN,\n        'gltoken'               => SEC_createToken(),\n    ));"""
if old not in text:
    raise SystemExit('watermark upload template variables anchor not found')
text = text.replace(old, new, 1)

# Upload-save: preserve existing policy but enforce same permissions as form and token.
old = """function MG_watermarkUploadSave()\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG02, $LANG_MG03;\n\n    // ok, we just check the type, we will accept png,jpg for now...\n"""
new = """function MG_watermarkUploadSave()\n{\n    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG02, $LANG_MG03;\n\n    $root_album = new mgAlbum(0);\n    if ($root_album->access != 3 && !$root_album->owner_id) {\n        COM_errorLog('MediaGallery: watermark upload rejected because of insufficient access.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: watermark upload rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    // ok, we just check the type, we will accept png,jpg for now...\n"""
if old not in text:
    raise SystemExit('watermark upload save function anchor not found')
text = text.replace(old, new, 1)

p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# Watermark templates
# ------------------------------------------------------------------
p = Path('templates/wm_manage.thtml')
text = p.read_text(encoding='utf-8')
anchor = '    <input type="hidden" name="album_id" value="0"{xhtml}>\n'
new = anchor + '    <input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n'
if anchor not in text:
    raise SystemExit('wm_manage token anchor not found')
text = text.replace(anchor, new, 1)
p.write_text(text, encoding='utf-8')

p = Path('templates/wm_upload.thtml')
text = p.read_text(encoding='utf-8')
anchor = '      <input type="hidden" name="action" value="{action}"{xhtml}>\n'
new = anchor + '      <input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n'
if anchor not in text:
    raise SystemExit('wm_upload token anchor not found')
text = text.replace(anchor, new, 1)
p.write_text(text, encoding='utf-8')

# ------------------------------------------------------------------
# Documentation
# ------------------------------------------------------------------
p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
roadmap = roadmap.replace(
    '- [ ] Review less common album mutation/admin permission paths.',
    '- [x] Add CSRF protection to global album permission/attribute mutations and watermark manage/upload/delete mutations while preserving their existing access rules.\n- [ ] Continue mutation audit for resize/rebuild/sort/batch paths and confirm owner/admin permission boundaries.'
)
p.write_text(roadmap, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
needle = '- permissions around less common album mutation/admin paths;'
replacement = '- global album permission/attribute changes and watermark manage/upload/delete actions now use Geeklog CSRF tokens in addition to their existing access rules;\n- continue permission/CSRF audit for resize/rebuild/sort/batch mutation paths;'
if needle in notes:
    notes = notes.replace(needle, replacement, 1)
else:
    marker = 'Still review before RC:\n\n'
    notes = notes.replace(marker, marker + replacement + '\n', 1)
p.write_text(notes, encoding='utf-8')

print('Global/watermark CSRF hardening patch prepared.')
