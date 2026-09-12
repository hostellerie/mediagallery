<?php

/**
 * MediaGallery 1.8.0 pre-upgrade media migration tool.
 *
 * Run this from an extracted MediaGallery 1.8.0 archive BEFORE uploading the
 * plugin ZIP over a MediaGallery 1.7.x installation. Geeklog's native plugin
 * uploader replaces public_html/mediagallery as a whole, so legacy media must
 * first be copied to the persistent images directory.
 *
 * Usage:
 *   php tools/migrate-media-storage.php /path/to/geeklog
 *
 * The supplied path may be the Geeklog private root (containing public_html)
 * or the public_html directory itself.
 */

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "This migration tool can only be run from the command line.\n");
    exit(2);
}

if (!isset($argv[1]) || trim($argv[1]) === '') {
    fwrite(STDERR, "Usage: php tools/migrate-media-storage.php /path/to/geeklog\n");
    exit(2);
}

$input = realpath($argv[1]);
if ($input === false || !is_dir($input)) {
    fwrite(STDERR, "Geeklog path not found: {$argv[1]}\n");
    exit(2);
}

$candidates = array(
    rtrim($input, '/\\') . '/public_html/lib-common.php',
    rtrim($input, '/\\') . '/lib-common.php',
);

$libCommon = '';
foreach ($candidates as $candidate) {
    if (is_file($candidate)) {
        $libCommon = $candidate;
        break;
    }
}

if ($libCommon === '') {
    fwrite(STDERR, "Unable to find public_html/lib-common.php below the supplied path.\n");
    exit(2);
}

require_once $libCommon;

// On a legacy 1.7.x site the 1.8 migration functions are not installed yet,
// so load them from this extracted archive. On an already updated 1.8 site,
// reuse the installed definitions instead.
if (!function_exists('MG_migrateMediaStorage180')) {
    require_once dirname(__DIR__) . '/include/config_180.php';
}

$source = MG_getLegacyMediaStorage180();
$target = MG_getMediaStorageTarget180();

if ($target === false) {
    fwrite(STDERR, "Unable to resolve the persistent images storage.\n");
    fwrite(STDERR, "If path_images is customized, define a matching images_url before migrating.\n");
    exit(1);
}

$sourceInventory = MG_inventoryMediaStorage180($source);
if ($sourceInventory === false) {
    fwrite(STDERR, "Unable to inventory legacy MediaGallery media.\n");
    exit(1);
}

printf("Legacy source : %s\n", $source);
printf("Destination   : %s\n", $target['path']);
printf("Files found   : %d\n", $sourceInventory['count']);
printf("Bytes found   : %d\n", $sourceInventory['bytes']);

if (!MG_migrateMediaStorage180($source)) {
    fwrite(STDERR, "Migration FAILED. The legacy source has not been deleted.\n");
    exit(1);
}

$targetInventory = MG_inventoryMediaStorage180($target['path']);
if ($targetInventory === false) {
    fwrite(STDERR, "Migration copied files but final destination inventory failed.\n");
    exit(1);
}

foreach ($sourceInventory['files'] as $relative => $size) {
    if (!isset($targetInventory['files'][$relative]) || $targetInventory['files'][$relative] !== $size) {
        fwrite(STDERR, "Final verification FAILED for: {$relative}\n");
        exit(1);
    }
}

printf("Migration OK   : %d source files verified in persistent storage.\n", $sourceInventory['count']);
echo "The legacy media directory was intentionally left untouched.\n";
echo "You may now upload the MediaGallery 1.8.0 plugin archive through Geeklog.\n";

exit(0);
