from pathlib import Path

# Producer-side IDs/labels for generated controls.
p = Path('include/mediamanage.php')
text = p.read_text(encoding='utf-8')
text = text.replace('$album_selectbox = \'<select name="album">\';', '$album_selectbox = \'<select id="mg-media-destination-album" name="album">\';', 1)
text = text.replace('$batchOptionSelect = \'<select name="batchOption">\';', '$batchOptionSelect = \'<select id="mg-media-batch-option" name="batchOption">\';', 1)
text = text.replace("$radio_box = '<input type=\"radio\" name=\"cover\" value=\"'\n                               . $row['media_id'] . '\"' . $checked . XHTML . '>';", "$radio_box = '<input type=\"radio\" name=\"cover\" value=\"'\n                               . $row['media_id'] . '\" aria-label=\"' . MG_escapeHTML($LANG_MG01['cover']) . '\"'\n                               . $checked . XHTML . '>';", 1)
text = text.replace("$include_ss = '<input type=\"checkbox\" name=\"ss[' . $counter . ']\" value=\"1\"'\n                                . $checked . XHTML . '>';", "$include_ss = '<input type=\"checkbox\" name=\"ss[' . $counter . ']\" value=\"1\" aria-label=\"'\n                                . MG_escapeHTML($LANG_MG01['include_ss']) . '\"' . $checked . XHTML . '>';", 1)
text = text.replace("$cat_select = '<select name=\"cat_id[]\">';", "$cat_select = '<select id=\"mg-media-category-' . $counter . '\" name=\"cat_id[]\" aria-label=\"'\n                            . MG_escapeHTML($LANG_MG01['category']) . '\">';", 1)
p.write_text(text, encoding='utf-8')

# Template-side unique ids, labels and table semantics.
p = Path('templates/mediaitems.thtml')
text = p.read_text(encoding='utf-8')
for old, new in [
    ('<th>{lang_select}</th>', '<th scope="col">{lang_select}</th>'),
    ('<th>{lang_item}</th>', '<th scope="col">{lang_item}</th>'),
    ('<th>{lang_watermarked}</th>', '<th scope="col">{lang_watermarked}</th>'),
    ('<th>{lang_order}</th>', '<th scope="col">{lang_order}</th>'),
    ('<th>{lang_cover}</th>', '<th scope="col">{lang_cover}</th>'),
    ('<th>{lang_include_ss}</th>', '<th scope="col">{lang_include_ss}</th>'),
    ('<th style="text-align:left;">{lang_title}/{lang_description}/{lang_keywords}</th>', '<th scope="col" style="text-align:left;">{lang_title}/{lang_description}/{lang_keywords}</th>'),
]:
    text = text.replace(old, new, 1)
text = text.replace('<input type="radio" name="cover" value="-2"{val_reset_cover}{xhtml}>&nbsp;&nbsp;{lang_reset_cover}', '<input type="radio" id="mg-reset-cover" name="cover" value="-2"{val_reset_cover}{xhtml}>&nbsp;&nbsp;<label for="mg-reset-cover">{lang_reset_cover}</label>', 1)
text = text.replace('<input type="checkbox" name="sel[]" value="{mid}"{xhtml}>', '<input type="checkbox" id="mg-media-select-{counter}" name="sel[]" value="{mid}" aria-label="{lang_select}"{xhtml}>', 1)
text = text.replace('<img src="{u_thumbnail}" height="{height}" width="{width}" alt=""{xhtml}>', '<img src="{u_thumbnail}" height="{height}" width="{width}" alt="{media_title}" loading="lazy" decoding="async"{xhtml}>', 1)
text = text.replace('<input type="text" name="seq[]" value="{order}" size="3"{xhtml}>', '<input type="number" id="mg-media-order-{counter}" name="seq[]" value="{order}" size="3" inputmode="numeric" aria-label="{lang_order}"{xhtml}>', 1)
text = text.replace('<div style="margin:4px 2px 0"><input type="text" name="mtitle[]" value="{media_title}" size="30" style="width:80%;"{xhtml}></div>', '<div style="margin:4px 2px 0"><label for="mg-media-title-{counter}">{lang_title}</label><br{xhtml}><input type="text" id="mg-media-title-{counter}" name="mtitle[]" value="{media_title}" size="30" style="width:80%;"{xhtml}></div>', 1)
text = text.replace('<textarea name="mdesc[]" cols="40" rows="2" style="width:96%;">{media_desc}</textarea><br{xhtml}>', '<label for="mg-media-desc-{counter}">{lang_description}</label><br{xhtml}><textarea id="mg-media-desc-{counter}" name="mdesc[]" cols="40" rows="2" style="width:96%;">{media_desc}</textarea><br{xhtml}>', 1)
text = text.replace('<div style="margin:4px 2px 0"><input type="text" name="mkeywords[]" value="{media_keywords}" size="30" style="width:80%;"{xhtml}></div>', '<div style="margin:4px 2px 0"><label for="mg-media-keywords-{counter}">{lang_keywords}</label><br{xhtml}><input type="text" id="mg-media-keywords-{counter}" name="mkeywords[]" value="{media_keywords}" size="30" style="width:80%;"{xhtml}></div>', 1)
text = text.replace('<div style="margin:4px 2px;">{lang_category}:&nbsp;{cat_select}</div>', '<div style="margin:4px 2px;"><label for="mg-media-category-{counter}">{lang_category}</label>:&nbsp;{cat_select}</div>', 1)
text = text.replace('onclick="javascript:doCheckAll_mediaitems()"', 'onclick="doCheckAll_mediaitems()"', 1)
text = text.replace('onclick="javascript:doUnCheckAll_mediaitems()"', 'onclick="doUnCheckAll_mediaitems()"', 1)
text = text.replace('{lang_albumsel}&nbsp;&nbsp;{albumselect}', '<label for="mg-media-destination-album">{lang_albumsel}</label>&nbsp;&nbsp;{albumselect}', 1)
text = text.replace('{lang_batch_options}&nbsp;&nbsp;{batchoptionselect}', '<label for="mg-media-batch-option">{lang_batch_options}</label>&nbsp;&nbsp;{batchoptionselect}', 1)
p.write_text(text, encoding='utf-8')

# Roadmap progress.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
needle = '  - [ ] Resolve remaining generated-control/global-management labeling.\n'
replacement = '  - [x] Label generated media-manager controls, row fields, destination album and batch-action selectors without changing array bindings.\n  - [ ] Resolve remaining global album-management and maintenance-form labeling.\n'
if text.count(needle) != 1:
    raise SystemExit('ROADMAP generated-control marker mismatch')
p.write_text(text.replace(needle, replacement, 1), encoding='utf-8')
