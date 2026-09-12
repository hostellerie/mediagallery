from pathlib import Path
import re


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit('Expected one marker for %s, found %d' % (label, text.count(old)))
    return text.replace(old, new, 1)

# Central HTML escaping helper. Keep double_encode disabled so historical
# entities already stored by MediaGallery are not encoded a second time.
p = Path('include/common.php')
text = p.read_text(encoding='utf-8')
marker = "function MG_getRemoteAddress()\n{\n    return isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';\n}\n"
helper = "function MG_escapeHTML($value)\n{\n    return htmlspecialchars((string) $value, ENT_QUOTES, COM_getCharset(), false);\n}\n\n" + marker
text = replace_once(text, marker, helper, 'MG_escapeHTML insertion')

# Frame rendering: all shipped frame variants consume these variables in HTML
# attributes, so escape once here instead of duplicating logic in every frame.
old = """    if ($media_link_start === null) $media_link_start = '<a href=\"' . $u_pic . '\">';
    if ($media_link_end   === null) $media_link_end   = '</a>';
"""
new = """    $u_pic_attr = MG_escapeHTML($u_pic);
    $u_image_attr = MG_escapeHTML($u_image);
    $media_tag = (isset($title) && $title != ' ') ? MG_escapeHTML(strip_tags($title)) : '';

    if ($media_link_start === null) $media_link_start = '<a href=\"' . $u_pic_attr . '\">';
    if ($media_link_end   === null) $media_link_end   = '</a>';
"""
text = replace_once(text, old, new, 'MG_getFramedImage preamble')
text = replace_once(text, "        'url_media_item'   => $u_pic,\n", "        'url_media_item'   => $u_pic_attr,\n", 'frame media item URL')
text = replace_once(text, "        'url_display_item' => $u_pic,\n", "        'url_display_item' => $u_pic_attr,\n", 'frame display URL')
text = replace_once(text, "        'media_thumbnail'  => $u_image,\n", "        'media_thumbnail'  => $u_image_attr,\n", 'frame thumbnail URL')
text = replace_once(text, "        'media_tag'        => (isset($title) && $title != ' ') ? strip_tags($title) : '',\n", "        'media_tag'        => $media_tag,\n", 'frame media tag')
p.write_text(text, encoding='utf-8')

# Media thumbnails and lightbox attributes.
p = Path('include/classMedia.php')
text = p.read_text(encoding='utf-8')
text, count = re.subn(r"('media_tag'\s*=>\s*)strip_tags\(\$this->title\)", r"\1MG_escapeHTML(strip_tags($this->title))", text)
if count < 1:
    raise SystemExit('No Media::displayThumb media_tag occurrence found')

old = "$caption = PLG_replaceTags(str_replace('$', '&#36;', $this->title));"
if old in text:
    text = text.replace(old, "$caption = MG_escapeHTML(strip_tags(PLG_replaceTags(str_replace('$', '&#36;', $this->title))));")
else:
    # Some branches may not retain the dollar-sign compatibility transform.
    old2 = "$caption = PLG_replaceTags($this->title);"
    if old2 not in text:
        raise SystemExit('Lightbox caption assignment not found')
    text = text.replace(old2, "$caption = MG_escapeHTML(strip_tags(PLG_replaceTags($this->title)));", 1)

text, hrefdirect_count = re.subn(r"('hrefdirect'\s*=>\s*)\$hrefdirect", r"\1MG_escapeHTML($hrefdirect)", text)
text, href_count = re.subn(r"('href'\s*=>\s*)\$url_media_item", r"\1MG_escapeHTML($url_media_item)", text)
if hrefdirect_count < 1 or href_count < 1:
    raise SystemExit('Lightbox href mappings not found')
p.write_text(text, encoding='utf-8')

# Media manager/edit output. These values are placed in src/href/value/textarea
# contexts by maintained templates.
p = Path('include/mediamanage.php')
text = p.read_text(encoding='utf-8')
text = text.replace(". $catRow[$i]['cat_name'] . '</option>';", ". MG_escapeHTML($catRow[$i]['cat_name']) . '</option>';")
text = text.replace("$media_zoom = '<a href=\"' . $object[4] . '\">';", "$media_zoom = '<a href=\"' . MG_escapeHTML($object[4]) . '\">';")
manager_repls = {
    "'u_thumbnail'       => $thumbnail,": "'u_thumbnail'       => MG_escapeHTML($thumbnail),",
    "'media_title'       => $row['media_title'],": "'media_title'       => MG_escapeHTML($row['media_title']),",
    "'media_desc'        => $row['media_desc'],": "'media_desc'        => MG_escapeHTML($row['media_desc']),",
    "'media_keywords'    => $row['media_keywords'],": "'media_keywords'    => MG_escapeHTML($row['media_keywords']),",
    "'media_edit'        => $media_edit,": "'media_edit'        => MG_escapeHTML($media_edit),",
}
for old, new in manager_repls.items():
    if old not in text:
        raise SystemExit('Missing manager mapping: ' + old)
    text = text.replace(old, new)

edit_repls = {
    "'original_filename' => $row['media_original_filename'],": "'original_filename' => MG_escapeHTML($row['media_original_filename']),",
    "'media_thumbnail'   => $thumbnail,": "'media_thumbnail'   => MG_escapeHTML($thumbnail),",
    "'media_title'       => $row['media_title'],": "'media_title'       => MG_escapeHTML($row['media_title']),",
    "'media_desc'        => $row['media_desc'],": "'media_desc'        => MG_escapeHTML($row['media_desc']),",
    "'remoteurl'         => $remoteurl,": "'remoteurl'         => MG_escapeHTML($remoteurl),",
    "'media_keywords'    => $row['media_keywords'],": "'media_keywords'    => MG_escapeHTML($row['media_keywords']),",
    "'artist'            => $row['artist'],": "'artist'            => MG_escapeHTML($row['artist']),",
    "'musicalbum'        => $row['album'],": "'musicalbum'        => MG_escapeHTML($row['album']),",
    "'genre'             => $row['genre'],": "'genre'             => MG_escapeHTML($row['genre']),",
}
for old, new in edit_repls.items():
    if old in text:
        text = text.replace(old, new)
p.write_text(text, encoding='utf-8')

# Advanced search values/options.
p = Path('public_html/search.php')
text = p.read_text(encoding='utf-8')
text = replace_once(text, ". $row['cat_name'] . '</option>';", ". MG_escapeHTML($row['cat_name']) . '</option>';", 'search category text')
text = replace_once(text, ". COM_getDisplayName($U['uid']) . '</option>';", ". MG_escapeHTML(COM_getDisplayName($U['uid'])) . '</option>';", 'search user text')
text = replace_once(text, "'search_keywords'      => ($searchinfo['keywords'] == '*') ? '*' : $S['keywords'],", "'search_keywords'      => ($searchinfo['keywords'] == '*') ? '*' : MG_escapeHTML($S['keywords']),", 'search keywords value')
p.write_text(text, encoding='utf-8')

# Roadmap: record the completed centralized hardening while leaving the broader
# all-theme audit open until the remaining album/theme variables are traced.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
old = '- [ ] Audit attribute escaping across all frame/theme variants.\n'
new = old + '- [x] Centralize HTML escaping for framed-image attributes, media edit/manage values, lightbox links and advanced-search values.\n'
text = replace_once(text, old, new, 'roadmap attribute audit')
p.write_text(text, encoding='utf-8')
