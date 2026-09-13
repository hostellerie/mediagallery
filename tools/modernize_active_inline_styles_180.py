from pathlib import Path

# Remove templates that became unreachable when the proprietary playback option
# panels were retired. Keeping them only inflates the theme surface and audit noise.
for dead in [
    'templates/edit_mp3_options.thtml',
    'templates/edit_flv_options.thtml',
    'templates/edit_swf_options.thtml',
]:
    p = Path(dead)
    if p.exists():
        p.unlink()

# Featured album: presentation table -> semantic responsive grid.
Path('templates/cb_featured_album.thtml').write_text('''<section class="mg-featured-album">\n  <h2>{featured_album}</h2>\n  <div class="mg-featured-album-grid">\n    <div class="mg-featured-album-thumb" style="max-width:{column_width}px;">\n      {media_item_thumbnail}\n    </div>\n    <div class="mg-featured-album-summary">\n      <p class="mg-featured-album-line"><strong>{album_title}</strong> ({subalbum_media_count})</p>\n      <div class="mg-featured-album-description">{album_desc}</div>\n      <p class="mg-featured-album-line"><strong>{updated_prompt}</strong> {album_last_update}</p>\n    </div>\n    <div class="mg-featured-album-subalbums">\n      <p class="mg-featured-album-line"><strong>{lang_subalbums}</strong> {subalbumcount}</p>\n      <div class="mg-featured-album-list">{saulstart}{subalbumlist}{saulend}</div>\n    </div>\n  </div>\n</section>\n''', encoding='utf-8')

# Podcast album cells: remove float/clear presentation styles.
for path in ['templates/themes/podcast/album_page_album_cell.thtml', 'templates/themes/podcast/album_page_body_album_cell_1.thtml']:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    text = text.replace('<div class="mgPluginMI" style="float:left;padding-right:3px;">{media_item_thumbnail}</div>\n{album_desc}\n<div style="clear:both;"></div>', '<div class="mg-podcast-album-summary">\n  <div class="mgPluginMI mg-podcast-album-thumb">{media_item_thumbnail}</div>\n  <div class="mg-podcast-album-description">{album_desc}</div>\n</div>')
    text = text.replace('<span style="font-weight:bold;">{lang_subalbums}</span>', '<strong>{lang_subalbums}</strong>')
    text = text.replace('\n<div style="clear:both;"></div>\n{# end', '\n{# end')
    p.write_text(text, encoding='utf-8')

# Podcast media cells: presentation table -> responsive grid, static styles -> classes.
podcast_media = '''{# begin {templatelocation} #}\n<a name="{media_id}"></a>\n<h1 class="mg-podcast-media-title">{media_title}</h1>\n<h2 class="mg-podcast-media-subtitle">{musicalbum} {lang_hyphen} {artist}</h2>\n<div class="pluginSmallText">\n {lang_published} {media_owner} {lang_on} {media_time}\n</div>\n{!if media_cell_keywords}\n<div class="pluginMediumText">{media_cell_keywords}</div>\n{!endif}\n<div class="mg-podcast-media-layout">\n  <div class="mg-podcast-media-aside">\n    <div class="mgPluginMI mg-podcast-media-thumb">{media_item_thumbnail}</div>\n    <div class="pluginItemFooter">\n      {!if media_comments}\n      <div class="pluginMediumText">{media_comments}</div>\n      {!endif}\n      {!if media_views}\n      <div class="pluginMediumText">{media_views}</div>\n      {!endif}\n      {!if rating_box}\n      {rating_box}\n      {!endif}\n      {!if alt_edit_link}\n      <div class="pluginSmallText">{alt_edit_link}</div>\n      {!endif}\n    </div>\n  </div>\n  <div class="mg-podcast-media-description"><p>{media_description}</p></div>\n</div>\n{mp3_podcast}\n<hr{xhtml}>\n{# end {templatelocation} #}\n'''
for path in ['templates/themes/podcast/album_page_media_cell.thtml', 'templates/themes/podcast/album_page_body_media_cell_1.thtml']:
    Path(path).write_text(podcast_media, encoding='utf-8')

# Active admin templates: migrate repeated static presentation into stylesheet classes.
replacements = {
    'templates/mediaitems.thtml': {
        ' style="text-align:left;"': ' class="mg-text-left"',
        ' style="text-align:center;"': ' class="mg-text-center"',
        ' style="vertical-align:middle;text-align:center;"': ' class="mg-valign-middle mg-text-center"',
        ' style="vertical-align:middle;"': ' class="mg-valign-middle"',
        '<div style="margin:4px 2px 0">': '<div class="mg-media-manager-field">',
        ' style="width:80%;"': ' class="mg-media-manager-input"',
        ' style="width:96%;"': ' class="mg-media-manager-textarea"',
        '<div style="margin:4px 2px;">': '<div class="mg-media-manager-category">',
        '<div style="margin-top:5px">': '<div class="mg-admin-action-row">',
    },
    'templates/batch_progress.thtml': {
        '<div class="pluginRow1" style="padding:10px;">': '<div class="pluginRow1 mg-batch-panel">',
        '<div style="margin-left:20px">': '<div class="mg-batch-body">',
        ' style="text-align:right;while-space:nowrap;width:220px"': ' class="mg-batch-label mg-batch-label-wide"',
        ' style="text-align:right;while-space:nowrap;"': ' class="mg-batch-label"',
        ' style="text-align:right;white-space:nowrap;"': ' class="mg-batch-label"',
    },
    'templates/global_album_attr.thtml': {
        '<div class="mg_navbar" style="text-align:center;">': '<div class="mg_navbar mg-text-center">',
        ' style="margin:0px auto;"': ' class="mg-table-centered"',
        ' style="text-align:center"': ' class="mg-text-center"',
        ' style="width:auto"': ' class="mg-table-auto"',
    },
    'templates/global_album_perm.thtml': {
        '<div style="clear:both;">{permissions_editor}</div>': '<div class="mg-clear">{permissions_editor}</div>',
        '<div style="text-align:center;margin-top:10px">': '<div class="mg-admin-submit-row">',
    },
    'templates/createmembers.thtml': {
        ' style="width:50px;"': ' class="mg-select-column"',
        '<div style="margin-top:5px;">': '<div class="mg-admin-action-row">',
        '<div style="text-align:center;">': '<div class="mg-text-center">',
    },
    'templates/purgealbums.thtml': {
        ' style="width:50px;"': ' class="mg-select-column"',
    },
    'templates/sessions.thtml': {
        ' style="width:50px"': ' class="mg-select-column"',
    },
    'templates/mediamanage.thtml': {
        '<div style="text-align:center;margin-top:10px">': '<div class="mg-admin-submit-row">',
    },
}
for path, mapping in replacements.items():
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    for old, new in mapping.items():
        text = text.replace(old, new)
    p.write_text(text, encoding='utf-8')

# Add reusable responsive styles to the plugin stylesheet.
p = Path('public_html/style.css')
css = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 inline-presentation cleanup */'
if marker not in css:
    css += '''\n\n/* MediaGallery 1.8 inline-presentation cleanup */\n.mg-text-center { text-align: center; }\n.mg-text-left { text-align: left; }\n.mg-valign-middle { vertical-align: middle; }\n.mg-clear { clear: both; }\n.mg-table-centered { margin-left: auto; margin-right: auto; }\n.mg-table-auto { width: auto; }\n.mg-select-column { width: 3.125rem; }\n\n.mg-admin-action-row {\n  display: flex;\n  align-items: center;\n  gap: 0.5rem;\n  flex-wrap: wrap;\n  margin-top: 0.5rem;\n}\n\n.mg-admin-submit-row {\n  display: flex;\n  justify-content: center;\n  gap: 0.5rem;\n  flex-wrap: wrap;\n  margin-top: 0.625rem;\n}\n\n.mg-media-manager-field,\n.mg-media-manager-category { margin: 0.25rem 0.125rem; }\n.mg-media-manager-input { width: min(100%, 34rem); }\n.mg-media-manager-textarea { width: 100%; max-width: 42rem; box-sizing: border-box; }\n\n.mg-batch-panel { padding: 0.625rem; }\n.mg-batch-body { margin-left: 1.25rem; }\n.mg-batch-label { text-align: right; white-space: nowrap; }\n.mg-batch-label-wide { width: 13.75rem; }\n\n.mg-featured-album { margin: 1.25rem 0.625rem; }\n.mg-featured-album-grid {\n  display: grid;\n  grid-template-columns: minmax(8rem, auto) minmax(12rem, 1fr) minmax(12rem, 1fr);\n  gap: 1rem;\n  align-items: start;\n  width: 100%;\n}\n.mg-featured-album-thumb { width: 100%; text-align: center; }\n.mg-featured-album-thumb img { max-width: 100%; height: auto; }\n.mg-featured-album-summary,\n.mg-featured-album-subalbums { min-width: 0; }\n.mg-featured-album-line,\n.mg-featured-album-description,\n.mg-featured-album-list { margin: 0.625rem 0; }\n\n.mg-podcast-album-summary,\n.mg-podcast-media-layout {\n  display: grid;\n  grid-template-columns: minmax(8rem, auto) minmax(0, 1fr);\n  gap: 1rem;\n  align-items: start;\n}\n.mg-podcast-album-thumb,\n.mg-podcast-media-thumb { padding: 0.3125rem 0.1875rem 0 0; }\n.mg-podcast-album-thumb img,\n.mg-podcast-media-thumb img { max-width: 100%; height: auto; }\n.mg-podcast-media-title { margin-bottom: 0; padding-bottom: 0; }\n.mg-podcast-media-subtitle { margin: 0.125rem 0; padding: 0 0 0.125rem; }\n.mg-podcast-media-description { min-width: 0; }\n\n@media (max-width: 48rem) {\n  .mg-featured-album-grid { grid-template-columns: minmax(8rem, 14rem) 1fr; }\n  .mg-featured-album-subalbums { grid-column: 1 / -1; }\n  .mg-batch-body { margin-left: 0; }\n  .mg-batch-label, .mg-batch-label-wide { width: auto; white-space: normal; text-align: left; }\n}\n\n@media (max-width: 34rem) {\n  .mg-featured-album-grid,\n  .mg-podcast-album-summary,\n  .mg-podcast-media-layout { grid-template-columns: 1fr; }\n  .mg-featured-album-thumb { max-width: 100% !important; }\n  .mg-podcast-album-thumb,\n  .mg-podcast-media-thumb { padding-right: 0; text-align: center; }\n  .mg-admin-action-row > select,\n  .mg-admin-action-row > input[type="submit"] { max-width: 100%; }\n}\n'''
p.write_text(css, encoding='utf-8')

# Record progress but do not close the full review until the residual inventory is classified.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
needle = '- [ ] Review remaining inline presentation styles.\n'
if needle in text and 'Remove dead playback templates' not in text:
    text = text.replace(needle, needle + '  - [x] Remove dead playback templates and migrate the largest active public/admin static style clusters to responsive CSS.\n  - [ ] Classify and resolve the residual inline-style inventory; retain only justified runtime dimensions.\n', 1)
p.write_text(text, encoding='utf-8')
