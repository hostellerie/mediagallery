<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | services.inc.php                                                         |
// |                                                                          |
// | Internal/public service API for MediaGallery                             |
// +--------------------------------------------------------------------------+

if (stripos($_SERVER['PHP_SELF'], basename(__FILE__)) !== false) {
    die('This file can not be used on its own.');
}

/**
 * MediaGallery exposes read-only services through Geeklog's native service
 * mechanism. At present only album_list is implemented.
 *
 * @return bool
 */
function plugin_wsEnabled_mediagallery()
{
    return true;
}

/**
 * Add one album and, optionally, its descendants to a service result.
 *
 * @param int   $albumId
 * @param int   $depth
 * @param bool  $recursive
 * @param bool  $visibleOnly
 * @param array $output
 * @return void
 */
function MG_serviceCollectAlbumTree180($albumId, $depth, $recursive, $visibleOnly, &$output)
{
    global $_MG_CONF;

    $album = new mgAlbum(intval($albumId));
    if (!$album->valid || $album->access <= 0) {
        return;
    }

    if ($visibleOnly && $album->hidden && $album->access < 3) {
        return;
    }

    $output[] = array(
        'id'       => intval($album->id),
        'title'    => strip_tags($album->title),
        'parent'   => intval($album->parent),
        'owner_id' => intval($album->owner_id),
        'hidden'   => (bool) $album->hidden,
        'access'   => intval($album->access),
        'depth'    => intval($depth),
        'url'      => $_MG_CONF['site_url'] . '/album.php?aid=' . intval($album->id),
    );

    if (!$recursive) {
        return;
    }

    $children = $visibleOnly ? $album->getChildrenVisible() : $album->getChildren();
    foreach ($children as $childId) {
        MG_serviceCollectAlbumTree180($childId, $depth + 1, true, $visibleOnly, $output);
    }
}

/**
 * Return an album tree through Geeklog's native PLG_invokeService API.
 *
 * Supported arguments:
 * - uid: user whose member album tree is requested; defaults to current user
 * - root: 'member' (default) or a numeric album id
 * - recursive: include descendants, default true
 * - visible: omit albums not visible to the current caller, default true
 *
 * @param array $args
 * @param array $output
 * @param array $svc_msg
 * @return int
 */
function service_album_list_mediagallery($args, &$output, &$svc_msg)
{
    global $_TABLES, $_USER, $_MG_CONF;

    require_once __DIR__ . '/include/classAlbum.php';

    $output = array();
    $svc_msg = array();

    $currentUid = isset($_USER['uid']) ? intval($_USER['uid']) : 1;
    $uid = isset($args['uid']) ? intval($args['uid']) : $currentUid;
    $root = isset($args['root']) ? $args['root'] : 'member';
    $recursive = !isset($args['recursive']) || (bool) $args['recursive'];
    $visibleOnly = !isset($args['visible']) || (bool) $args['visible'];

    if ($uid < 1) {
        $svc_msg['error_desc'] = 'Invalid user id.';
        return PLG_RET_ERROR;
    }

    // A user may inspect their own tree. Administrators may request another
    // user's tree for administrative/plugin integration purposes.
    if ($uid !== $currentUid && !SEC_hasRights('mediagallery.admin')) {
        $svc_msg['error_desc'] = 'Not authorized to list albums for this user.';
        return PLG_RET_AUTH_FAILED;
    }

    if ($root === 'member' || $root === '') {
        if (empty($_MG_CONF['member_albums']) || empty($_MG_CONF['member_album_root'])) {
            return PLG_RET_OK;
        }

        $memberRoot = intval($_MG_CONF['member_album_root']);
        $sql = "SELECT album_id FROM {$_TABLES['mg_albums']} "
             . "WHERE owner_id = " . intval($uid)
             . " AND album_parent = " . $memberRoot
             . " ORDER BY album_order DESC";
        $result = DB_query($sql);

        while ($A = DB_fetchArray($result)) {
            MG_serviceCollectAlbumTree180(
                intval($A['album_id']),
                0,
                $recursive,
                $visibleOnly,
                $output
            );
        }

        return PLG_RET_OK;
    }

    if (!is_numeric($root)) {
        $svc_msg['error_desc'] = 'Invalid album root.';
        return PLG_RET_ERROR;
    }

    $rootId = intval($root);
    if ($rootId < 0) {
        $svc_msg['error_desc'] = 'Invalid album root.';
        return PLG_RET_ERROR;
    }

    $rootAlbum = new mgAlbum($rootId);
    if (!$rootAlbum->valid || ($rootId > 0 && $rootAlbum->access <= 0)) {
        $svc_msg['error_desc'] = 'Album not found or not accessible.';
        return PLG_RET_ERROR;
    }

    $children = $visibleOnly ? $rootAlbum->getChildrenVisible() : $rootAlbum->getChildren();
    foreach ($children as $childId) {
        MG_serviceCollectAlbumTree180($childId, 0, $recursive, $visibleOnly, $output);
    }

    return PLG_RET_OK;
}
