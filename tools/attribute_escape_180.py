from pathlib import Path


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit('Expected one marker for %s, found %d' % (label, text.count(old)))
    return text.replace(old, new, 1)

# Replace the historical lightbox slideshow href-breaking trick with a valid
# href plus a separate, constant onclick attribute. Escape the URL normally.
p = Path('include/common.php')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    "    $url_slideshow = '';\n    $lang_slideshow = '';\n",
    "    $url_slideshow = '';\n    $slideshow_onclick = '';\n    $lang_slideshow = '';\n",
    'slideshow onclick initialization'
)
text = replace_once(
    text,
    "                $url_slideshow  = '#\\\" onclick=\\\"return openGallery1()';\n                $lang_slideshow = $LANG_MG03['slide_show'];\n",
    "                $url_slideshow = '#';\n                $slideshow_onclick = ' onclick=\"return openGallery1()\"';\n                $lang_slideshow = $LANG_MG03['slide_show'];\n",
    'lightbox slideshow URL hack'
)
text = replace_once(
    text,
    "        'lang_slideshow' => $lang_slideshow,\n        'url_slideshow'  => $url_slideshow,\n",
    "        'lang_slideshow'     => $lang_slideshow,\n        'url_slideshow'      => MG_escapeHTML($url_slideshow),\n        'slideshow_onclick'  => $slideshow_onclick,\n",
    'slideshow template variables'
)
p.write_text(text, encoding='utf-8')

# Every maintained album-page variant using url_slideshow gets the dedicated
# constant onclick slot. Do not touch templates that do not expose the action.
changed_templates = []
for p in [Path('templates/album_page.thtml')] + sorted(Path('templates/themes').glob('*/album_page.thtml')):
    text = p.read_text(encoding='utf-8')
    old = 'href="{url_slideshow}"'
    if old in text:
        text = text.replace(old, 'href="{url_slideshow}"{slideshow_onclick}')
        p.write_text(text, encoding='utf-8')
        changed_templates.append(str(p))
if not changed_templates:
    raise SystemExit('No album-page slideshow href found')

# Album edit links are internal but still belong to an attribute context.
# Also define the search input value explicitly as empty on album pages.
p = Path('public_html/album.php')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    "        $url_edit = $_MG_CONF['site_url'] . '/admin.php?album_id=' . $album->id . '&amp;mode=edit';\n        $lang_edit = $LANG_MG01['edit'];\n        $edit_album = '<a href=\"' . $url_edit . '\">' . $lang_edit . '</a>';\n",
    "        $url_edit = MG_escapeHTML($_MG_CONF['site_url'] . '/admin.php?album_id=' . $album->id . '&amp;mode=edit');\n        $lang_edit = $LANG_MG01['edit'];\n        $edit_album = '<a href=\"' . $url_edit . '\">' . $lang_edit . '</a>';\n",
    'album edit URL'
)
text = replace_once(
    text,
    "    'lang_search'        => $LANG_MG01['search'],\n",
    "    'lang_search'        => $LANG_MG01['search'],\n    'keywords'           => '',\n",
    'album search keywords default'
)
p.write_text(text, encoding='utf-8')

# Keep the global audit open until the remaining non-album templates have been
# classified, but record this completed theme-wide album action cleanup.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
marker = '- [x] Centralize HTML escaping for framed-image attributes, media edit/manage values, lightbox links and advanced-search values.\n'
addition = marker + '- [x] Replace the lightbox slideshow href-injection workaround with valid escaped album-action attributes across maintained album themes.\n'
text = replace_once(text, marker, addition, 'roadmap album theme escaping')
p.write_text(text, encoding='utf-8')

print('Updated album templates:')
for name in changed_templates:
    print(' - ' + name)
