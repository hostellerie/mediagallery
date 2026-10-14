<?php
// MediaGallery 2.0.0: site-scoped persistent private imports.
// Keep persistent files outside Geeklog's destructively cleaned path_data.
if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

function MG_persistentImportRoot200()
{
    global $_CONF;
    $data = isset($_CONF['path_data']) ? rtrim($_CONF['path_data'], "/\\") : '';
    if ($data === '' || $data === '/' || $data === '.' || $data === '..') {
        return false;
    }
    return dirname($data) . DIRECTORY_SEPARATOR . basename($data) . '-mediagallery' . DIRECTORY_SEPARATOR;
}

/**
 * Non-destructive, repeatable migration of the former data/mediagallery/uploads tree.
 * Never traverse symlinks or overwrite conflicting destination files.
 * The old tree is intentionally never deleted (even on success).
 */
function MG_migratePrivateUploads200($source, $destination)
{
    if (!is_dir($source)) {
        return true;
    }
    if (is_link($source) || is_link($destination)) {
        COM_errorLog('MediaGallery: refusing symlink in private import roots', 1);
        return false;
    }
    if (!is_dir($destination) && !@mkdir($destination, 0750, true)) {
        COM_errorLog('MediaGallery: unable to create private import directory ' . $destination, 1);
        return false;
    }
    if (!is_writable($destination)) {
        COM_errorLog('MediaGallery: private import directory not writable ' . $destination, 1);
        return false;
    }

    $items = @scandir($source);
    if ($items === false) {
        COM_errorLog('MediaGallery: cannot scan legacy imports ' . $source, 1);
        return false;
    }
    $success = true;
    foreach ($items as $name) {
        if ($name === '.' || $name === '..') {
            continue;
        }
        $from = rtrim($source, "/\\") . DIRECTORY_SEPARATOR . $name;
        $to = rtrim($destination, "/\\") . DIRECTORY_SEPARATOR . $name;
        if (is_link($from) || is_link($to)) {
            COM_errorLog('MediaGallery: refusing symlink in legacy imports ' . $from, 1);
            $success = false;
            continue;
        }
        if (is_dir($from)) {
            if (is_file($to) || !MG_migratePrivateUploads200($from, $to)) {
                $success = false;
            }
            continue;
        }
        if (!is_file($from) || is_dir($to)) {
            COM_errorLog('MediaGallery: unsupported legacy import entry ' . $from, 1);
            $success = false;
            continue;
        }
        $checksum = @hash_file('sha256', $from);
        if ($checksum === false) {
            $success = false;
            continue;
        }
        if (is_file($to)) {
            if (@hash_file('sha256', $to) !== $checksum) {
                COM_errorLog('MediaGallery: conflicting private import, destination left untouched ' . $to, 1);
                $success = false;
            }
            continue;
        }
        $temporary = @tempnam($destination, '.mg-import-');
        if ($temporary === false) {
            $success = false;
            continue;
        }
        if (!@copy($from, $temporary) || @hash_file('sha256', $temporary) !== $checksum || !@rename($temporary, $to)) {
            COM_errorLog('MediaGallery: failed to verify/copy private import ' . $from, 1);
            @unlink($temporary);
            $success = false;
        }
    }
    return $success;
}
