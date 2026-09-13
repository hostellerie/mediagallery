from pathlib import Path


def replace_once(path, old, new, label, encoding='utf-8'):
    p = Path(path)
    text = p.read_text(encoding=encoding)
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one %s marker in %s, found %d' % (label, path, count))
    p.write_text(text.replace(old, new, 1), encoding=encoding)


# Common structured-data helpers. Keep output conservative and tied to reliable MediaGallery data.
path = Path('include/common.php')
text = path.read_text(encoding='utf-8')
marker = """function MG_getRemoteAddress()\n{\n    return isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';\n}\n"""
addition = r'''function MG_renderJsonLd($data)
{
    if (!is_array($data) || empty($data)) {
        return '';
    }

    $json = json_encode(
        $data,
        JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_UNESCAPED_SLASHES
    );
    if ($json === false || $json === '') {
        return '';
    }

    return '<script type="application/ld+json">' . $json . '</script>' . LB;
}

function MG_buildMediaStructuredData($media, $canonicalUrl)
{
    if (!is_array($media) || empty($canonicalUrl)) {
        return array();
    }

    $type = isset($media['media_type']) ? (int) $media['media_type'] : -1;
    $isRemote = !empty($media['remote_media']);

    // Remote and embedded media can point at third-party resources whose
    // content URL, thumbnail and publication metadata MediaGallery does not own.
    if ($isRemote || $type === 5) {
        return array();
    }

    $schemaType = '';
    if ($type === 0) {
        $schemaType = 'ImageObject';
    } elseif ($type === 1) {
        $schemaType = 'VideoObject';
    } elseif ($type === 2) {
        $schemaType = 'AudioObject';
    } else {
        return array();
    }

    $title = isset($media['media_title']) ? trim(strip_tags(PLG_replaceTags($media['media_title']))) : '';
    if ($title === '' && isset($media['media_original_filename'])) {
        $title = trim((string) $media['media_original_filename']);
    }
    if ($title === '') {
        return array();
    }

    $filename = isset($media['media_filename']) ? trim((string) $media['media_filename']) : '';
    $extension = isset($media['media_mime_ext']) ? trim((string) $media['media_mime_ext']) : '';
    if ($filename === '' || $extension === '') {
        return array();
    }

    $uploadTime = isset($media['media_upload_time']) ? (int) $media['media_upload_time'] : 0;

    // Google requires a real thumbnail and upload date for VideoObject. MediaGallery's
    // generated fallback for videos may only be a generic file-type icon, so only an
    // explicitly attached thumbnail is reliable enough for video structured data.
    if ($type === 1 && ($uploadTime <= 0 || empty($media['media_tn_attached']))) {
        return array();
    }

    $data = array(
        '@context' => 'https://schema.org',
        '@type'    => $schemaType,
        '@id'      => $canonicalUrl . '#media',
        'url'      => $canonicalUrl,
        'name'     => $title,
        'contentUrl' => Media::getFileUrl('orig', $filename, $extension),
    );

    $description = isset($media['media_desc'])
        ? MG_prepareMetaDescription(PLG_replaceTags($media['media_desc']), 500)
        : '';
    if ($description !== '') {
        $data['description'] = $description;
    }

    if ($uploadTime > 0) {
        $data['uploadDate'] = date('c', $uploadTime);
    }

    if (!empty($media['mime_type'])) {
        $data['encodingFormat'] = (string) $media['mime_type'];
    }

    $width = isset($media['media_resolution_x']) ? (int) $media['media_resolution_x'] : 0;
    $height = isset($media['media_resolution_y']) ? (int) $media['media_resolution_y'] : 0;
    if ($width > 0) {
        $data['width'] = $width;
    }
    if ($height > 0) {
        $data['height'] = $height;
    }

    if ($type === 1) {
        $data['thumbnailUrl'] = Media::getFileUrl('tn', $filename, 'jpg', 1);
    }

    return $data;
}

function MG_getRemoteAddress()
{
    return isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
}
'''
if text.count(marker) != 1:
    raise SystemExit('common structured-data insertion marker mismatch')
path.write_text(text.replace(marker, addition, 1), encoding='utf-8')

# Use one metadata query for description + structured data and append JSON-LD to the existing header code.
path = Path('public_html/media.php')
text = path.read_text(encoding='utf-8')
old = r'''$mediaDescription = DB_getItem(
    $_TABLES['mg_media'],
    'media_desc',
    "media_id='" . DB_escapeString($mid) . "'"
);
$seoDescription = MG_prepareMetaDescription(PLG_replaceTags($mediaDescription), 160);
if ($seoDescription !== '') {
    $meta .= '<meta name="description" content="' . MG_escapeHTML($seoDescription) . '"' . XHTML . '>' . LB;
}

$display = MG_createHTMLDocument($display, $ptitle, $meta);
'''
new = r'''$mediaMeta = array();
$metaResult = DB_query(
    "SELECT media_id, media_filename, media_original_filename, media_mime_ext, mime_type, "
  . "media_title, media_desc, media_type, media_upload_time, media_resolution_x, "
  . "media_resolution_y, remote_media, remote_url, media_tn_attached "
  . "FROM {$_TABLES['mg_media']} WHERE media_id='" . DB_escapeString($mid) . "'"
);
if ($metaResult !== false && DB_numRows($metaResult) === 1) {
    $mediaMeta = DB_fetchArray($metaResult);
}

$mediaDescription = isset($mediaMeta['media_desc']) ? $mediaMeta['media_desc'] : '';
$seoDescription = MG_prepareMetaDescription(PLG_replaceTags($mediaDescription), 160);
if ($seoDescription !== '') {
    $meta .= '<meta name="description" content="' . MG_escapeHTML($seoDescription) . '"' . XHTML . '>' . LB;
}

$structuredData = MG_buildMediaStructuredData($mediaMeta, $canonicalUrl);
if (!empty($structuredData)) {
    $meta .= MG_renderJsonLd($structuredData);
}

$display = MG_createHTMLDocument($display, $ptitle, $meta);
'''
if text.count(old) != 1:
    raise SystemExit('media.php metadata marker mismatch')
path.write_text(text.replace(old, new, 1), encoding='utf-8')

# Record the conservative implementation and explicit album-page decision.
path = Path('ROADMAP.md')
text = path.read_text(encoding='utf-8')
old = '- [ ] Add structured data only where MediaGallery has reliable source data and does not conflict with Geeklog core/theme output.\n'
new = '''- [x] Add structured data only where MediaGallery has reliable source data and does not conflict with Geeklog core/theme output.\n  - [x] Emit conservative JSON-LD for local `ImageObject` / `AudioObject`, and `VideoObject` only when a real attached thumbnail and upload date are available.\n  - [x] Skip remote/embedded media whose content, thumbnail or publication metadata MediaGallery does not own.\n  - [x] Do not add album-level `CollectionPage` JSON-LD while generic page-schema ownership may belong to Geeklog core/themes.\n'''
if text.count(old) != 1:
    raise SystemExit('ROADMAP structured-data marker mismatch')
path.write_text(text.replace(old, new, 1), encoding='utf-8')

# Add a release-candidate test item so JSON-LD gets checked on real media rows.
path = Path('TESTING-1.8.md')
text = path.read_text(encoding='utf-8')
marker = '## Public rendering\n'
if marker in text and 'structured data' not in text.lower():
    text = text.replace(marker, marker + '\n- Validate JSON-LD on a local image, local audio, video with attached thumbnail, video without attached thumbnail, and remote/embed media. Only the first three eligible cases should emit media structured data.\n', 1)
elif 'structured data' not in text.lower():
    text += '\n\n## Structured data\n\n- Validate JSON-LD on a local image, local audio, video with attached thumbnail, video without attached thumbnail, and remote/embed media. Only the first three eligible cases should emit media structured data.\n'
path.write_text(text, encoding='utf-8')
