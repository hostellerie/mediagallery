from pathlib import Path

p = Path('include/lib-media.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')

replacements = {
    "$_MG_CONF['swf_play']": '1',
    "$_MG_CONF['swf_menu']": '0',
    "$_MG_CONF['swf_quality']": "'high'",
    "$_MG_CONF['swf_height']": '480',
    "$_MG_CONF['swf_width']": '640',
    "$_MG_CONF['swf_loop']": '0',
    "$_MG_CONF['swf_scale']": "'showall'",
    "$_MG_CONF['swf_wmode']": "'transparent'",
    "$_MG_CONF['swf_allowscriptaccess']": "'sameDomain'",
    "$_MG_CONF['swf_bgcolor']": "'#FFFFFF'",
    "$_MG_CONF['swf_version']": '6',
    "$_MG_CONF['swf_flashvars']": "''",
}

for old, new in replacements.items():
    count = text.count(old)
    if count != 2:
        raise SystemExit('%s expected exactly twice, found %d' % (old, count))
    text = text.replace(old, new)

p.write_text(text, encoding='utf-8', errors='surrogateescape')
