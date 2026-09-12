<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | moderate.php                                                             |
// |                                                                          |
// | Moderation routines                                                      |
// +--------------------------------------------------------------------------+
// | Copyright (C) 2015 by the following authors:                             |
// |                                                                          |
// | Yoshinori Tahara       taharaxp AT gmail DOT com                         |
// |                                                                          |
// | Based on the Media Gallery Plugin for glFusion CMS                       |
// | Copyright (C) 2002-2009 by the following authors:                        |
// |                                                                          |
// | Mark R. Evans          mark AT glfusion DOT org                          |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

/**
 * Resolve and validate one queued MediaGallery submission.
 *
 * Geeklog's moderation controller already protects its POST mutations with a
 * CSRF token. These callbacks still revalidate authorization and object
 * membership so they remain safe if called from another plugin path later.
 *
 * @param  string $media_id
 * @return array|false
 */
function MG_getModerationSubmission($media_id)
{
    global $_TABLES;

    if (!SEC_hasRights('mediagallery.admin')) {
        COM_errorLog('MediaGallery: moderation mutation rejected for a non-admin user.', 1);
        return false;
    }

    $media_id = COM_applyFilter($media_id);
    if ($media_id === '') {
        return false;
    }

    $mid = DB_escapeString($media_id);
    $sql = "SELECT q.*, aq.album_id, aq.media_order "
         . "FROM {$_TABLES['mg_mediaqueue']} AS q "
         . "INNER JOIN {$_TABLES['mg_media_album_queue']} AS aq "
         . "ON aq.media_id=q.media_id "
         . "INNER JOIN {$_TABLES['mg_albums']} AS a "
         . "ON a.album_id=aq.album_id "
         . "WHERE q.media_id='" . $mid . "'";
    $result = DB_query($sql, 1);

    if (DB_error() || DB_numRows($result) !== 1) {
        COM_errorLog('MediaGallery: moderation mutation rejected for invalid or ambiguous media id ' . $media_id, 1);
        return false;
    }

    return DB_fetchArray($result);
}

function MG_approveSubmission($media_id)
{
    global $_CONF, $_TABLES, $LANG_MG01;

    $submission = MG_getModerationSubmission($media_id);
    if ($submission === false) {
        return false;
    }

    $media_id = COM_applyFilter($submission['media_id']);
    $mid = DB_escapeString($media_id);
    $album_id = (int) $submission['album_id'];
    $media_order = (int) $submission['media_order'];

    if (DB_count($_TABLES['mg_media'], 'media_id', $media_id) > 0 ||
        DB_count($_TABLES['mg_media_albums'], array('album_id', 'media_id'), array($album_id, $media_id)) > 0) {
        COM_errorLog('MediaGallery: moderation approval rejected because media ' . $media_id . ' already exists.', 1);
        return false;
    }

    // mg_media and mg_mediaqueue intentionally share the same schema. Copy
    // the queued record first, then bind it to the validated queued album.
    DB_query(
        "INSERT INTO {$_TABLES['mg_media']} "
        . "SELECT * FROM {$_TABLES['mg_mediaqueue']} WHERE media_id='" . $mid . "'",
        1
    );
    if (DB_error()) {
        COM_errorLog('MediaGallery: unable to promote queued media ' . $media_id . ' into the media table.', 1);
        return false;
    }

    DB_save(
        $_TABLES['mg_media_albums'],
        'album_id, media_id, media_order',
        $album_id . ", '" . $mid . "', " . $media_order
    );
    if (DB_error()) {
        DB_delete($_TABLES['mg_media'], 'media_id', $mid);
        COM_errorLog('MediaGallery: unable to bind approved media ' . $media_id . ' to album ' . $album_id . '.', 1);
        return false;
    }

    DB_delete($_TABLES['mg_media_album_queue'], 'media_id', $mid);
    DB_delete($_TABLES['mg_mediaqueue'], 'media_id', $mid);

    require_once $_CONF['path'] . 'plugins/mediagallery/include/sort.php';
    MG_SortMedia($album_id);

    // Recalculate instead of incrementing a potentially stale counter.
    $media_count = DB_count($_TABLES['mg_media_albums'], 'album_id', $album_id);
    DB_change($_TABLES['mg_albums'], 'media_count', $media_count, 'album_id', $album_id);
    MG_updateAlbumLastUpdate($album_id);

    $album_cover = DB_getItem($_TABLES['mg_albums'], 'album_cover', 'album_id=' . $album_id);
    if ($album_cover == -1 && (int) $submission['media_type'] === 0) {
        DB_change(
            $_TABLES['mg_albums'],
            'album_cover_filename',
            $submission['media_filename'],
            'album_id',
            $album_id
        );
    }

    PLG_itemSaved($media_id, 'mediagallery');

    // Email the uploader that the item has been approved.
    $owner_uid = (int) $submission['media_user_id'];
    COM_clearSpeedlimit(600, 'mgapprove');
    $last = COM_checkSpeedlimit('mgapprove');
    if ($last == 0 && $owner_uid > 0) {
        $result = DB_query(
            "SELECT username, fullname, email FROM {$_TABLES['users']} WHERE uid=" . $owner_uid
        );
        if (DB_numRows($result) === 1) {
            list($username, $fullname, $email) = DB_fetchArray($result);
            if ($email != '') {
                $subject = $LANG_MG01['upload_approved'];
                $body  = $LANG_MG01['upload_approved'];
                $body .= '<br' . XHTML . '><br' . XHTML . '>';
                $body .= $LANG_MG01['thanks_submit'];
                $body .= '<br' . XHTML . '><br' . XHTML . '>';
                $body .= $_CONF['site_name'] . '<br' . XHTML . '>';
                $body .= $_CONF['site_url'] . '<br' . XHTML . '>';
                $to = COM_formatEmailAddress($username, $email);

                if (!COM_mail($to, $subject, $body, '', true)) {
                    COM_errorLog('Media Gallery Error - Unable to send queue notification email');
                }
                COM_updateSpeedlimit('mgapprove');
            }
        }
    }

    require_once $_CONF['path'] . 'plugins/mediagallery/include/rssfeed.php';
    MG_buildFullRSS();
    MG_buildAlbumRSS($album_id);

    return true;
}

function MG_deleteSubmission($media_id)
{
    global $_TABLES, $_MG_CONF;

    $submission = MG_getModerationSubmission($media_id);
    if ($submission === false) {
        return false;
    }

    $media_id = COM_applyFilter($submission['media_id']);
    $mid = DB_escapeString($media_id);
    $filename = $submission['media_filename'];
    $mime_ext = $submission['media_mime_ext'];

    if ($filename === '') {
        COM_errorLog('MediaGallery: queued media ' . $media_id . ' has no filename; refusing destructive cleanup.', 1);
        return false;
    }

    DB_delete($_TABLES['mg_media_album_queue'], 'media_id', $mid);
    DB_delete($_TABLES['mg_mediaqueue'], 'media_id', $mid);
    DB_delete($_TABLES['mg_playback_options'], 'media_id', $mid);

    // Remove generated media files. Moderated uploads already live in the
    // persistent media tree, so rejection must also clean every generated
    // thumbnail size used by MG_createThumbnail().
    $bucket = $filename[0];
    $thumbSuffixes = array('', '_100', '_150', '_200', '_100x100', '_150x150', '_200x200');
    foreach ($_MG_CONF['validExtensions'] as $ext) {
        foreach ($thumbSuffixes as $suffix) {
            @unlink(
                $_MG_CONF['path_mediaobjects'] . 'tn/' . $bucket . '/'
                . $filename . $suffix . $ext
            );
        }
        @unlink(
            $_MG_CONF['path_mediaobjects'] . 'disp/' . $bucket . '/'
            . $filename . $ext
        );
    }

    if ($mime_ext !== '') {
        @unlink($_MG_CONF['path_mediaobjects'] . 'orig/' . $bucket . '/' . $filename . '.' . $mime_ext);
    }

    return true;
}
?>