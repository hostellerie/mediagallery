from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one %s marker in %s, found %d' % (label, path, count))
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


# Reusable plain-text metadata helper, PHP 5.6 compatible with mbstring fallback.
replace_once(
    'include/common.php',
    """function MG_escapeHTML($value)\n{\n    return htmlspecialchars((string) $value, ENT_QUOTES, COM_getCharset(), false);\n}\n\nfunction MG_getRemoteAddress()""",
    """function MG_escapeHTML($value)\n{\n    return htmlspecialchars((string) $value, ENT_QUOTES, COM_getCharset(), false);\n}\n\nfunction MG_prepareMetaDescription($value, $maxLength = 160)\n{\n    $value = html_entity_decode(strip_tags((string) $value), ENT_QUOTES, COM_getCharset());\n    $normalized = preg_replace('/\\s+/u', ' ', $value);\n    if ($normalized === null) {\n        $normalized = preg_replace('/\\s+/', ' ', $value);\n    }\n    $value = trim($normalized);\n    $maxLength = (int) $maxLength;\n\n    if ($value === '' || $maxLength < 1) {\n        return '';\n    }\n\n    if (function_exists('mb_strlen') && function_exists('mb_substr')) {\n        if (mb_strlen($value, COM_getCharset()) > $maxLength) {\n            $value = rtrim(mb_substr($value, 0, max(1, $maxLength - 1), COM_getCharset()), \" \\t\\n\\r\\0\\x0B,.;:-\") . '…';\n        }\n    } elseif (strlen($value) > $maxLength) {\n        $value = rtrim(substr($value, 0, max(1, $maxLength - 3)), \" \\t\\n\\r\\0\\x0B,.;:-\") . '...';\n    }\n\n    return $value;\n}\n\nfunction MG_getRemoteAddress()""",
    'meta description helper')

# Album canonical already exists: append description derived only from editorial album description.
p = Path('public_html/album.php')
text = p.read_text(encoding='utf-8')
old = """$meta = '<link rel=\"canonical\" href=\"'\n      . htmlspecialchars($canonicalUrl, ENT_QUOTES, COM_getCharset())\n      . '\"' . XHTML . '>' . LB;\n\n$display = MG_createHTMLDocument($display, $pageTitle, $meta);"""
new = """$meta = '<link rel=\"canonical\" href=\"'\n      . htmlspecialchars($canonicalUrl, ENT_QUOTES, COM_getCharset())\n      . '\"' . XHTML . '>' . LB;\n\n$descriptionLength = ($current_print_page > 1) ? 145 : 160;\n$seoDescription = MG_prepareMetaDescription(PLG_replaceTags($album->description), $descriptionLength);\nif ($seoDescription !== '') {\n    if ($current_print_page > 1) {\n        $seoDescription .= ' - ' . $LANG_MG03['page'] . ' ' . $current_print_page;\n    }\n    $meta .= '<meta name=\"description\" content=\"' . MG_escapeHTML($seoDescription) . '\"' . XHTML . '>' . LB;\n}\n\n$display = MG_createHTMLDocument($display, $pageTitle, $meta);"""
if text.count(old) != 1:
    raise SystemExit('album metadata marker mismatch')
p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Media canonical already exists: add description from the stored media description only.
p = Path('public_html/media.php')
text = p.read_text(encoding='utf-8')
old = """$meta = '<link rel=\"canonical\" href=\"'\n      . htmlspecialchars($canonicalUrl, ENT_QUOTES, COM_getCharset())\n      . '\"' . XHTML . '>' . LB;\n\n$display = MG_createHTMLDocument($display, $ptitle, $meta);"""
new = """$meta = '<link rel=\"canonical\" href=\"'\n      . htmlspecialchars($canonicalUrl, ENT_QUOTES, COM_getCharset())\n      . '\"' . XHTML . '>' . LB;\n\n$mediaDescription = DB_getItem(\n    $_TABLES['mg_media'],\n    'media_desc',\n    \"media_id='\" . DB_escapeString($mid) . \"'\"\n);\n$seoDescription = MG_prepareMetaDescription(PLG_replaceTags($mediaDescription), 160);\nif ($seoDescription !== '') {\n    $meta .= '<meta name=\"description\" content=\"' . MG_escapeHTML($seoDescription) . '\"' . XHTML . '>' . LB;\n}\n\n$display = MG_createHTMLDocument($display, $ptitle, $meta);"""
if text.count(old) != 1:
    raise SystemExit('media metadata marker mismatch')
p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Roadmap: precise SEO metadata completion; structured data remains deliberately open.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
needle = '- [x] Modernize active media popups, public profile tables and remaining audio fragments for responsive rendering.\n'
addition = needle + '- [x] Add canonical-safe meta descriptions for public album and media pages from existing editorial descriptions.\n'
if text.count(needle) != 1:
    raise SystemExit('ROADMAP SEO metadata marker mismatch')
p.write_text(text.replace(needle, addition, 1), encoding='utf-8')
