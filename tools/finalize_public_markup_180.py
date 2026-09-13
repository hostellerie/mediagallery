from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit('%s marker missing in %s' % (label, path))
    text = text.replace(old, new, 1)
    p.write_text(text, encoding='utf-8')

# Podcast album cells are repeated inside a page that already owns the H1.
for path in [
    'templates/themes/podcast/album_page_album_cell.thtml',
    'templates/themes/podcast/album_page_body_album_cell_1.thtml',
]:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    text = text.replace('<h1>{lang_album} {album_title}</h1>', '<h2 class="mg-podcast-card-title">{lang_album} {album_title}</h2>', 1)
    p.write_text(text, encoding='utf-8')

for path in [
    'templates/themes/podcast/album_page_media_cell.thtml',
    'templates/themes/podcast/album_page_body_media_cell_1.thtml',
]:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    text = text.replace('<a name="{media_id}"></a>\n', '<span id="{media_id}" class="mg-anchor-target" aria-hidden="true"></span>\n', 1)
    text = text.replace('<h1>{media_title}</h1>', '<h2 class="mg-podcast-card-title">{media_title}</h2>', 1)
    text = text.replace('<h2>{musicalbum} {lang_hyphen} {artist}</h2>', '<h3 class="mg-podcast-card-subtitle">{musicalbum} {lang_hyphen} {artist}</h3>', 1)
    p.write_text(text, encoding='utf-8')

# Public member-album enrollment: remove the layout table and BR-driven spacing.
p = Path('templates/enroll.thtml')
text = p.read_text(encoding='utf-8')
old = '''<div class="plugin">\n<table width="100%" border="0" align="left">\n  <tr class="pluginCellTitle">\n    <td><span class="mg-fw-bold">{lang_title}</span></td>\n  </tr>\n</table>\n<br{xhtml}>\n<form name="enroll" method="post" action="{s_form_action}" class="uk-form">\n<br{xhtml}>\n<span class="mg-fw-bold">{lang_overview}</span><br{xhtml}>\n{lang_member_album_overview}\n<br{xhtml}>\n<br{xhtml}>\n<span class="mg-fw-bold">{lang_terms}</span><br{xhtml}>\n{lang_member_album_terms}\n<br{xhtml}><br{xhtml}>\n<div class="mg_submit_center">\n  <input type="submit" value="{lang_agree}"  name="mode"{xhtml}>\n  <input type="submit" value="{lang_cancel}" name="mode"{xhtml}>\n</div>\n</form>\n<br{xhtml}><br{xhtml}>\n</div>'''
new = '''<section class="plugin mg-enroll">\n  <header class="mg-enroll-header">\n    <h1 class="mg-enroll-title">{lang_title}</h1>\n  </header>\n  <form name="enroll" method="post" action="{s_form_action}" class="uk-form">\n    <section class="mg-enroll-section">\n      <h2>{lang_overview}</h2>\n      <div>{lang_member_album_overview}</div>\n    </section>\n    <section class="mg-enroll-section">\n      <h2>{lang_terms}</h2>\n      <div>{lang_member_album_terms}</div>\n    </section>\n    <div class="mg_submit_center">\n      <input type="submit" value="{lang_agree}" name="mode"{xhtml}>\n      <input type="submit" value="{lang_cancel}" name="mode"{xhtml}>\n    </div>\n  </form>\n</section>'''
if old not in text:
    raise SystemExit('enroll markup marker missing')
p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Watermark popup image is decorative; give it an explicit empty alt.
p = Path('templates/wm_manage.thtml')
text = p.read_text(encoding='utf-8')
old = '<img src="\'+imgpath+\'" class="mg-mb-half-em">'
new = '<img src="\'+imgpath+\'" alt="" class="mg-mb-half-em">'
if old not in text:
    raise SystemExit('watermark popup image marker missing')
p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Shared responsive styling.
p = Path('public_html/style.css')
css = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 final public semantic markup */'
if marker not in css:
    css += '''\n\n/* MediaGallery 1.8 final public semantic markup */\n.mg-anchor-target {\n  display: block;\n  position: relative;\n  top: -0.5rem;\n  visibility: hidden;\n}\n\n.mg-podcast-card-title {\n  margin: 0 0 0.25rem;\n  font-size: clamp(1.1rem, 1.5vw + 0.75rem, 1.5rem);\n  line-height: 1.3;\n  overflow-wrap: anywhere;\n}\n\n.mg-podcast-card-subtitle {\n  margin: 0 0 0.5rem;\n  font-size: 1rem;\n  line-height: 1.4;\n  font-weight: normal;\n  overflow-wrap: anywhere;\n}\n\n.mg-enroll {\n  max-width: 60rem;\n  margin: 0 auto;\n}\n\n.mg-enroll-header {\n  margin-bottom: 1rem;\n}\n\n.mg-enroll-title {\n  margin: 0;\n  line-height: 1.25;\n}\n\n.mg-enroll-section {\n  margin: 0 0 1.5rem;\n}\n\n.mg-enroll-section h2 {\n  margin: 0 0 0.5rem;\n  font-size: 1.2rem;\n}\n'''
p.write_text(css, encoding='utf-8')

# Record the final public-markup pass in the roadmap.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
needle = '- [x] Modernize bundled file-list, podcast, jQuery gallery and SimpleViewer skins for responsive layouts and semantic album headings.\n'
addition = needle + '- [x] Complete final public markup audit: one H1 per Podcast page, semantic repeated-card headings, non-link anchors and table-free member enrollment.\n'
if 'Complete final public markup audit:' not in text:
    if needle not in text:
        raise SystemExit('roadmap insertion marker missing')
    text = text.replace(needle, addition, 1)
p.write_text(text, encoding='utf-8')
