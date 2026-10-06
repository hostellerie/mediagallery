<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | Interoperability helpers for MediaGallery 1.8.0                           |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

/**
 * Build the stable item id used for album lifecycle events.
 *
 * Media ids remain unchanged for backward compatibility. Albums use a
 * namespaced id so Geeklog 2.1.1 can distinguish them without relying on the
 * sub_type argument added in newer Geeklog releases.
 *
 * @param int $album_id
 * @return string
 */
function MG_albumItemId180($album_id)
{
    return 'album:' . intval($album_id);
}

/**
 * Decode a MediaGallery interoperability item id.
 *
 * @param string $id
 * @return array Array containing type (media|album) and id.
 */
function MG_parseItemId180($id)
{
    $id = (string) $id;

    if (strpos($id, 'album:') === 0) {
        return array(
            'type' => 'album',
            'id'   => intval(substr($id, 6))
        );
    }

    return array(
        'type' => 'media',
        'id'   => $id
    );
}

/**
 * Notify Geeklog listeners that an album's public representation changed.
 *
 * Each album is announced at most once per request. Operations such as batch
 * uploads, multi-media edits and recursive maintenance can touch the same
 * album repeatedly; consumers such as IndexNow only need the final state.
 *
 * @param int $album_id
 * @return void
 */
function MG_notifyAlbumSaved180($album_id)
{
    static $notified = array();

    $album_id = intval($album_id);
    if ($album_id <= 0 || !function_exists('PLG_itemSaved')) {
        return;
    }
    if (isset($notified[$album_id])) {
        return;
    }

    $notified[$album_id] = true;
    PLG_itemSaved(MG_albumItemId180($album_id), 'mediagallery');
}

/**
 * Notify Geeklog listeners that an album was deleted.
 *
 * Recursive deletion paths can encounter the root album both in the recursive
 * worker and in the caller. Deduplication keeps the lifecycle contract stable.
 *
 * @param int $album_id
 * @return void
 */
function MG_notifyAlbumDeleted180($album_id)
{
    static $notified = array();

    $album_id = intval($album_id);
    if ($album_id <= 0 || !function_exists('PLG_itemDeleted')) {
        return;
    }
    if (isset($notified[$album_id])) {
        return;
    }

    $notified[$album_id] = true;
    PLG_itemDeleted(MG_albumItemId180($album_id), 'mediagallery');
}

/**
 * Notify listeners for every album containing a media item.
 *
 * Useful after a media edit: the media URL changed in content terms and each
 * album page containing that media has changed too.
 *
 * @param string $media_id
 * @return void
 */
function MG_notifyMediaAlbumsSaved180($media_id)
{
    global $_TABLES;

    if (empty($_TABLES['mg_media_albums'])) {
        return;
    }

    $media_id = DB_escapeString((string) $media_id);
    $result = DB_query(
        "SELECT DISTINCT album_id FROM {$_TABLES['mg_media_albums']} "
        . "WHERE media_id='" . $media_id . "'"
    );

    while ($row = DB_fetchArray($result)) {
        MG_notifyAlbumSaved180($row['album_id']);
    }
}

/**
 * Return whether an album is anonymously readable.
 *
 * Hidden albums are treated as non-public for interoperability purposes even
 * when their raw permission bits would otherwise allow anonymous reads.
 *
 * @param int $album_id
 * @return bool
 */
function MG_albumIsPublic180($album_id)
{
    global $_TABLES;

    $album_id = intval($album_id);
    if ($album_id <= 0) {
        return false;
    }

    $result = DB_query(
        "SELECT hidden, perm_anon FROM {$_TABLES['mg_albums']} "
        . "WHERE album_id=" . $album_id . " LIMIT 1"
    );
    if (!$result || DB_numRows($result) !== 1) {
        return false;
    }

    $row = DB_fetchArray($result);
    return ((int) $row['hidden'] === 0 && (((int) $row['perm_anon']) & 2) === 2);
}

/**
 * Resolve an album item for PLG_getItemInfo consumers such as IndexNow/Hub.
 *
 * @param int    $album_id
 * @param string $what
 * @param int    $uid
 * @return mixed
 */
function MG_getAlbumItemInfo180($album_id, $what, $uid = 0)
{
    global $_TABLES, $_MG_CONF;

    $album_id = intval($album_id);
    if ($album_id <= 0) {
        return false;
    }

    $result = DB_query(
        "SELECT album_id, album_title, album_desc, last_update, hidden, perm_anon "
        . "FROM {$_TABLES['mg_albums']} WHERE album_id=" . $album_id . " LIMIT 1"
    );
    if (!$result || DB_numRows($result) !== 1) {
        return false;
    }

    $row = DB_fetchArray($result);
    if ((int) $uid === 1 && ((int) $row['hidden'] !== 0 || (((int) $row['perm_anon']) & 2) !== 2)) {
        return false;
    }

    $url = $_MG_CONF['site_url'] . '/album.php?aid=' . $album_id;
    $properties = explode(',', $what);
    $values = array();

    foreach ($properties as $property) {
        $property = trim($property);
        switch ($property) {
            case 'id':
                $values[$property] = MG_albumItemId180($album_id);
                break;
            case 'url':
                $values[$property] = $url;
                break;
            case 'title':
                $values[$property] = $row['album_title'];
                break;
            case 'description':
            case 'excerpt':
            case 'raw-description':
                $values[$property] = $row['album_desc'];
                break;
            case 'date-modified':
                $values[$property] = intval($row['last_update']);
                break;
            default:
                $values[$property] = '';
                break;
        }
    }

    if (count($properties) === 1) {
        return isset($values[$properties[0]]) ? $values[$properties[0]] : '';
    }

    /*
     * Geeklog's historical PLG_getItemInfo() contract returns values for a
     * single item as a numerically indexed array in the same order as the
     * requested property list. Consumers such as XMLSitemap still rely on
     * offsets 0..n even on Geeklog 2.2.2.
     */
    $ordered = array();
    foreach ($properties as $property) {
        $property = trim($property);
        $ordered[] = isset($values[$property]) ? $values[$property] : '';
    }

    return $ordered;
}

/**
 * Resolve deterministic MediaGallery URLs, including deleted albums.
 *
 * @param string $id
 * @return string
 */
function MG_itemToURL180($id)
{
    global $_MG_CONF;

    $item = MG_parseItemId180($id);
    if ($item['type'] === 'album') {
        return $_MG_CONF['site_url'] . '/album.php?aid=' . intval($item['id']);
    }

    return $_MG_CONF['site_url'] . '/media.php?f=0&sort=0&s=' . $item['id'];
}
