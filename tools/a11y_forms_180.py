from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit('Missing marker: ' + label)
    return text.replace(old, new, 1)

# Browser upload: bind labels to each slot's native controls. Keep names and
# array indexes unchanged so server-side slot handling is unaffected.
p = Path('templates/userupload.thtml')
text = p.read_text(encoding='utf-8')
for slot in range(4):
    fields = [
        ('{lang_file}', 'newmedia[%d]' % slot, 'file'),
        ('{lang_do_not_convert_orig}', 'dnc[%d]' % slot, 'dnc'),
        ('{lang_caption}', 'caption[%d]' % slot, 'caption'),
        ('{lang_description}', 'description[%d]' % slot, 'description'),
        ('{lang_keywords}', 'keywords[%d]' % slot, 'keywords'),
    ]
    for lang, name, suffix in fields:
        control_id = 'mg-upload-%s-%d' % (suffix, slot + 1)
        text = replace_once(text, '<dt><label>%s</label></dt>' % lang,
                            '<dt><label for="%s">%s</label></dt>' % (control_id, lang),
                            'userupload label %s %d' % (suffix, slot))
        if name.startswith('description'):
            text = replace_once(text, '<textarea name="%s"' % name,
                                '<textarea id="%s" name="%s"' % (control_id, name),
                                'userupload control %s %d' % (suffix, slot))
        else:
            text = replace_once(text, 'name="%s"' % name,
                                'id="%s" name="%s"' % (control_id, name),
                                'userupload control %s %d' % (suffix, slot))

    attach_id = 'mg-upload-attachtn-%d' % (slot + 1)
    thumb_id = 'mg-upload-thumbnail-%d' % (slot + 1)
    text = replace_once(text, '<dt><label>{lang_attached_tn}</label></dt>',
                        '<dt><label for="%s">{lang_attached_tn}</label></dt>' % attach_id,
                        'userupload attached label %d' % slot)
    text = replace_once(text, 'name="attachtn[%d]"' % slot,
                        'id="%s" name="attachtn[%d]"' % (attach_id, slot),
                        'userupload attach control %d' % slot)
    text = replace_once(text, 'name="thumbnail[%d]"' % slot,
                        'id="%s" name="thumbnail[%d]" aria-label="{lang_attached_tn}"' % (thumb_id, slot),
                        'userupload thumbnail control %d' % slot)

p.write_text(text, encoding='utf-8')

# Remote upload: repeated array names are intentionally retained. IDs are
# unique per fieldset and formControl() continues to address controls by name.
p = Path('templates/remoteupload.thtml')
text = p.read_text(encoding='utf-8')
for slot in range(1, 5):
    controls = [
        ('{lang_remote_media_type}', '<select name="type[]"', '<select id="mg-remote-type-%d" name="type[]"' % slot, 'type'),
        ('{lang_thumbnail}', '<input type="file" name="thumbnail[]"', '<input type="file" id="mg-remote-thumbnail-%d" name="thumbnail[]"' % slot, 'thumbnail'),
        ('{lang_remote_url}', '<textarea name="remoteurl[]"', '<textarea id="mg-remote-url-%d" name="remoteurl[]"' % slot, 'url'),
        ('{lang_width}', '<input type="text" name="width[]"', '<input type="text" id="mg-remote-width-%d" name="width[]"' % slot, 'width'),
        ('{lang_height}', '<input type="text" name="height[]"', '<input type="text" id="mg-remote-height-%d" name="height[]"' % slot, 'height'),
        ('{lang_caption}', '<input type="text" name="caption[]"', '<input type="text" id="mg-remote-caption-%d" name="caption[]"' % slot, 'caption'),
        ('{lang_description}', '<textarea name="description[]"', '<textarea id="mg-remote-description-%d" name="description[]"' % slot, 'description'),
        ('{lang_keywords}', '<input type="text" name="keywords[]"', '<input type="text" id="mg-remote-keywords-%d" name="keywords[]"' % slot, 'keywords'),
    ]
    for lang, old_control, new_control, suffix in controls:
        control_id = 'mg-remote-%s-%d' % (suffix, slot)
        text = replace_once(text, '<dt><label>%s</label></dt>' % lang,
                            '<dt><label for="%s">%s</label></dt>' % (control_id, lang),
                            'remote label %s %d' % (suffix, slot))
        text = replace_once(text, old_control, new_control,
                            'remote control %s %d' % (suffix, slot))
p.write_text(text, encoding='utf-8')

# Media edit already has stable IDs; connect its visible labels to them.
p = Path('templates/mediaedit.thtml')
text = p.read_text(encoding='utf-8')
labels = [
    ('{lang_original_filename}', 'original_filename'),
    ('{lang_attached_thumbnail}', 'attachtn'),
    ('{lang_replacefile}', 'replacefile'),
    ('{lang_remote_url}', 'remoteurl'),
    ('{lang_title}', 'media_title'),
    ('{description}', 'media_desc'),
    ('{lang_keywords}', 'media_keywords'),
    ('{lang_artist}', 'artist'),
    ('{lang_music_album}', 'musicalbum'),
    ('{lang_genre}', 'genre'),
]
for lang, control_id in labels:
    text = replace_once(text, '<dt><label>%s</label></dt>' % lang,
                        '<dt><label for="%s">%s</label></dt>' % (control_id, lang),
                        'mediaedit label ' + control_id)
p.write_text(text, encoding='utf-8')
