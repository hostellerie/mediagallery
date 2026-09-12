<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | MediaGallery 1.8.0 stale temporary-file cleanup                          |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

/**
 * Remove abandoned MediaGallery temporary files/directories conservatively.
 *
 * The cleanup is intentionally scoped to MediaGallery's private tmp directory,
 * runs at most once per interval, and only removes entries whose complete tree
 * is older than the configured age. This protects active uploads and batches.
 *
 * @param int $maxAge      Minimum age in seconds before an entry is stale.
 * @param int $minInterval Minimum seconds between directory scans.
 * @return int Number of top-level stale entries removed.
 */
function MG_cleanupStaleTemp180($maxAge = 172800, $minInterval = 3600)
{
    global $_MG_CONF;

    static $ran = false;
    if ($ran) {
        return 0;
    }
    $ran = true;

    if (!isset($_MG_CONF['tmp_path'])) {
        return 0;
    }

    $tmpPath = rtrim((string) $_MG_CONF['tmp_path'], '/\\') . DIRECTORY_SEPARATOR;
    if (!is_dir($tmpPath) || !is_readable($tmpPath)) {
        return 0;
    }

    $maxAge = max(3600, (int) $maxAge);
    $minInterval = max(300, (int) $minInterval);
    $now = time();
    $marker = $tmpPath . '.mediagallery-cleanup';

    clearstatcache(true, $marker);
    if (is_file($marker)) {
        $markerTime = @filemtime($marker);
        if ($markerTime !== false && ($now - $markerTime) < $minInterval) {
            return 0;
        }
    }

    // Touch before scanning so concurrent requests do not all perform cleanup.
    @touch($marker, $now);

    $cutoff = $now - $maxAge;
    $removed = 0;
    $handle = @opendir($tmpPath);
    if ($handle === false) {
        return 0;
    }

    while (($name = readdir($handle)) !== false) {
        if ($name === '.' || $name === '..' || $name === '.mediagallery-cleanup') {
            continue;
        }

        $path = $tmpPath . $name;
        if (!MG_tempTreeIsStale180($path, $cutoff)) {
            continue;
        }

        if (is_dir($path) && !is_link($path)) {
            if (MG_removeTempTree180($path)) {
                $removed++;
            }
        } else {
            if (@unlink($path)) {
                $removed++;
            }
        }
    }
    closedir($handle);

    if ($removed > 0) {
        COM_errorLog('MediaGallery 1.8: removed ' . $removed . ' stale temporary item(s) older than ' . $maxAge . ' seconds.');
    }

    return $removed;
}

/**
 * Return true only when an entire file/directory tree is older than cutoff.
 * Symlinks are treated as leaf entries and never followed.
 */
function MG_tempTreeIsStale180($path, $cutoff)
{
    if (is_link($path) || is_file($path)) {
        $mtime = @filemtime($path);
        return $mtime !== false && $mtime < $cutoff;
    }

    if (!is_dir($path)) {
        return false;
    }

    $mtime = @filemtime($path);
    if ($mtime === false || $mtime >= $cutoff) {
        return false;
    }

    $handle = @opendir($path);
    if ($handle === false) {
        return false;
    }

    while (($name = readdir($handle)) !== false) {
        if ($name === '.' || $name === '..') {
            continue;
        }
        if (!MG_tempTreeIsStale180($path . DIRECTORY_SEPARATOR . $name, $cutoff)) {
            closedir($handle);
            return false;
        }
    }
    closedir($handle);

    return true;
}

/**
 * Remove a stale tree without following symlinks.
 */
function MG_removeTempTree180($path)
{
    if (is_link($path) || is_file($path)) {
        return @unlink($path);
    }

    if (!is_dir($path)) {
        return false;
    }

    $handle = @opendir($path);
    if ($handle === false) {
        return false;
    }

    $ok = true;
    while (($name = readdir($handle)) !== false) {
        if ($name === '.' || $name === '..') {
            continue;
        }
        if (!MG_removeTempTree180($path . DIRECTORY_SEPARATOR . $name)) {
            $ok = false;
        }
    }
    closedir($handle);

    if (!$ok) {
        return false;
    }

    return @rmdir($path);
}
