from pathlib import Path


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit('Expected one marker for %s, found %d' % (label, text.count(old)))
    return text.replace(old, new, 1)

# Album editor: values rendered into input/textarea contexts must be escaped at
# output time. Also harden locally generated option labels/attribute values.
p = Path('include/albumedit.php')
text = p.read_text(encoding='utf-8')
text = replace_once(text,
    "            . '>' . $themes[$i] . '</option>';",
    "            . '>' . MG_escapeHTML($themes[$i]) . '</option>';",
    'album theme label')
text = replace_once(text,
    "            . '>' . COM_getDisplayName($row['uid']) . '</option>';",
    "            . '>' . MG_escapeHTML(COM_getDisplayName($row['uid'])) . '</option>';",
    'album owner display name')
text = replace_once(text,
    "        $wm_select .= '<option value=\"' . $row['filename'] . '\"'",
    "        $wm_select .= '<option value=\"' . MG_escapeHTML($row['filename']) . '\"'",
    'watermark option value')
text = replace_once(text,
    "                    . '>' . $row['filename'] . '</option>';",
    "                    . '>' . MG_escapeHTML($row['filename']) . '</option>';",
    'watermark option label')
text = replace_once(text,
    "            $wm_current = '<img src=\"' . $_MG_CONF['site_url'] . '/watermarks/' . $row['filename'] . '\" name=\"myImage\" alt=\"\"' . XHTML . '>';",
    "            $wm_current = '<img src=\"' . MG_escapeHTML($_MG_CONF['site_url'] . '/watermarks/' . $row['filename']) . '\" name=\"myImage\" alt=\"\"' . XHTML . '>';",
    'watermark current URL')
text = replace_once(text,
    "            $groupdd .= '>' . key($usergroups) . '</option>';\n            $moddd   .= '>' . key($usergroups) . '</option>';",
    "            $groupdd .= '>' . MG_escapeHTML(key($usergroups)) . '</option>';\n            $moddd   .= '>' . MG_escapeHTML(key($usergroups)) . '</option>';",
    'group option labels')
text = replace_once(text,
    "        'album_title'             => $album->title,\n        'album_desc'              => $album->description,",
    "        'album_title'             => MG_escapeHTML($album->title),\n        'album_desc'              => MG_escapeHTML($album->description),",
    'album editable text')
p.write_text(text, encoding='utf-8')

# Category editor: preserve allowed HTML in storage, but escape it for safe
# round-tripping through input/textarea controls.
p = Path('admin/category.php')
text = p.read_text(encoding='utf-8')
text = replace_once(text,
    "        'cat_name'            => $A['cat_name'],\n        'cat_description'     => $A['cat_description'],",
    "        'cat_name'            => MG_escapeHTML($A['cat_name']),\n        'cat_description'     => MG_escapeHTML($A['cat_description']),",
    'category editable text')
p.write_text(text, encoding='utf-8')

# Record the completed admin-form output hardening while keeping the broader
# all-template audit open.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
marker = '- [x] Replace the lightbox slideshow href-injection workaround with valid escaped album-action attributes across maintained album themes.\n'
addition = marker + '- [x] Escape editable album/category values and generated admin option labels when rendering form controls.\n'
text = replace_once(text, marker, addition, 'roadmap admin escaping')
p.write_text(text, encoding='utf-8')
