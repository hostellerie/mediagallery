from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one %s marker in %s, found %d' % (label, path, count))
    p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Preserve legacy template variables but expose a stable responsive grid class.
replace_once(
    'public_html/album.php',
    "    'table_columns'      => $columns_per_page,\n    'table_column_width' => intval(100 / $columns_per_page) . '%',",
    "    'table_columns'      => $columns_per_page,\n    'grid_class'         => 'mg-cols-' . max(1, min(10, (int) $columns_per_page)),\n    'table_column_width' => intval(100 / $columns_per_page) . '%',",
    'album grid class')

# Search results use the same responsive grid contract.
p = Path('public_html/search.php')
text = p.read_text(encoding='utf-8')
old = "        'table_columns'        => $columns_per_page,\n        'table_column_width'   => intval(100 / $columns_per_page) . '%',"
new = "        'table_columns'        => $columns_per_page,\n        'grid_class'           => 'mg-cols-' . max(1, min(10, (int) $columns_per_page)),\n        'table_column_width'   => intval(100 / $columns_per_page) . '%',"
count = text.count(old)
if count != 2:
    raise SystemExit('Expected two search grid markers, found %d' % count)
p.write_text(text.replace(old, new), encoding='utf-8')

# Default album grid: semantic, float-free, responsive.
replace_once(
    'templates/album_page.thtml',
    '<div class="mg_album_grid" style="width:100%;margin:10px 0;clear:both">\n<!-- BEGIN ImageRow -->\n<!-- BEGIN ImageColumn -->\n<div class="mg_album_cell" style="width:{table_column_width};{clear_float}">\n{CELL_DISPLAY_IMAGE}\n</div>\n<!-- END ImageColumn -->\n<!-- END ImageRow -->\n</div>\n<div style="clear:both"></div>',
    '<div class="mg_album_grid {grid_class}" role="list">\n<!-- BEGIN ImageRow -->\n<!-- BEGIN ImageColumn -->\n<div class="mg_album_cell" role="listitem">\n{CELL_DISPLAY_IMAGE}\n</div>\n<!-- END ImageColumn -->\n<!-- END ImageRow -->\n</div>',
    'default album grid')

# Card templates: remove fixed thumbnail heights and use semantic headings.
replace_once(
    'templates/album_page_album_cell.thtml',
    '<div class="mg_thumbnail" style="height:{row_height}px">',
    '<div class="mg_thumbnail">',
    'album thumbnail height')
replace_once(
    'templates/album_page_album_cell.thtml',
    '<div class="mg_album_item_title"><strong>{lang_album} {album_title}</strong> ({subalbum_media_count})</div>',
    '<h2 class="mg_album_item_title">{lang_album} {album_title} <span class="mg_item_count">({subalbum_media_count})</span></h2>',
    'album card heading')
replace_once(
    'templates/album_page_media_cell.thtml',
    '<div class="mg_thumbnail" style="height:{row_height}px">',
    '<div class="mg_thumbnail">',
    'media thumbnail height')
replace_once(
    'templates/album_page_media_cell.thtml',
    '<div class="mg_title">\n<strong>{media_title}</strong>',
    '<h2 class="mg_title">\n{media_title}',
    'media card heading open')
replace_once(
    'templates/album_page_media_cell.thtml',
    '</div>\n{!if artist}',
    '</h2>\n{!if artist}',
    'media card heading close')

# Search result grid uses the same layout without inline widths/clear floats.
replace_once(
    'templates/search_page.thtml',
    '<div class="mg_album_grid" style="width:100%;margin:10px 0;clear:both">',
    '<div class="mg_album_grid {grid_class}" role="list">',
    'search grid')
replace_once(
    'templates/search_page.thtml',
    '<div class="mg_album_cell" style="width:{table_column_width};{clear_float}">',
    '<div class="mg_album_cell" role="listitem">',
    'search grid cell')
replace_once(
    'templates/search_page.thtml',
    '<div style="clear:both"></div>',
    '',
    'search float clear')

# Media detail pages: one meaningful H1, accessible search/nav and no presentation-only EXIF style.
for path in ('templates/view_image.thtml', 'templates/view_audio.thtml', 'templates/view_video.thtml'):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    replacements = [
        ('<div class="bc_navigation">{birdseed}</div>', '<nav class="bc_navigation" aria-label="Breadcrumb">{birdseed}</nav>'),
        ('<div class="mg_album_header">\n  <div class="mg_album_title"><strong>{album_title}</strong>{!if rsslink}&nbsp;{rsslink}{!endif}</div>', '<header class="mg_album_header mg_media_header">\n  <div class="mg_album_context">{album_title}{!if rsslink}&nbsp;{rsslink}{!endif}</div>'),
        ('<form name="mgsearch" method="post" action="{site_url}/search.php" class="uk-form"><div>\n      <input type="text" name="keywords" value="{keywords}"{xhtml}>', '<form name="mgsearch" method="post" action="{site_url}/search.php" class="uk-form" role="search"><div>\n      <label for="mg-media-search-keywords" class="mg-visually-hidden">{lang_search}</label>\n      <input id="mg-media-search-keywords" type="search" name="keywords" value="{keywords}" aria-label="{lang_search}"{xhtml}>'),
        ('</div>\n<div class="mg_navbar">', '</header>\n<nav class="mg_navbar" aria-label="Media actions and navigation">'),
        ('</div>\n<div class="mg_media_title">{!if media_title}{media_title}{!else}&nbsp;{!endif}</div>\n<div class="mg_media_detail">', '</nav>\n<h1 class="mg_media_title">{!if media_title}{media_title}{!else}{album_title}{!endif}</h1>\n<div class="mg_media_detail">'),
        ('<div class="mg_exif_info" style="clear:both;margin:0 5px">', '<div class="mg_exif_info">'),
    ]
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise SystemExit('Expected one media-view marker in %s, found %d: %s' % (path, count, old[:50]))
        text = text.replace(old, new, 1)
    p.write_text(text, encoding='utf-8')

# All bundled thumbnail frames: responsive dimensions + lazy loading, no inline sizing.
frames = [
    'border', 'default', 'mgAlbum', 'mgShadow',
    'new_border', 'new_shadow', 'none', 'shadow'
]
old_img = '<img src="{media_thumbnail}" alt="{media_tag}" title="{media_tag}" class="image" style="max-width: {media_width}px; max-height: {media_height}px; width:100%; height:100%;"{xhtml}>'
new_img = '<img src="{media_thumbnail}" alt="{media_tag}" title="{media_tag}" class="image" width="{media_width}" height="{media_height}" loading="lazy" decoding="async"{xhtml}>'
for frame in frames:
    replace_once('public_html/frames/%s/frame.thtml' % frame, old_img, new_img, frame + ' frame image')

# Add modern responsive rules as an override layer, preserving legacy selectors for custom skins.
p = Path('public_html/style.css')
text = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 responsive rendering layer */'
if marker in text:
    raise SystemExit('Responsive rendering layer already present')
css = r'''

/* MediaGallery 1.8 responsive rendering layer */
.mg_album_header {
  display: flex;
  align-items: center;
  gap: 0.75rem 1rem;
  flex-wrap: wrap;
  min-width: 0;
  padding: 0.5rem 0.75rem;
}

.mg_album_title,
.mg_album_context {
  flex: 1 1 16rem;
  min-width: 0;
  height: auto;
  line-height: 1.3;
  padding: 0;
  overflow-wrap: anywhere;
}

.mg_search,
.mg_adminbox {
  float: none;
  display: block;
  height: auto;
  line-height: normal;
  margin: 0;
  min-width: 0;
}

.mg_search {
  flex: 1 1 18rem;
}

.mg_search form > div {
  display: flex;
  gap: 0.4rem;
  justify-content: flex-end;
  align-items: center;
  flex-wrap: wrap;
}

.mg_search input[type="search"],
.mg_search input[type="text"] {
  flex: 1 1 12rem;
  min-width: 8rem;
  max-width: 100%;
}

.mg_navbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  line-height: 1.4;
  padding: 0.45rem 0.6rem;
}

.mg_navbar a.button {
  display: inline-flex;
  align-items: center;
  min-height: 2.25rem;
  margin: 0;
  box-sizing: border-box;
}

.mg_right_nav {
  margin-left: auto;
}

.mg_album_description {
  max-width: 70rem;
  margin: 0.75rem auto;
  padding: 0 0.75rem;
  line-height: 1.6;
}

.mg_album_grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 11rem), 1fr));
  gap: 1rem;
  width: 100%;
  margin: 1rem 0;
  clear: both;
  align-items: stretch;
}

.mg_album_grid.mg-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-5 { grid-template-columns: repeat(5, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-6 { grid-template-columns: repeat(6, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-7 { grid-template-columns: repeat(7, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-8 { grid-template-columns: repeat(8, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-9 { grid-template-columns: repeat(9, minmax(0, 1fr)); }
.mg_album_grid.mg-cols-10 { grid-template-columns: repeat(10, minmax(0, 1fr)); }

.mg_album_cell {
  float: none;
  display: block;
  width: auto;
  min-width: 0;
  min-height: 0;
  margin: 0;
  text-align: center;
}

.mg_album_item,
.mg_media_item {
  height: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.mg_album_cell .mg_thumbnail {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  min-height: 0;
  margin: 0 0 0.65rem;
  position: static;
}

.mg_album_cell .mg_thumbnail_wrapper {
  position: static;
  width: 100%;
  min-width: 0;
}

.mg_album_cell .mg_thumbnail img,
.mg_media_detail img,
.mgFrame_default img.image,
.mgFrame_border img.image,
.mgFrame_mgAlbum img.image,
.mgFrame_mgShadow img.image,
.mgFrame_new_border img.image,
.mgFrame_new_shadow img.image,
.mgFrame_none img.image,
.mgFrame_shadow img.image {
  max-width: 100%;
  height: auto;
}

.mg_album_item_title,
.mg_album_cell .mg_title,
.mg_media_title {
  margin: 0.35rem 0;
  overflow-wrap: anywhere;
}

.mg_album_item_title,
.mg_album_cell .mg_title {
  font-size: 1rem;
  line-height: 1.35;
}

.mg_item_count {
  font-size: 0.9em;
  font-weight: normal;
}

.mg_media_title {
  text-align: center;
  font-size: clamp(1.35rem, 2vw + 0.7rem, 2rem);
  line-height: 1.25;
  margin: 1rem 0 0.75rem;
}

.mg_media_detail {
  max-width: 100%;
  overflow: hidden;
}

.mg_media_detail video,
.mg_media_detail audio,
.mg_media_detail iframe,
.mg_media_detail object,
.mg_media_detail embed {
  max-width: 100%;
}

.mg_info {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem 1rem;
  box-sizing: border-box;
}

.mg_info_left,
.mg_info_right,
.mg_info_center,
.mg_exif_info {
  float: none;
  width: auto;
  min-width: 0;
  box-sizing: border-box;
}

.mg_info_center,
.mg_exif_info {
  grid-column: 1 / -1;
}

.mg_exif_info {
  clear: both;
  margin: 0 0.5rem;
  overflow-x: auto;
}

.mg_jumpbox,
.mg_sortbox {
  white-space: normal;
}

.mg_jumpbox select,
.mg_sortbox select,
.mg_adminbox select {
  max-width: 100%;
}

@media (max-width: 64rem) {
  .mg_album_grid.mg-cols-5,
  .mg_album_grid.mg-cols-6,
  .mg_album_grid.mg-cols-7,
  .mg_album_grid.mg-cols-8,
  .mg_album_grid.mg-cols-9,
  .mg_album_grid.mg-cols-10 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 48rem) {
  .mg_album_grid.mg-cols-3,
  .mg_album_grid.mg-cols-4,
  .mg_album_grid.mg-cols-5,
  .mg_album_grid.mg-cols-6,
  .mg_album_grid.mg-cols-7,
  .mg_album_grid.mg-cols-8,
  .mg_album_grid.mg-cols-9,
  .mg_album_grid.mg-cols-10 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .mg_info {
    grid-template-columns: 1fr;
  }

  .mg_info_center,
  .mg_exif_info {
    grid-column: auto;
  }

  .mg_info_right,
  .mg_info_left,
  .mg_info_center {
    text-align: left;
  }
}

@media (max-width: 34rem) {
  .mg_album_grid,
  .mg_album_grid.mg-cols-2,
  .mg_album_grid.mg-cols-3,
  .mg_album_grid.mg-cols-4,
  .mg_album_grid.mg-cols-5,
  .mg_album_grid.mg-cols-6,
  .mg_album_grid.mg-cols-7,
  .mg_album_grid.mg-cols-8,
  .mg_album_grid.mg-cols-9,
  .mg_album_grid.mg-cols-10 {
    grid-template-columns: 1fr;
  }

  .mg_album_header,
  .mg_navbar {
    align-items: stretch;
  }

  .mg_search,
  .mg_search form > div,
  .mg_search input[type="search"],
  .mg_search input[type="text"],
  .mg_search input[type="submit"] {
    width: 100%;
  }

  .mg_navbar a.button {
    justify-content: center;
    flex: 1 1 calc(50% - 0.35rem);
  }

  .mg_right_nav {
    flex-basis: 100%;
    margin-left: 0;
    text-align: center;
  }
}
'''
p.write_text(text.rstrip() + css + '\n', encoding='utf-8')

# Roadmap: record the first responsive/semantic rendering milestone, but leave the global inline-style item open.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
marker = '- [ ] Review remaining inline presentation styles.\n'
addition = marker + '- [x] Modernize default album/search/media rendering with responsive CSS Grid/Flexbox, semantic media/card headings and responsive thumbnail frames.\n'
if text.count(marker) != 1:
    raise SystemExit('Roadmap inline-style marker mismatch')
p.write_text(text.replace(marker, addition, 1), encoding='utf-8')
