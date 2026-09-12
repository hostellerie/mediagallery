from pathlib import Path

# Make MG_optionlist capable of emitting an explicit id so templates can bind
# visible labels to generated select controls.
p = Path('include/common.php')
text = p.read_text(encoding='utf-8')
old = """function MG_optionlist($info)
{
    $disabled = isset($info['disabled']) ? $info['disabled'] : '';
    $retval = '<select name=\"' . $info['name'] . '\"'
            . ($disabled ? ' disabled=\"disabled\"' : '') . '>' . LB;
"""
new = """function MG_optionlist($info)
{
    $disabled = isset($info['disabled']) ? $info['disabled'] : '';
    $id = isset($info['id']) ? trim($info['id']) : '';
    $retval = '<select name=\"' . $info['name'] . '\"'
            . ($id !== '' ? ' id=\"' . htmlspecialchars($id, ENT_QUOTES, COM_getCharset()) . '\"' : '')
            . ($disabled ? ' disabled=\"disabled\"' : '') . '>' . LB;
"""
if text.count(old) != 1:
    raise SystemExit('MG_optionlist header not found exactly once')
p.write_text(text.replace(old, new), encoding='utf-8')

# Give every advanced-search form control a stable id.
p = Path('public_html/search.php')
text = p.read_text(encoding='utf-8')
repls = {
    '$cat_select = \'<select name="cat_id">\';': '$cat_select = \'<select id="mg-search-category" name="cat_id">\';',
    "        'name'    => 'keyType',\n": "        'name'    => 'keyType',\n        'id'      => 'mg-search-keytype',\n",
    "        'name'    => 'swhere',\n": "        'name'    => 'swhere',\n        'id'      => 'mg-search-swhere',\n",
    "        'name'    => 'numresults',\n": "        'name'    => 'numresults',\n        'id'      => 'mg-search-numresults',\n",
    '$userselect = \'<select name="uid">\';': '$userselect = \'<select id="mg-search-user" name="uid">\';',
}
for old, new in repls.items():
    if text.count(old) != 1:
        raise SystemExit('search.php marker not found exactly once: ' + old)
    text = text.replace(old, new)
p.write_text(text, encoding='utf-8')

# Bind visible labels to all advanced-search controls.
p = Path('templates/search_page.thtml')
text = p.read_text(encoding='utf-8')
repls = {
    '    {lang_search_for}:\n': '    <label for="mg-search-keywords">{lang_search_for}:</label>\n',
    '    <input type="text" name="keywords" size="40" value="{search_keywords}"{xhtml}>&nbsp;\n    {keytype_select}\n': '    <input type="text" id="mg-search-keywords" name="keywords" size="40" value="{search_keywords}"{xhtml}>&nbsp;\n    <label for="mg-search-keytype">{lang_options}:</label> {keytype_select}\n',
    '    {lang_search_in}:\n': '    <label for="mg-search-swhere">{lang_search_in}:</label>\n',
    '    {lang_category}:\n': '    <label for="mg-search-category">{lang_category}:</label>\n',
    '    {lang_user}:\n': '    <label for="mg-search-user">{lang_user}:</label>\n',
    '    {lang_results}:\n': '    <label for="mg-search-numresults">{lang_results}:</label>\n',
}
for old, new in repls.items():
    if text.count(old) != 1:
        raise SystemExit('search template marker not found exactly once: ' + old)
    text = text.replace(old, new)
p.write_text(text, encoding='utf-8')

# Record only the part of the roadmap that is fully completed by this patch.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
old = '- [ ] Remove or replace remaining legacy IE-only slideshow transition code.\n'
new = '- [x] Remove the legacy IE-only slideshow transition code and keep browser-neutral slideshow controls.\n'
if text.count(old) != 1:
    raise SystemExit('Roadmap slideshow marker not found exactly once')
p.write_text(text.replace(old, new), encoding='utf-8')
