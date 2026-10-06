<?php

$root = dirname(__DIR__);
$albumSource = file_get_contents($root . '/public_html/album.php');
$mediaSource = file_get_contents($root . '/public_html/media.php');
$legacySource = file_get_contents($root . '/functions_legacy.inc');
$interopSource = file_get_contents($root . '/include/interoperability_180.php');

$failures = array();

function mg_item_display_require($content, $needle, $message, &$failures)
{
    if ($content === false || strpos($content, $needle) === false) {
        $failures[] = $message;
    }
}

mg_item_display_require(
    $albumSource,
    "PLG_itemDisplay(MG_albumItemId180(\$album_id), 'mediagallery')",
    'Public album pages do not expose the generic PLG_itemDisplay() hook.',
    $failures
);
mg_item_display_require(
    $mediaSource,
    "PLG_itemDisplay((string) \$mid, 'mediagallery')",
    'Public media pages do not expose the generic PLG_itemDisplay() hook.',
    $failures
);

mg_item_display_require(
    $mediaSource,
    "\$mid       = isset(\$_REQUEST['s'])    ? COM_applyFilter(\$_REQUEST['s'])",
    'Public media pages must preserve alphanumeric MediaGallery media IDs.',
    $failures
);
if (strpos($mediaSource, "COM_applyFilter(\$_REQUEST['s'],   true)") !== false
    || strpos($mediaSource, "COM_applyFilter(\$_REQUEST['s'], true)") !== false
) {
    $failures[] = 'Public media pages still force media IDs through numeric filtering.';
}
mg_item_display_require(
    $interopSource,
    "return 'album:' . intval(\$album_id);",
    'Album interoperability IDs no longer use album:<id>.',
    $failures
);
mg_item_display_require(
    $legacySource,
    'function plugin_getiteminfo_mediagallery',
    'MediaGallery Item Info callback is missing.',
    $failures
);
mg_item_display_require(
    $legacySource,
    "if (\$item180['type'] === 'album')",
    'MediaGallery Item Info no longer resolves album identities.',
    $failures
);

mg_item_display_require(
    $legacySource,
    "'/media.php?f=0&sort=0&s='",
    'MediaGallery Item Info must return raw media URLs with & separators.',
    $failures
);
mg_item_display_require(
    $interopSource,
    "'/media.php?f=0&sort=0&s='",
    'MediaGallery ID resolver must return raw media URLs with & separators.',
    $failures
);
if (strpos($legacySource, "/media.php?f=0&amp;sort=0&amp;s=") !== false) {
    $failures[] = 'MediaGallery Item Info still returns HTML-escaped media URLs.';
}
if (strpos($interopSource, "/media.php?f=0&amp;sort=0&amp;s=") !== false) {
    $failures[] = 'MediaGallery ID resolver still returns HTML-escaped media URLs.';
}

if (!empty($failures)) {
    fwrite(STDERR, "MediaGallery public item-display contract failed:\n");
    foreach ($failures as $failure) {
        fwrite(STDERR, '- ' . $failure . "\n");
    }
    exit(1);
}

echo "MediaGallery public item-display contract: OK\n";
