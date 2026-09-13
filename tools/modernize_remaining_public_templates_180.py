from pathlib import Path


# Active media popup: modern HTML5 shell, responsive viewport, and noindex to avoid duplicate indexing.
Path('templates/view_window.thtml').write_text('''<!doctype html>\n<html>\n<head>\n<meta charset="{charset}">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="robots" content="noindex,follow">\n<title>{title}</title>\n{themeCSS}\n</head>\n<body class="mg-media-popup-body">\n<main class="mg-media-popup">\n{object}\n</main>\n</body>\n</html>\n''', encoding='utf-8')

# Give the popup a useful title; keep the actual media output contract untouched.
p = Path('public_html/view.php')
text = p.read_text(encoding='utf-8')
old = """$T->set_var(array(\n    'site_url' => $_MG_CONF['site_url'],\n    'themeCSS' => $themeCSS,\n    'charset'  => COM_getCharset(),\n    'object'   => $object[0],\n));"""
new = """$popupTitle = !empty($row['media_title']) ? strip_tags($row['media_title']) : $row['media_original_filename'];\n\n$T->set_var(array(\n    'site_url' => $_MG_CONF['site_url'],\n    'themeCSS' => $themeCSS,\n    'charset'  => COM_getCharset(),\n    'title'    => MG_escapeHTML($popupTitle),\n    'object'   => $object[0],\n));"""
if text.count(old) != 1:
    raise SystemExit('view.php popup vars marker mismatch')
p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Legacy audio popup/template names stay supported; remove fixed inline widths.
Path('templates/mp3_wmp.thtml').write_text('''<!doctype html>\n<html>\n<head>\n<meta charset="{charset}">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n{themeCSS}\n<title>{title}</title>\n</head>\n<body class="mg-player-popup-body">\n<div class="mg-media-player mg-media-player-audio mg-media-player-popup" style="max-width:{width}px;">\n  {u_pic}\n  <audio controls preload="metadata">\n    <source src="{movie}">\n    <a href="{movie}">{title}</a>\n  </audio>\n</div>\n</body>\n</html>\n''', encoding='utf-8')

Path('templates/mp3_podcast.thtml').write_text('''<div class="mg-media-player mg-media-player-audio mg-media-player-podcast">\n  <audio controls preload="metadata">\n    <source src="{mp3_file}" type="audio/mpeg">\n    <a href="{mp3_file}">{title}</a>\n  </audio>\n</div>\n''', encoding='utf-8')

# File-list row: keep table semantics but move presentation widths/alignment to CSS.
p = Path('templates/filelist.thtml')
text = p.read_text(encoding='utf-8')
replacements = {
    '<td style="width:52px;text-align:center;vertical-align:top;">': '<td class="mg_filelist_thumb">',
    '<td style="vertical-align:top;">': '<td class="mg_filelist_content">',
    '<td style="width:90px;vertical-align:top;white-space:nowrap;">': '<td class="mg_filelist_size">',
    '<td style="width:120px;vertical-align:top;white-space:nowrap;">': '<td class="mg_filelist_user">',
    '<td style="width:160px;vertical-align:top;white-space:nowrap;">': '<td class="mg_filelist_updated">',
}
for old, new in replacements.items():
    text = text.replace(old, new)
p.write_text(text, encoding='utf-8')

# Profile tables: retain compatible/tabular markup, strip presentation-only inline styles.
for path in ('templates/profile_album.thtml', 'templates/profile_media.thtml'):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    text = text.replace('<table class="mg_mediaitems_table" style="width:100%;">', '<div class="mg_table_scroll mg_profile_table_scroll" role="region" tabindex="0">\n<table class="mg_mediaitems_table mg_profile_table">')
    text = text.rstrip() + '\n</div>\n'
    text = text.replace('<td style="width:20%;vertical-align:top;text-align:center;">', '<td class="mg_profile_thumb">')
    text = text.replace('<td style="width:60%;vertical-align:top;">', '<td class="mg_profile_content">')
    text = text.replace('<td style="width:20%;vertical-align:top;white-space:nowrap;">', '<td class="mg_profile_meta">')
    p.write_text(text, encoding='utf-8')

# Final public-fragment responsive CSS.
p = Path('public_html/style.css')
text = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 remaining public template layer */'
if marker in text:
    raise SystemExit('Remaining public template layer already present')
css = r'''

/* MediaGallery 1.8 remaining public template layer */
.mg-media-popup-body {
  margin: 0;
  padding: 0;
  background: #000;
}

.mg-media-popup {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.mg-media-popup img,
.mg-media-popup video,
.mg-media-popup audio,
.mg-media-popup iframe,
.mg-media-popup object,
.mg-media-popup embed {
  max-width: 100%;
}

.mg-media-popup img,
.mg-media-popup video {
  height: auto;
}

.mg-media-player-podcast {
  max-width: 18.125rem;
}

.mg_filelist_thumb {
  width: 3.25rem;
  text-align: center;
  vertical-align: top;
}

.mg_filelist_content {
  vertical-align: top;
}

.mg_filelist_size {
  width: 5.625rem;
  vertical-align: top;
  white-space: nowrap;
}

.mg_filelist_user {
  width: 7.5rem;
  vertical-align: top;
  white-space: nowrap;
}

.mg_filelist_updated {
  width: 10rem;
  vertical-align: top;
  white-space: nowrap;
}

.mg_profile_table {
  width: 100%;
  min-width: 36rem;
}

.mg_profile_thumb {
  width: 20%;
  vertical-align: top;
  text-align: center;
}

.mg_profile_content {
  width: 60%;
  vertical-align: top;
}

.mg_profile_meta {
  width: 20%;
  vertical-align: top;
  white-space: nowrap;
}

.mg_profile_thumb img {
  max-width: 100%;
  height: auto;
}

@media (max-width: 40rem) {
  .mg-media-popup {
    align-items: flex-start;
  }
}
'''
p.write_text(text + css, encoding='utf-8')

# Precise roadmap entry only; broader inline-style task stays open.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
needle = '- [x] Modernize secondary public autotag, random-block, fullscreen-slideshow and maintained HTML5 audio rendering for responsive output.\n'
addition = needle + '- [x] Modernize active media popups plus profile, file-list and remaining audio fragments for responsive public rendering.\n'
if text.count(needle) != 1:
    raise SystemExit('ROADMAP remaining public template marker mismatch')
p.write_text(text.replace(needle, addition, 1), encoding='utf-8')
