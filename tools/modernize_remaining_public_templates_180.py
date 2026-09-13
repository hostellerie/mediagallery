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

# Public profile sections: keep real table semantics, remove presentation-only inline styles,
# add scoped headers and a narrow-screen overflow wrapper.
Path('templates/profile_album.thtml').write_text('''{start_block_useralbums}\n  <div class="mg_table_scroll mg_profile_table_scroll">\n    <table class="mg_mediaitems_table mg_profile_table mg_profile_album_table">\n      <tr>\n        <th scope="col" class="mg_profile_thumb_col">{lang_thumbnail}</th>\n        <th scope="col" class="mg_profile_album_col">{lang_album}</th>\n        <th scope="col" class="mg_profile_desc_col">{lang_album_description}</th>\n      </tr>\n      <!-- BEGIN itemRow -->\n      <tr>\n        <td class="mg_profile_thumb">{album_begin_href}{album_cover}{album_end_href}</td>\n        <td class="mg_profile_title">{album_title}</td>\n        <td class="mg_profile_desc">{album_desc}</td>\n      </tr>\n      <!-- END itemRow -->\n    </table>\n  </div>\n{end_block}\n''', encoding='utf-8')

Path('templates/profile_media.thtml').write_text('''{start_block_last10mediaitems}\n  <div class="mg_table_scroll mg_profile_table_scroll">\n    <table class="mg_mediaitems_table mg_profile_table mg_profile_media_table">\n      <tr>\n        <th scope="col" class="mg_profile_thumb_col">{lang_thumbnail}</th>\n        <th scope="col" class="mg_profile_media_title_col">{lang_title}</th>\n        <th scope="col" class="mg_profile_media_album_col">{lang_album}</th>\n        <th scope="col" class="mg_profile_date_col">{lang_upload_date}</th>\n      </tr>\n      <!-- BEGIN itemRow -->\n      <tr>\n        <td class="mg_profile_thumb">{mediaitem_begin_href}{mediaitem_image}{mediaitem_end_href}</td>\n        <td class="mg_profile_title">{mediaitem_title}</td>\n        <td class="mg_profile_album">{mediaitem_album_begin_href}<strong>{mediaitem_album_title}</strong>{mediaitem_end_href}</td>\n        <td class="mg_profile_date">{mediaitem_date}</td>\n      </tr>\n      <!-- END itemRow -->\n    </table>\n  </div>\n{end_block}\n''', encoding='utf-8')

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

.mg_profile_table {
  width: 100%;
  min-width: 36rem;
}

.mg_profile_thumb_col {
  width: 3.5rem;
}

.mg_profile_album_col,
.mg_profile_media_title_col,
.mg_profile_media_album_col {
  width: 35%;
}

.mg_profile_desc_col {
  width: 55%;
}

.mg_profile_date_col {
  width: 20%;
}

.mg_profile_thumb {
  vertical-align: middle;
  text-align: center;
}

.mg_profile_title,
.mg_profile_desc,
.mg_profile_album {
  vertical-align: middle;
  text-align: left;
}

.mg_profile_date {
  vertical-align: middle;
  text-align: center;
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
addition = needle + '- [x] Modernize active media popups, public profile tables and remaining audio fragments for responsive rendering.\n'
if text.count(needle) != 1:
    raise SystemExit('ROADMAP remaining public template marker mismatch')
p.write_text(text.replace(needle, addition, 1), encoding='utf-8')
