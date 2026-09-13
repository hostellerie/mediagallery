from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one %s marker in %s, found %d' % (label, path, count))
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


# Album editor: connect primary direct fields and format checkboxes to labels.
p = Path('templates/editalbum.thtml')
text = p.read_text(encoding='utf-8')
text = text.replace('<dt><label>{lang_title}</label></dt>\n      <dd><input type="text" name="album_name"', '<dt><label for="mg-album-name">{lang_title}</label></dt>\n      <dd><input type="text" id="mg-album-name" name="album_name"', 1)
text = text.replace('<dt><label>{lang_description}</label></dt>\n      <dd><textarea name="album_desc"', '<dt><label for="mg-album-desc">{lang_description}</label></dt>\n      <dd><textarea id="mg-album-desc" name="album_desc"', 1)
# Target the upload field only; the earlier thumbnail label refers to the existing thumbnail display.
text = text.replace('<dt><label>{lang_thumbnail}</label></dt>\n        <dd><input type="file" dir="ltr" name="thumbnail"', '<dt><label for="mg-album-thumbnail-upload">{lang_thumbnail}</label></dt>\n        <dd><input type="file" id="mg-album-thumbnail-upload" dir="ltr" name="thumbnail"', 1)
formats = [
    ('jpg', '1'), ('png', '2'), ('tif', '4'), ('gif', '8'), ('bmp', '16'), ('tga', '32'), ('psd', '64'),
    ('mp3', '128'), ('ogg', '256'), ('asf', '512'), ('swf', '1024'), ('mov', '2048'), ('mp4', '4096'),
    ('mpg', '8192'), ('flv', '131072'), ('rflv', '262144'), ('emb', '524288'), ('zip', '16384'), ('other', '32768')
]
for name, value in formats:
    old = '<input type="checkbox" name="format_%s" value="%s" {%s_checked}{xhtml}> <span>{lang_%s}</span>' % (name, value, name, name)
    new = '<input type="checkbox" id="mg-format-%s" name="format_%s" value="%s" {%s_checked}{xhtml}> <label for="mg-format-%s">{lang_%s}</label>' % (name, name, value, name, name, name)
    if text.count(old) != 1:
        raise SystemExit('format checkbox marker mismatch for %s' % name)
    text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

# Category editor: turn visible text into explicit labels.
p = Path('templates/editcategory.thtml')
text = p.read_text(encoding='utf-8')
text = text.replace('<dt>{lang_title}</dt>\n      <dd><input type="text" name="cat_name"', '<dt><label for="mg-category-name">{lang_title}</label></dt>\n      <dd><input type="text" id="mg-category-name" name="cat_name"', 1)
text = text.replace('<dt>{lang_description}</dt>\n      <dd><textarea name="cat_desc"', '<dt><label for="mg-category-desc">{lang_description}</label></dt>\n      <dd><textarea id="mg-category-desc" name="cat_desc"', 1)
p.write_text(text, encoding='utf-8')

# Batch progress: explicit labels plus function callback instead of string-eval timeout.
p = Path('templates/batch_progress.thtml')
text = p.read_text(encoding='utf-8')
text = text.replace('refresh = setTimeout("updateButton()", 1000);', 'refresh = setTimeout(updateButton, 1000);', 1)
text = text.replace('<td style="text-align:right;while-space:nowrap;">{L_REFRESH_RATE}: </td>\n    <td><input type="text" name="refresh_rate" value="{REFRESH_RATE}" size="5" style="texi-align:right"{xhtml}></td>', '<td style="text-align:right;white-space:nowrap;"><label for="mg-batch-refresh-rate">{L_REFRESH_RATE}</label>: </td>\n    <td><input type="text" id="mg-batch-refresh-rate" name="refresh_rate" value="{REFRESH_RATE}" size="5"{xhtml}></td>', 1)
text = text.replace('<td style="text-align:right;while-space:nowrap;">{L_ITEMS_PER_CYCLE}: </td>\n    <td><input type="text" name="item_limit" value="{ITEM_LIMIT}" size="5" style="texi-align:right"{xhtml}></td>', '<td style="text-align:right;white-space:nowrap;"><label for="mg-batch-item-limit">{L_ITEMS_PER_CYCLE}</label>: </td>\n    <td><input type="text" id="mg-batch-item-limit" name="item_limit" value="{ITEM_LIMIT}" size="5"{xhtml}></td>', 1)
text = text.replace('onclick="javascript:ticker=0"', 'onclick="ticker=0"', 1)
p.write_text(text, encoding='utf-8')

# Export tool: label both radio options and text fields explicitly without changing names/values.
p = Path('templates/export.thtml')
text = p.read_text(encoding='utf-8')
text = text.replace('<input type="radio" name="unix" value=0 />Windows&nbsp;&nbsp;\n        <input type="radio" name="unix" value=1>Unix', '<input type="radio" id="mg-export-windows" name="unix" value="0"> <label for="mg-export-windows">Windows</label>&nbsp;&nbsp;\n        <input type="radio" id="mg-export-unix" name="unix" value="1"> <label for="mg-export-unix">Unix</label>', 1)
text = text.replace('<input type="radio" name="moveorcopy" value=0 />Move&nbsp;&nbsp;\n        <input type="radio" name="moveorcopy" value=1>Copy', '<input type="radio" id="mg-export-move" name="moveorcopy" value="0"> <label for="mg-export-move">Move</label>&nbsp;&nbsp;\n        <input type="radio" id="mg-export-copy" name="moveorcopy" value="1"> <label for="mg-export-copy">Copy</label>', 1)
text = text.replace('Temp directory on dest system:\n      </td>\n      <td>\n        <input type="text" name="srcroot" size="40" value="">', '<label for="mg-export-srcroot">Temp directory on dest system:</label>\n      </td>\n      <td>\n        <input type="text" id="mg-export-srcroot" name="srcroot" size="40" value="">', 1)
text = text.replace('Base Directory:\n      </td>\n      <td>\n        <input type="text" name="destroot" size="40" value="">', '<label for="mg-export-destroot">Base Directory:</label>\n      </td>\n      <td>\n        <input type="text" id="mg-export-destroot" name="destroot" size="40" value="">', 1)
p.write_text(text, encoding='utf-8')

# User quota editor: explicit association; generated active control is left to its producer.
p = Path('templates/useredit.thtml')
text = p.read_text(encoding='utf-8')
text = text.replace('<td class="mg_alignright" width="40%">{lang_quota}</td>\n      <td>\n        <input type="text" maxlength="4" size="4" name="quota"', '<td class="mg_alignright" width="40%"><label for="mg-user-quota">{lang_quota}</label></td>\n      <td>\n        <input type="text" id="mg-user-quota" maxlength="4" size="4" name="quota"', 1)
p.write_text(text, encoding='utf-8')

# Record focused progress without declaring the broad audit complete yet.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
needle = '- [ ] Review keyboard accessibility and form labeling across remaining admin/public templates.\n'
addition = needle + '  - [x] Connect primary album/category, batch, export and user-quota controls to explicit labels; retain already-valid implicit FTP radio labels.\n  - [ ] Resolve remaining generated-control/global-management labeling together with obsolete playback-control cleanup.\n'
if text.count(needle) != 1:
    raise SystemExit('ROADMAP accessibility marker mismatch')
p.write_text(text.replace(needle, addition, 1), encoding='utf-8')
