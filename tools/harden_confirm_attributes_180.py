from pathlib import Path


def replace_all_exact(path, old, new, expected, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != expected:
        raise SystemExit('Expected %d markers for %s, found %d' % (expected, label, count))
    p.write_text(text.replace(old, new), encoding='utf-8')

# Escape confirmation messages for their HTML attribute context.
replace_all_exact(
    'admin/category.php',
    "'lang_delete_confirm' => $LANG_MG01['delete_item_confirm'],",
    "'lang_delete_confirm' => MG_escapeHTML($LANG_MG01['delete_item_confirm']),",
    1,
    'category confirmation producer')
replace_all_exact(
    'admin/massdelete.php',
    "'lang_delete_confirm' => $LANG_MG01['delete_item_confirm'],",
    "'lang_delete_confirm' => MG_escapeHTML($LANG_MG01['delete_item_confirm']),",
    1,
    'massdelete confirmation producer')
replace_all_exact(
    'include/mediamanage.php',
    "'lang_delete_confirm'     => $LANG_MG01['delete_item_confirm'],",
    "'lang_delete_confirm'     => MG_escapeHTML($LANG_MG01['delete_item_confirm']),",
    2,
    'media manager confirmation producers')
replace_all_exact(
    'include/mediamanage.php',
    "'lang_delete_confirm'           => $LANG_MG01['delete_item_confirm'],",
    "'lang_delete_confirm'           => MG_escapeHTML($LANG_MG01['delete_item_confirm']),",
    1,
    'media editor confirmation producer')

# Keep translated data in HTML, not inside JavaScript string literals.
replacements = {
    'templates/category.thtml': (
        "onclick=\"javascript:return confirm('{lang_delete_confirm}');\"",
        "data-confirm=\"{lang_delete_confirm}\" onclick=\"return confirm(this.getAttribute('data-confirm'));\"") ,
    'templates/massdelete.thtml': (
        "onclick=\"return confirm('{lang_delete_confirm}');\"",
        "data-confirm=\"{lang_delete_confirm}\" onclick=\"return confirm(this.getAttribute('data-confirm'));\"") ,
    'templates/mediamanage.thtml': (
        "onclick=\"return confirm('{lang_delete_confirm}');\"",
        "data-confirm=\"{lang_delete_confirm}\" onclick=\"return confirm(this.getAttribute('data-confirm'));\"") ,
    'templates/mediaedit.thtml': (
        "onclick=\"return confirm('{lang_delete_confirm}');\"",
        "data-confirm=\"{lang_delete_confirm}\" onclick=\"return confirm(this.getAttribute('data-confirm'));\"") ,
}
for path, pair in replacements.items():
    replace_all_exact(path, pair[0], pair[1], 1, path + ' confirmation')

p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
marker = '- [x] Remove dynamic property URLs from inline JavaScript and preserve lightbox slideshow actions on media detail views.\n'
addition = marker + '- [x] Remove translated delete-confirmation text from JavaScript string literals and escape it for HTML data attributes.\n'
if text.count(marker) != 1:
    raise SystemExit('Roadmap marker mismatch')
p.write_text(text.replace(marker, addition, 1), encoding='utf-8')
