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
    global $_TABLES, $_MG_CONF, $_USER;

    $album_id = intval($album_id);
    if ($album_id <= 0) {
        return false;
    }

    $effective_uid = (int) $uid;
    if ($effective_uid <= 0) {
        $effective_uid = isset($_USER['uid']) ? (int) $_USER['uid'] : 1;
    }

    $sql = "SELECT album_id, album_title, album_desc, last_update, hidden, "
         . "owner_id, group_id, perm_owner, perm_group, perm_members, perm_anon "
         . "FROM {$_TABLES['mg_albums']} WHERE album_id=" . $album_id;

    $is_current_admin = isset($_USER['uid'])
        && (int) $_USER['uid'] === $effective_uid
        && SEC_hasRights('mediagallery.admin');

    if (!$is_current_admin) {
        $sql .= " AND hidden = 0";
        $sql .= COM_getPermSQL('AND', $effective_uid, 2);
    }

    $sql .= " LIMIT 1";

    $result = DB_query($sql);
    if (!$result || DB_numRows($result) !== 1) {
        return false;
    }

    $row = DB_fetchArray($result);
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
            case 'canonical_url':
                $values[$property] = $url;
                break;
            case 'title':
                $values[$property] = $row['album_title'];
                break;
            case 'description':
            case 'excerpt':
                $values[$property] = PLG_replaceTags($row['album_desc']);
                break;
            case 'raw-description':
                $values[$property] = $row['album_desc'];
                break;
            case 'date-created':
            case 'date-modified':
                $values[$property] = intval($row['last_update']);
                break;
            case 'type':
                $values[$property] = 'mediagallery';
                break;
            case 'subtype':
                $values[$property] = 'album';
                break;
            case 'album_id':
                $values[$property] = $album_id;
                break;
            case 'uid':
                $values[$property] = isset($row['owner_id']) ? (int) $row['owner_id'] : 0;
                break;
            case 'status':
                $values[$property] = 1;
                break;
            default:
                $values[$property] = '';
                break;
        }
    }

    if (count($properties) === 1) {
        return isset($values[$properties[0]]) ? $values[$properties[0]] : '';
    }

    $ordered = array();
    foreach ($properties as $property) {
        $property = trim($property);
        $ordered[] = isset($values[$property]) ? $values[$property] : '';
    }

    return $ordered;
}

/**
 * Return a permission-filtered collection of albums for generic consumers.
 *
 * @param string $what
 * @param int    $uid
 * @param array  $options
 * @return array
 */
function MG_getAlbumCollection180($what, $uid = 0, $options = array())
{
    global $_TABLES, $_MG_CONF, $_USER;

    $options = is_array($options) ? $options : array();
    $effective_uid = (int) $uid;
    if ($effective_uid <= 0) {
        $effective_uid = isset($_USER['uid']) ? (int) $_USER['uid'] : 1;
    }

    $properties = array();
    foreach (explode(',', (string) $what) as $property) {
        $property = trim($property);
        if ($property !== '' && !in_array($property, $properties, true)) {
            $properties[] = $property;
        }
    }
    if (empty($properties)) {
        return array();
    }

    $limit = isset($options['limit']) ? (int) $options['limit'] : 50;
    if ($limit < 1) {
        $limit = 50;
    } elseif ($limit > 500) {
        $limit = 500;
    }

    $sql = "SELECT album_id, album_title, album_desc, last_update, hidden, "
         . "owner_id, group_id, perm_owner, perm_group, perm_members, perm_anon "
         . "FROM {$_TABLES['mg_albums']} WHERE album_id > 0";

    $is_current_admin = isset($_USER['uid'])
        && (int) $_USER['uid'] === $effective_uid
        && SEC_hasRights('mediagallery.admin');

    if (!$is_current_admin) {
        $sql .= " AND hidden = 0";
        $sql .= COM_getPermSQL('AND', $effective_uid, 2);
    }

    if (isset($options['since']) && $options['since'] !== '' && $options['since'] !== null) {
        $since = $options['since'];
        if (is_numeric($since)) {
            $since_ts = (int) $since;
        } else {
            $since_ts = strtotime((string) $since);
            if ($since_ts === false) {
                $since_ts = 0;
            }
        }

        if ($since_ts > 0) {
            $sql .= " AND last_update >= " . $since_ts;
        }
    }

    $order = isset($options['order'])
        ? strtolower(trim((string) $options['order']))
        : 'modified-desc';

    switch ($order) {
        case 'modified-asc':
        case 'created-asc':
            $sql .= " ORDER BY last_update ASC, album_id ASC";
            break;
        case 'created-desc':
        case 'modified-desc':
        default:
            $sql .= " ORDER BY last_update DESC, album_id DESC";
            break;
    }

    $sql .= " LIMIT " . $limit;

    $result = DB_query($sql);
    $retval = array();

    while ($row = DB_fetchArray($result)) {
        $album_id = (int) $row['album_id'];
        $url = $_MG_CONF['site_url'] . '/album.php?aid=' . $album_id;
        $props = array();

        foreach ($properties as $property) {
            switch ($property) {
                case 'id':
                    $props[$property] = MG_albumItemId180($album_id);
                    break;
                case 'url':
                case 'canonical_url':
                    $props[$property] = $url;
                    break;
                case 'title':
                    $props[$property] = $row['album_title'];
                    break;
                case 'description':
                case 'excerpt':
                    $props[$property] = PLG_replaceTags($row['album_desc']);
                    break;
                case 'raw-description':
                    $props[$property] = $row['album_desc'];
                    break;
                case 'date-created':
                case 'date-modified':
                    $props[$property] = (int) $row['last_update'];
                    break;
                case 'type':
                    $props[$property] = 'mediagallery';
                    break;
                case 'subtype':
                    $props[$property] = 'album';
                    break;
                case 'album_id':
                    $props[$property] = $album_id;
                    break;
                case 'uid':
                    $props[$property] = isset($row['owner_id']) ? (int) $row['owner_id'] : 0;
                    break;
                case 'status':
                    $props[$property] = 1;
                    break;
                default:
                    $props[$property] = '';
                    break;
            }
        }

        $mapped = array();
        foreach ($props as $key => $value) {
            if ($value !== '') {
                $mapped[$key] = $value;
            }
        }
        $retval[] = $mapped;
    }

    return $retval;
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


/**
 * Collect public MediaGallery URLs for XMLSitemap.
 *
 * Keep sitemap generation independent from the generic getiteminfo collection
 * API. Media items may belong to several albums, so URLs are deduplicated
 * explicitly. Hidden or non-readable albums are excluded for anonymous users.
 *
 * @param int $uid User id used for permission checks
 * @param int $limit Maximum number of items, 0 = unlimited
 * @return array
 */
function plugin_collectSitemapItems_mediagallery($uid = 1, $limit = 0)
{
    global $_MG_CONF, $_TABLES, $_PLUGINS;

    /*
     * XMLSitemap can rebuild during a plugin state change before Geeklog has
     * refreshed $_PLUGINS. Avoid querying MediaGallery in that transient state.
     */
    if (!is_array($_PLUGINS) || !in_array('mediagallery', $_PLUGINS, true)) {
        return array();
    }

    $uid = (int) $uid;
    $limit = (int) $limit;
    $items = array();
    $seen = array();

    $append = function ($url, $modified, $priority, $frequency) use (&$items, &$seen, $limit) {
        if ($url === '' || isset($seen[$url])) {
            return false;
        }

        $entry = array(
            'url' => $url,
            'priority' => $priority,
            'change-freq' => $frequency
        );
        if (!empty($modified)) {
            $entry['date-modified'] = (int) $modified;
        }

        $seen[$url] = true;
        $items[] = $entry;

        return ($limit > 0 && count($items) >= $limit);
    };

    // MediaGallery landing page.
    if ($append($_MG_CONF['site_url'] . '/index.php', 0, 0.6, 'weekly')) {
        return $items;
    }

    // Public albums.
    $sql = "SELECT a.album_id, a.last_update "
         . "FROM {$_TABLES['mg_albums']} a "
         . "WHERE a.album_id > 0 AND a.hidden = 0 "
         . COM_getPermSQL('AND', $uid, 2, 'a')
         . " ORDER BY a.album_id ASC";
    $result = DB_query($sql);

    while ($row = DB_fetchArray($result)) {
        $url = $_MG_CONF['site_url'] . '/album.php?aid=' . (int) $row['album_id'];
        if ($append($url, $row['last_update'], 0.6, 'weekly')) {
            return $items;
        }
    }

    // Public media. DISTINCT avoids duplicates when one media item is in
    // several albums; the URL itself is also deduplicated as a final guard.
    $sql = "SELECT DISTINCT m.media_id, m.media_upload_time "
         . "FROM {$_TABLES['mg_media']} m "
         . "INNER JOIN {$_TABLES['mg_media_albums']} ma ON m.media_id=ma.media_id "
         . "INNER JOIN {$_TABLES['mg_albums']} a ON ma.album_id=a.album_id "
         . "WHERE m.media_id<>'' AND a.hidden=0 "
         . COM_getPermSQL('AND', $uid, 2, 'a')
         . " ORDER BY m.media_upload_time DESC, m.media_id ASC";
    $result = DB_query($sql);

    while ($row = DB_fetchArray($result)) {
        $media_id = (string) $row['media_id'];
        if ($media_id === '') {
            continue;
        }

        $modified = 0;
        if (!empty($row['media_upload_time'])) {
            $modified = strtotime($row['media_upload_time']);
            if ($modified === false) {
                $modified = 0;
            }
        }

        $url = $_MG_CONF['site_url']
             . '/media.php?f=0&sort=0&s=' . rawurlencode($media_id);

        if ($append($url, $modified, 0.5, 'monthly')) {
            break;
        }
    }

    return $items;
}
