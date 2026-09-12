from pathlib import Path

p = Path('include/sort.php')
text = p.read_text(encoding='utf-8')

# Album sort form token variables.
old = """        'lang_cancel'          => $LANG_MG01['cancel'],\n        's_form_action'        => $_MG_CONF['site_url'] . '/admin.php',\n    ));"""
new = """        'lang_cancel'          => $LANG_MG01['cancel'],\n        's_form_action'        => $_MG_CONF['site_url'] . '/admin.php',\n        'gltoken_name'         => CSRF_TOKEN,\n        'gltoken'              => SEC_createToken(),\n    ));"""
if old not in text:
    raise SystemExit('album sort form variable anchor not found')
text = text.replace(old, new, 1)

# Album sort save token guard after admin rights.
old = """    if (!SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"MediaGallery: Someone has tried to illegally sort albums in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $parent"""
new = """    if (!SEC_hasRights('mediagallery.admin')) {\n        COM_errorLog(\"MediaGallery: Someone has tried to illegally sort albums in Media Gallery. \"\n                   . \"User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: $REMOTE_ADDR\",1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: album sort rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $parent"""
if old not in text:
    raise SystemExit('album sort save guard anchor not found')
text = text.replace(old, new, 1)

# Static sort form token variables.
old = """        'lang_order_options'       => $LANG_MG01['order_options'],\n    ));"""
new = """        'lang_order_options'       => $LANG_MG01['order_options'],\n        'gltoken_name'             => CSRF_TOKEN,\n        'gltoken'                  => SEC_createToken(),\n    ));"""
if old not in text:
    raise SystemExit('static sort form variable anchor not found')
text = text.replace(old, new, 1)

# Static sort save must revalidate access and token server-side.
old = """    if ($album_id == 0) {\n        COM_errorLog(\"Media Gallery: Invalid album_id passed to sort\");\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    //\n    // -- get the sort options\n"""
new = """    if ($album_id == 0) {\n        COM_errorLog(\"Media Gallery: Invalid album_id passed to sort\");\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    $album = new mgAlbum($album_id);\n    if (!isset($album->id) || !$album->valid || ($album->access != 3 && !SEC_hasRights('mediagallery.admin'))) {\n        COM_errorLog('MediaGallery: static media sort rejected because the user has no write access to album ' . intval($album_id), 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n    if (!SEC_checkToken()) {\n        COM_errorLog('MediaGallery: static media sort rejected because of an invalid CSRF token.', 1);\n        return COM_showMessageText($LANG_MG00['access_denied_msg']);\n    }\n\n    //\n    // -- get the sort options\n"""
if old not in text:
    raise SystemExit('static sort save guard anchor not found')
text = text.replace(old, new, 1)

p.write_text(text, encoding='utf-8')

# Template tokens.
for filename, anchor in (
    ('templates/sortalbum.thtml', '    <input type="hidden" name="album_id" value="0"{xhtml}>\n'),
    ('templates/staticsort.thtml', '  <input type="hidden" name="album_id" value="{album_id}"{xhtml}>\n'),
):
    p = Path(filename)
    t = p.read_text(encoding='utf-8')
    if anchor not in t:
        raise SystemExit(filename + ': token anchor not found')
    t = t.replace(anchor, anchor + ('    ' if 'sortalbum' in filename else '  ') + '<input type="hidden" name="{gltoken_name}" value="{gltoken}"{xhtml}>\n', 1)
    p.write_text(t, encoding='utf-8')

p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
roadmap = roadmap.replace(
    '- [ ] Continue mutation audit for resize/rebuild/sort/batch paths and confirm owner/admin permission boundaries.',
    '- [x] Harden album/static sort mutations with Geeklog CSRF tokens and revalidate static-sort album write access server-side.\n- [ ] Continue mutation audit for resize/rebuild/batch/rotate paths and confirm owner/admin permission boundaries.'
)
p.write_text(roadmap, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
notes = p.read_text(encoding='utf-8')
notes = notes.replace(
    '- continue permission/CSRF audit for resize/rebuild/sort/batch mutation paths;',
    '- album sort and static media sort now use Geeklog CSRF tokens; static sort also revalidates album write access in the save handler;\n- continue permission/CSRF audit for resize/rebuild/batch/rotate mutation paths;'
)
p.write_text(notes, encoding='utf-8')

print('Sort security patch prepared.')
