from pathlib import Path


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit('Expected one marker for %s, found %d' % (label, text.count(old)))
    return text.replace(old, new, 1)

# Media property URLs are internal, but they belong to href attributes. Escape
# them once in the producer and keep them out of JavaScript string literals.
p = Path('include/lib-media.php')
text = p.read_text(encoding='utf-8')
text = replace_once(text,
    "        'property'            => $property,",
    "        'property'            => MG_escapeHTML($property),",
    'media property URL')
p.write_text(text, encoding='utf-8')

# The three maintained media detail templates share the same navigation. Use a
# real property href and let popitup() consume this.href. Also propagate the
# dedicated slideshow onclick attribute introduced for lightbox mode.
for name in ('view_image.thtml', 'view_audio.thtml', 'view_video.thtml'):
    p = Path('templates') / name
    text = p.read_text(encoding='utf-8')
    text = replace_once(text,
        '<a class="button" href="{url_slideshow}">{lang_slideshow}</a>',
        '<a class="button" href="{url_slideshow}"{slideshow_onclick}>{lang_slideshow}</a>',
        name + ' slideshow action')
    text = replace_once(text,
        '<a class="button" href="#" onclick="return popitup(\'{property}\')">{lang_property}</a>',
        '<a class="button" href="{property}" onclick="return popitup(this.href)">{lang_property}</a>',
        name + ' property action')
    text = replace_once(text,
        "    newwindow=window.open(url,'name','height=600,width=450,resizable=yes,toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes');",
        "    var newwindow = window.open(url,'name','height=600,width=450,resizable=yes,toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=yes');",
        name + ' popup variable')
    p.write_text(text, encoding='utf-8')

# Record the completed removal of dynamic values from inline property JavaScript.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
marker = '- [x] Escape editable album/category values and generated admin option labels when rendering form controls.\n'
addition = marker + '- [x] Remove dynamic property URLs from inline JavaScript and preserve lightbox slideshow actions on media detail views.\n'
text = replace_once(text, marker, addition, 'roadmap media view cleanup')
p.write_text(text, encoding='utf-8')
