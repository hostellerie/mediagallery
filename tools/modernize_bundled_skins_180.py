from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one %s marker in %s, found %d' % (label, path, count))
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


def modernize_standard_header(path):
    replace_once(path, '<div class="bc_navigation">\n{birdseed}\n</div>', '<nav class="bc_navigation" aria-label="Breadcrumb">\n{birdseed}\n</nav>', 'breadcrumb')
    replace_once(path, '<div class="mg_album_header">\n<div class="mg_album_title"><strong>{album_title}</strong>{!if rsslink}&nbsp;&nbsp;{rsslink}{!endif}</div>', '<header class="mg_album_header">\n<h1 class="mg_album_title">{album_title}{!if rsslink}&nbsp;&nbsp;{rsslink}{!endif}</h1>', 'album header')
    replace_once(path, '<form name="mgsearch" method="post" action="{site_url}/search.php" class="uk-form">\n<div>\n  <input type="text" name="keywords" value="{keywords}"{xhtml}>', '<form name="mgsearch" method="post" action="{site_url}/search.php" class="uk-form" role="search">\n<div>\n  <label for="mg-skin-search-keywords" class="mg-visually-hidden">{lang_search}</label>\n  <input id="mg-skin-search-keywords" type="search" name="keywords" value="{keywords}" aria-label="{lang_search}"{xhtml}>', 'skin search')
    replace_once(path, '{!endif}\n</div>\n\n', '{!endif}\n</header>\n\n', 'album header close')

# File-list skin: semantic header + horizontally scrollable data table on narrow screens.
modernize_standard_header('templates/themes/filelist/album_page.thtml')
replace_once('templates/themes/filelist/album_page.thtml', '<table class="mg_mediaitems_table">', '<div class="mg_table_scroll" role="region" aria-label="Media list" tabindex="0">\n<table class="mg_mediaitems_table mg_filelist_table">', 'filelist table open')
replace_once('templates/themes/filelist/album_page.thtml', '</table>\n\n{!if lang_no_image}', '</table>\n</div>\n\n{!if lang_no_image}', 'filelist table close')
replace_once('templates/themes/filelist/album_page.thtml', '<th style="width:52px;text-align:center;">&nbsp;</th>', '<th class="mg_filelist_thumb_col">&nbsp;</th>', 'filelist thumb header')
replace_once('templates/themes/filelist/album_page.thtml', '<div class="mg_navbar">', '<nav class="mg_navbar" aria-label="Album actions and pagination">', 'filelist top navbar')
# There are two navbar closes; convert the first nav closing only and second separately.
p = Path('templates/themes/filelist/album_page.thtml')
text = p.read_text(encoding='utf-8')
idx = text.find('</div>', text.find('<nav class="mg_navbar"'))
if idx == -1:
    raise SystemExit('filelist first navbar close not found')
text = text[:idx] + '</nav>' + text[idx+6:]
# Bottom navbar remains div to avoid guessing nested pagination close; give semantic role instead.
last = text.rfind('<div class="mg_navbar">')
if last != -1:
    text = text[:last] + '<nav class="mg_navbar" aria-label="Album status and pagination">' + text[last+len('<div class="mg_navbar">'):]
    close = text.find('</div>', last)
    # nested pagination closes first; use final close before jumpbox
    marker = '</div>\n<div class="mg_jumpbox">'
    if marker not in text:
        raise SystemExit('filelist bottom navbar close marker missing')
    text = text.replace(marker, '</nav>\n<div class="mg_jumpbox">', 1)
p.write_text(text, encoding='utf-8')

# Podcast skin: replace one-column presentation table with a semantic responsive list.
modernize_standard_header('templates/themes/podcast/album_page.thtml')
old_table = '''<table style="width:100%;border:none;margin:0px auto;">
<!-- BEGIN ImageRow -->
<!-- BEGIN ImageColumn -->
<tr>
<td style="width:{table_column_width};vertical-align:top;">
{CELL_DISPLAY_IMAGE}
</td>
</tr>
<!-- END ImageColumn -->
<!-- END ImageRow -->
</table>'''
new_list = '''<div class="mg_podcast_list" role="list">
<!-- BEGIN ImageRow -->
<!-- BEGIN ImageColumn -->
<div class="mg_podcast_item" role="listitem">
{CELL_DISPLAY_IMAGE}
</div>
<!-- END ImageColumn -->
<!-- END ImageRow -->
</div>'''
replace_once('templates/themes/podcast/album_page.thtml', old_table, new_list, 'podcast list')
replace_once('templates/themes/podcast/album_page_body.thtml', old_table, new_list, 'podcast body list')

# SimpleViewer: semantic header and responsive viewport instead of hard-coded 800px inline height.
modernize_standard_header('templates/themes/simpleviewer/album_page.thtml')
replace_once('templates/themes/simpleviewer/album_page.thtml', '<div style="text-align:center;">', '<div class="mg_simpleviewer">', 'simpleviewer wrapper')
replace_once('templates/themes/simpleviewer/album_page.thtml', '<div class="sv-container-wrapper" style="height:800px">', '<div class="sv-container-wrapper">', 'simpleviewer height')

# jQuery gallery skins: replace float-based inline title/admin header with semantic responsive header.
for path in ('templates/themes/jquery_colorbox/album_page.thtml', 'templates/themes/jquery_ad-gallery/album_page.thtml'):
    replace_once(path, '<div class="bc_navigation">\n{birdseed}\n</div>', '<nav class="bc_navigation" aria-label="Breadcrumb">\n{birdseed}\n</nav>', 'jquery breadcrumb')
    old = '''<h2 style="float:left;font-weight:bold;font-size:2em;line-height:2em;padding-left:5px;">{album_title}</h2>
<div class="" style="float:right;text-align:right;vertical-align:middle;white-space:nowrap;padding-right:5px;line-height:2em;">
  {!if rsslink}
    &nbsp;{rsslink}
  {!endif}
  {select_adminbox}
</div>
<div style="clear:both;"></div>'''
    new = '''<header class="mg_album_header mg_theme_gallery_header">
  <h1 class="mg_album_title">{album_title}</h1>
  <div class="mg_theme_gallery_actions">
    {!if rsslink}{rsslink}{!endif}
    {select_adminbox}
  </div>
</header>'''
    replace_once(path, old, new, 'jquery gallery header')
    replace_once(path, '<div style="text-align:left;line-height:1.5em;font-size:1.2em;text-indent:0;padding:1em 50px;">', '<div class="mg_album_description mg_theme_gallery_description">', 'jquery gallery description')

# Responsive skin-specific CSS overrides.
p = Path('public_html/style.css')
text = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 bundled skin responsive layer */'
if marker in text:
    raise SystemExit('Bundled skin responsive layer already present')
css = r'''

/* MediaGallery 1.8 bundled skin responsive layer */
.mg_table_scroll {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.mg_filelist_table {
  width: 100%;
  min-width: 42rem;
  border-collapse: collapse;
}

.mg_filelist_thumb_col {
  width: 3.25rem;
  text-align: center;
}

.mg_podcast_list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  width: 100%;
  margin: 1rem 0;
}

.mg_podcast_item {
  min-width: 0;
}

.mg_theme_gallery_header {
  margin-bottom: 0.75rem;
}

.mg_theme_gallery_actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  flex: 0 1 auto;
  min-width: 0;
}

.mg_theme_gallery_description {
  text-align: left;
  font-size: 1rem;
  line-height: 1.6;
  padding: 0 0.75rem;
}

.mg_simpleviewer {
  width: 100%;
  text-align: center;
}

.sv-container-wrapper {
  width: 100%;
  min-height: 28rem;
  height: min(75vh, 50rem);
}

#sv-container,
#ad-gallery,
#mg_colorbox {
  max-width: 100%;
}

@media (max-width: 48rem) {
  .mg_theme_gallery_actions {
    flex: 1 1 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .sv-container-wrapper {
    min-height: 20rem;
    height: 65vh;
  }
}

@media (max-width: 34rem) {
  .mg_theme_gallery_description {
    padding: 0;
  }

  .sv-container-wrapper {
    min-height: 18rem;
    height: 60vh;
  }
}
'''
p.write_text(text.rstrip() + css + '\n', encoding='utf-8')

p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
marker = '- [x] Modernize default album/search/media rendering with responsive CSS Grid/Flexbox, semantic media/card headings and responsive thumbnail frames.\n'
addition = marker + '- [x] Modernize bundled file-list, podcast, jQuery gallery and SimpleViewer skins for responsive layouts and semantic album headings.\n'
if text.count(marker) != 1:
    raise SystemExit('Roadmap responsive rendering marker mismatch')
p.write_text(text.replace(marker, addition, 1), encoding='utf-8')
