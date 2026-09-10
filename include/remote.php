<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | remote.php                                                               |
// |                                                                          |
// | Remote Media routines                                                    |
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
// |                                                                          |
// | This program is free software; you can redistribute it and/or            |
// | modify it under the terms of the GNU General Public License              |
// | as published by the Free Software Foundation; either version 2           |
// | of the License, or (at your option) any later version.                   |
// |                                                                          |
// | This program is distributed in the hope that it will be useful,          |
// | but WITHOUT ANY WARRANTY; without even the implied warranty of           |
// | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            |
// | GNU General Public License for more details.                             |
// |                                                                          |
// | You should have received a copy of the GNU General Public License        |
// | along with this program; if not, write to the Free Software Foundation,  |
// | Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.          |
// |                                                                          |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

require_once $_CONF['path'] . 'plugins/mediagallery/include/lib-upload.php';

/**
 * Remote Media Import.
 *
 * @param int $album_id
 * @return string
 */
function MG_remoteUpload($album_id)
{
    global $_TABLES, $_MG_CONF, $LANG_MG01, $LANG_MG03, $LANG_MG07;

    $retval = '';
    $root_album = new mgAlbum(0);
    $album_selectbox = MG_buildAlbumBox($root_album, $album_id, 3, -1, 'upload');

    $catRow = array();
    $result = DB_query("SELECT * FROM {$_TABLES['mg_category']} ORDER BY cat_id ASC");
    $nRows = DB_numRows($result);
    for ($i = 0; $i < $nRows; $i++) {
        $catRow[$i] = DB_fetchArray($result);
    }

    $cRows = count($catRow);
    $cat_select = '';
    if ($cRows > 0) {
        $cat_select = '<select name="cat_id[]">';
        $cat_select .= '<option value="0">' . $LANG_MG01['no_category'] . '</option>';
        for ($i = 0; $i < $cRows; $i++) {
            $cat_select .= '<option value="' . $catRow[$i]['cat_id'] . '">' . $catRow[$i]['cat_name'] . '</option>';
        }
        $cat_select .= '</select>';
    }

    $T = COM_newTemplate(MG_getTemplatePath($album_id));
    $T->set_file('mupload', 'remoteupload.thtml');
    $T->set_var(array(
        'start_block' => COM_startBlock($LANG_MG03['upload_media']),
        'end_block' => COM_endBlock(),
        'navbar' => MG_navbar($LANG_MG01['remote_media'], $album_id),
        's_form_action' => $_MG_CONF['site_url'] . '/admin.php',
        'lang_remote_media_type' => $LANG_MG01['remote_media_type'],
        'lang_remote_help' => $LANG_MG01['remote_help'],
        'lang_flv_stream' => $LANG_MG01['flv_stream'],
        'lang_embed' => $LANG_MG01['embed'],
        'lang_thumbnail' => $LANG_MG01['thumbnail'],
        'lang_remote_thumbnail' => $LANG_MG01['remote_thumbnail'],
        'lang_remote_url' => $LANG_MG01['remote_url'],
        'lang_width' => $LANG_MG07['width'],
        'lang_height' => $LANG_MG07['height'],
        'lang_media_upload' => $LANG_MG01['upload_media'],
        'lang_caption' => $LANG_MG01['title'],
        'lang_file' => $LANG_MG01['file'],
        'lang_description' => $LANG_MG01['description'],
        'lang_attached_tn' => $LANG_MG01['attached_thumbnail'],
        'lang_save' => $LANG_MG01['save'],
        'lang_cancel' => $LANG_MG01['cancel'],
        'lang_reset' => $LANG_MG01['reset'],
        'lang_category' => ($cRows > 0 ? $LANG_MG01['category'] : ''),
        'lang_keywords' => $LANG_MG01['keywords'],
        'lang_destination_album' => $LANG_MG01['destination_album'],
        'lang_file_number' => $LANG_MG01['file_number'],
        'lang_jpg' => $LANG_MG01['jpg'],
        'lang_gif' => $LANG_MG01['gif'],
        'lang_png' => $LANG_MG01['png'],
        'lang_bmp' => $LANG_MG01['bmp'],
        'cat_select' => $cat_select,
        'album_id' => $album_id,
        'action' => 'remoteupload',
        'album_select' => $album_selectbox,
        'site_url' => $_MG_CONF['site_url'],
        'gltoken_name' => CSRF_TOKEN,
        'gltoken' => SEC_createToken(),
    ));

    if ($_MG_CONF['enable_remote_images'] == 1) {
        $T->set_var('enable_remote_images', 'true');
    } else {
        $T->set_var('enable_remote_images', '');
    }

    $retval .= $T->finish($T->parse('output', 'mupload'));
    return $retval;
}

/**
 * Save remote media entries.
 *
 * @param int $album_id
 * @return string
 */
function MG_saveRemoteUpload($album_id)
{
    global $_CONF, $_TABLES, $_MG_CONF, $LANG_MG01, $LANG_MG02, $LANG_MG03;

    if (!SEC_checkToken()) {
        COM_errorLog('MediaGallery: remote media upload rejected because of an invalid CSRF token.', 1);
        return COM_showMessageText($LANG_MG02['generic_error']);
    }

    $retval = COM_startBlock($LANG_MG03['upload_results'], '',
                             COM_getBlockTemplate('_admin_block', 'header'));
    $statusMsg = '';
    $file = isset($_FILES['thumbnail']) ? $_FILES['thumbnail'] : array();
    $successfull_upload = 0;

    $remoteURL = (isset($_POST['remoteurl']) && is_array($_POST['remoteurl']))
        ? $_POST['remoteurl'] : array();
    $totalUploads = count($remoteURL);

    for ($i = 0; $i < $totalUploads; $i++) {
        $errorFound = 0;
        if ($remoteURL[$i] == '') {
            continue;
        }

        $URL = COM_stripslashes($remoteURL[$i]);
        $uploadType = isset($_POST['type'][$i]) ? COM_applyFilter($_POST['type'][$i]) : -1;
        $caption = isset($_POST['caption'][$i]) ? COM_stripslashes($_POST['caption'][$i]) : '';
        $description = isset($_POST['description'][$i]) ? COM_stripslashes($_POST['description'][$i]) : '';
        $keywords = isset($_POST['keywords'][$i]) ? COM_stripslashes($_POST['keywords'][$i]) : '';
        $category = isset($_POST['cat_id'][$i]) ? COM_applyFilter($_POST['cat_id'][$i], true) : 0;
        $thumbnail = isset($file['tmp_name'][$i]) ? $file['tmp_name'][$i] : '';
        $resolution_x = isset($_POST['width'][$i]) ? COM_applyFilter($_POST['width'][$i], true) : 0;
        $resolution_y = isset($_POST['height'][$i]) ? COM_applyFilter($_POST['height'][$i], true) : 0;

        if ($thumbnail != '') {
            $attachedThumbnail = 1;
        } else {
            $attachedThumbnail = 0;
            if (in_array($uploadType, array(4, 6, 7, 8)) && $_MG_CONF['enable_remote_images'] == 1) {
                if (!MG_validateRemoteFetchUrl180($URL)) {
                    COM_errorLog('MediaGallery: blocked unsafe remote image URL.', 1);
                    $statusMsg .= sprintf($LANG_MG02['invalid_remote_url'] . '<br>', $i);
                    continue;
                }
                $attachedThumbnail = 1;
                $thumbnail = $URL;
            }
        }

        switch ($uploadType) {
            case 0:
                $mimeType = 'video/x-flv';
                $urlParts = parse_url($URL);
                if (!is_array($urlParts) || empty($urlParts['scheme']) || empty($urlParts['path'])) {
                    $statusMsg .= sprintf($LANG_MG02['invalid_remote_url'] . '<br>', $i);
                    continue 2;
                }
                $pathParts = explode('/', $urlParts['path']);
                $ppCount = count($pathParts);
                $pPath = '';
                for ($x = 1; $x < $ppCount - 1; $x++) {
                    $pPath .= '/' . $pathParts[$x];
                }
                $videoFile = $pathParts[$ppCount - 1];
                if ($urlParts['scheme'] != 'rtmp' && $urlParts['scheme'] != 'rtsp') {
                    $statusMsg .= sprintf($LANG_MG02['invalid_remote_url'] . '<br>', $i);
                    return COM_showMessageText($statusMsg
                        . '  [ <a href=\'javascript:history.go(-1)\'>' . $LANG_MG02['go_back'] . '</a> ]');
                }
                break;

            case 1:
                $mimeType = 'video/quicktime';
                break;

            case 2:
                $mimeType = 'video/x-ms-asf';
                break;

            case 3:
                $mimeType = 'audio/mpeg';
                break;

            case 4:
                $mimeType = 'image/jpg';
                break;

            case 5:
                $mimeType = 'embed';
                $videoFile = 'Embedded Video';
                if (!preg_match('/embed/i', $URL) && !preg_match('/movie/i', $URL)) {
                    $statusMsg .= sprintf($LANG_MG02['invalid_embed_url'] . '<br>', $i);
                    return COM_showMessageText($statusMsg
                        . '  [ <a href=\'javascript:history.go(-1)\'>' . $LANG_MG02['go_back'] . '</a> ]');
                }
                break;

            case 6:
                $mimeType = 'image/gif';
                break;

            case 7:
                $mimeType = 'image/png';
                break;

            case 8:
                $mimeType = 'image/bmp';
                break;

            default:
                $fileNumber = $i + 1;
                return COM_showMessageText($LANG_MG01['file_number'] . ' ' . $fileNumber . ' - ' . $LANG_MG02['no_format']
                    . '  [ <a href=\'javascript:history.go(-1)\'>' . $LANG_MG02['go_back'] . '</a> ]');
        }

        if ($errorFound) {
            continue;
        }

        list($rc, $msg) = MG_getRemote(
            $URL,
            $mimeType,
            $album_id,
            $caption,
            $description,
            $keywords,
            $category,
            $attachedThumbnail,
            $thumbnail,
            $resolution_x,
            $resolution_y
        );

        $statusMsg .= (isset($videoFile) ? $videoFile : '') . ' ' . $msg . '<br' . XHTML . '>';
        if ($rc == true) {
            $successfull_upload++;
        }
    }

    if ($successfull_upload) {
        MG_notifyModerators180($album_id);
    }

    $dbCount = DB_count($_TABLES['mg_media_albums'], 'album_id', intval($album_id));
    $aCount = DB_getItem($_TABLES['mg_albums'], 'media_count', 'album_id=' . intval($album_id));
    if ($dbCount != $aCount) {
        DB_change($_TABLES['mg_albums'], 'media_count', $dbCount, 'album_id', intval($album_id));
        COM_errorLog("MediaGallery: Upload processing - Counts don't match - dbCount = " . $dbCount . " aCount = " . $aCount);
    }

    $T = COM_newTemplate(MG_getTemplatePath($album_id));
    $T->set_file('mupload', 'useruploadstatus.thtml');
    $T->set_var('site_url', $_CONF['site_url']);
    $T->set_var('status_message', $statusMsg);

    $tmp = $_MG_CONF['site_url'] . '/album.php?aid=' . $album_id . '&page=1';
    $redirect = sprintf($LANG_MG03['album_redirect'], $tmp);
    $T->set_var('redirect', $redirect);
    $retval .= $T->finish($T->parse('output', 'mupload'));
    $retval .= COM_endBlock(COM_getBlockTemplate('_admin_block', 'footer'));
    return $retval;
}

function MG_getRemote($URL, $mimeType, $album_id, $caption, $description, $keywords, $category, $attachedThumbnail, $thumbnail, $resolution_x, $resolution_y)
{
    global $_CONF, $_MG_CONF, $_USER, $_TABLES, $LANG_MG00, $LANG_MG01, $LANG_MG02;

    if ($_MG_CONF['verbose']) {
        COM_errorLog('MG Upload: Entering MG_getRemote()');
        COM_errorLog('MG Upload: URL to process: ' . htmlentities($URL));
    }

    $album = new mgAlbum($album_id);
    $root_album = new mgAlbum(0);

    $resolution_x = 0;
    $resolution_y = 0;
    $urlArray = parse_url($URL);

    $sql = "SELECT * FROM {$_TABLES['mg_albums']} WHERE album_id=" . intval($album_id);
    $aResult = DB_query($sql);
    $aRows = DB_numRows($aResult);
    if ($aRows != 1) {
        return array(false, $LANG_MG02['album_nonexist']);
    }
    $albumInfo = DB_fetchArray($aResult);

    $access = SEC_hasAccess(
        $albumInfo['owner_id'],
        $albumInfo['group_id'],
        $albumInfo['perm_owner'],
        $albumInfo['perm_group'],
        $albumInfo['perm_members'],
        $albumInfo['perm_anon']
    );

    if ($access != 3 && !$root_album->owner_id && $albumInfo['member_uploads'] == 0) {
        COM_errorLog("Someone has tried to illegally upload to an album in Media Gallery. "
            . "User id: {$_USER['uid']}, Username: {$_USER['username']}, IP: {$_SERVER['REMOTE_ADDR']}", 1);
        return array(false, $LANG_MG00['access_denied_msg']);
    }

    $errors = 0;
    $errMsg = '';

    sleep(1);
    $new_media_id = COM_makesid();
    $media_time = time();
    $media_upload_time = time();
    $media_user_id = $_USER['uid'];

    switch ($mimeType) {
        case 'embed':
            $format_type = MG_EMB;
            $mimeExt = 'flv';
            $mediaType = 5;
            break;
        case 'image/gif':
            $format_type = MG_GIF;
            $mimeExt = 'gif';
            $mediaType = 0;
            break;
        case 'image/jpg':
            $format_type = MG_JPG;
            $mimeExt = 'jpg';
            $mediaType = 0;
            break;
        case 'image/png':
            $format_type = MG_PNG;
            $mimeExt = 'png';
            $mediaType = 0;
            break;
        case 'image/bmp':
            $format_type = MG_BMP;
            $mimeExt = 'bmp';
            $mediaType = 0;
            break;
        case 'application/x-shockwave-flash':
            $format_type = MG_SWF;
            $mimeExt = 'swf';
            $mediaType = 1;
            break;
        case 'video/quicktime':
            $format_type = MG_MOV;
            $mimeExt = 'mov';
            $mediaType = 1;
            break;
        case 'video/x-flv':
            $format_type = MG_RFLV;
            $mimeExt = 'flv';
            $mediaType = 1;
            break;
        case 'video/x-ms-asf':
            $format_type = MG_ASF;
            $mimeExt = 'asf';
            $mediaType = 1;
            break;
        case 'audio/mpeg':
            $format_type = MG_MP3;
            $mimeExt = 'mp3';
            $mediaType = 2;
            break;
        case 'audio/x-ms-wma':
            $format_type = MG_ASF;
            $mimeExt = 'wma';
            $mediaType = 2;
            break;
        default:
            return array(false, $LANG_MG02['format_not_allowed']);
    }

    if (!($album->valid_formats & $format_type)) {
        return array(false, $LANG_MG02['format_not_allowed']);
    }

    clearstatcache();
    do {
        $media_filename = md5(uniqid(rand()));
    } while (MG_file_exists($media_filename));

    $disp_media_filename = $media_filename . '.' . $mimeExt;

    if ($_MG_CONF['verbose']) {
        COM_errorLog('MG Upload: Stored filename is : ' . $disp_media_filename);
        COM_errorLog('MG Upload: Mime Type: ' . $mimeType);
    }

    $media_orig = $_MG_CONF['path_mediaobjects'] . 'orig/' . $media_filename[0] . '/' . $media_filename . '.' . $mimeExt;
    $media_time = time();
    touch($media_orig);

    if ($errors) {
        COM_errorLog('MG Upload: Problem uploading a media object');
        return array(false, $errMsg);
    }

    if ($_MG_CONF['verbose']) {
        COM_errorLog('MG Upload: attachedThumbnail: ' . $attachedThumbnail);
        COM_errorLog('MG Upload: thumbnail: ' . $thumbnail);
    }

    if ($attachedThumbnail == 1 && $thumbnail != '') {
        if (preg_match('/^https?:\/\//i', $thumbnail)) {
            if (!MG_validateRemoteFetchUrl180($thumbnail)) {
                COM_errorLog('MediaGallery: blocked unsafe remote thumbnail URL.', 1);
                return array(false, $LANG_MG02['invalid_remote_url']);
            }

            $tmp_thumbnail = $_MG_CONF['tmp_path'] . $media_filename . '.jpg';
            $rc = MG_getRemoteThumbnail($thumbnail, $tmp_thumbnail);
            $tmp_image_size = @getimagesize($tmp_thumbnail);
            if ($tmp_image_size != false) {
                $resolution_x = $tmp_image_size[0];
                $resolution_y = $tmp_image_size[1];
            }
            $thumbnail = $tmp_thumbnail;
        } else {
            $rc = true;
        }

        if ($rc == true) {
            $saveThumbnailName = $_MG_CONF['path_mediaobjects'] . 'tn/' . $media_filename[0] . '/tn_' . $media_filename;
            MG_attachThumbnail($album_id, $thumbnail, $saveThumbnailName);
        }
    }

    if ($_MG_CONF['htmlallowed'] != 1) {
        $media_desc = DB_escapeString(htmlspecialchars(strip_tags(COM_checkWords(COM_killJS($description)))));
        $media_caption = DB_escapeString(htmlspecialchars(strip_tags(COM_checkWords(COM_killJS($caption)))));
        $media_keywords = DB_escapeString(htmlspecialchars(strip_tags(COM_checkWords(COM_killJS($keywords)))));
    } else {
        $media_desc = DB_escapeString(COM_checkHTML(COM_killJS($description)));
        $media_caption = DB_escapeString(COM_checkHTML(COM_killJS($caption)));
        $media_keywords = DB_escapeString(COM_checkHTML(COM_killJS($keywords)));
    }

    if ($albumInfo['moderate'] == 1 && !$root_album->owner_id) {
        $tableMedia = $_TABLES['mg_mediaqueue'];
        $tableMediaAlbum = $_TABLES['mg_media_album_queue'];
        $queue = 1;
    } else {
        $tableMedia = $_TABLES['mg_media'];
        $tableMediaAlbum = $_TABLES['mg_media_albums'];
        $queue = 0;
    }

    if (!is_array($urlArray) || !isset($urlArray['path'])) {
        $urlArray = array('path' => '');
    }
    $pathParts = explode('/', $urlArray['path']);
    $ppCount = count($pathParts);
    $pPath = '';
    for ($i = 1; $i < $ppCount - 1; $i++) {
        $pPath .= '/' . $pathParts[$i];
    }
    $videoFile = $pathParts[$ppCount - 1];

    $original_filename = ($mediaType != 5) ? $videoFile : '';

    if (($resolution_x == 0 || $resolution_y == 0) && ($mediaType != 0)) {
        $resolution_x = 320;
        $resolution_y = 240;
    }

    $remoteURL = DB_escapeString($URL);

    $sql = "INSERT INTO " . $tableMedia . " (media_id,media_filename,media_original_filename,media_mime_ext,media_exif,mime_type,media_title,media_desc,media_keywords,media_time,media_views,media_comments,media_votes,media_rating,media_tn_attached,media_tn_image,include_ss,media_user_id,media_user_ip,media_approval,media_type,media_upload_time,media_category,media_watermarked,v100,maint,media_resolution_x,media_resolution_y,remote_media,remote_url)"
         . " VALUES ('" . DB_escapeString($new_media_id) . "','" . DB_escapeString($media_filename) . "','" . DB_escapeString($original_filename) . "','" . DB_escapeString($mimeExt) . "','1','" . DB_escapeString($mimeType) . "','$media_caption','$media_desc','$media_keywords','" . DB_escapeString($media_time) . "','0','0','0','0.00','" . DB_escapeString($attachedThumbnail) . "','','1','" . intval($media_user_id) . "','','0','" . DB_escapeString($mediaType) . "','" . DB_escapeString($media_upload_time) . "','" . DB_escapeString($category) . "','0','0','0'," . intval($resolution_x) . ',' . intval($resolution_y) . ",1,'$remoteURL')";
    DB_query($sql);

    $sql = "SELECT MAX(media_order) + 10 AS media_seq FROM {$_TABLES['mg_media_albums']} WHERE album_id = " . intval($album_id);
    $result = DB_query($sql);
    $row = DB_fetchArray($result);
    $media_seq = $row['media_seq'];
    if ($media_seq < 10) {
        $media_seq = 10;
    }

    $sql = "INSERT INTO " . $tableMediaAlbum . " (media_id, album_id, media_order) VALUES ('" . DB_escapeString($new_media_id) . "', " . intval($album_id) . ", " . intval($media_seq) . ')';
    DB_query($sql);

    if ($mediaType == 1 && $resolution_x > 0 && $resolution_y > 0) {
        DB_save($_TABLES['mg_playback_options'], 'media_id,option_name,option_value', "'$new_media_id','width','" . intval($resolution_x) . "'");
        DB_save($_TABLES['mg_playback_options'], 'media_id,option_name,option_value', "'$new_media_id','height','" . intval($resolution_y) . "'");
    }

    if ($queue == 0) {
        $media_count = $albumInfo['media_count'] + 1;
        DB_change($_TABLES['mg_albums'], 'media_count', $media_count, 'album_id', $albumInfo['album_id']);
        MG_updateAlbumLastUpdate($albumInfo['album_id']);

        if ($albumInfo['album_cover'] == -1 && ($mediaType == 0 || $attachedThumbnail == 1)) {
            $covername = ($attachedThumbnail == 1) ? 'tn_' . $media_filename : $media_filename;
            DB_change($_TABLES['mg_albums'], 'album_cover_filename', $covername, 'album_id', $albumInfo['album_id']);
        }
    }

    if ($queue) {
        $errMsg .= $LANG_MG01['successful_upload_queue'];
    } else {
        $errMsg .= $LANG_MG01['successful_upload'];
    }

    if ($queue == 0) {
        require_once $_CONF['path'] . 'plugins/mediagallery/include/rssfeed.php';
        MG_buildFullRSS();
        MG_buildAlbumRSS($album_id);
    }

    COM_errorLog('MG Upload: Successfully uploaded a media object');
    return array(true, $errMsg);
}

/**
 * Fetch a remote thumbnail from a public HTTP(S) URL.
 *
 * @param string $remotefile
 * @param string $localfile
 * @return bool
 */
function MG_getRemoteThumbnail($remotefile, $localfile)
{
    global $_MG_CONF;

    if (!isset($_MG_CONF['enable_remote_images']) || !$_MG_CONF['enable_remote_images']) {
        return false;
    }

    if (!MG_validateRemoteFetchUrl180($remotefile)) {
        COM_errorLog('MediaGallery: blocked unsafe remote thumbnail fetch.', 1);
        return false;
    }

    if ($_MG_CONF['verbose']) {
        COM_errorLog('Entering MG_getRemoteThumbnail');
    }

    if (!function_exists('curl_init')) {
        $context = stream_context_create(array(
            'http' => array(
                'follow_location' => 0,
                'timeout' => 10,
            ),
            'https' => array(
                'follow_location' => 0,
                'timeout' => 10,
            ),
        ));

        $handle = @fopen($remotefile, 'rb', false, $context);
        if ($handle === false) {
            return false;
        }

        $localhandle = @fopen($localfile, 'wb');
        if ($localhandle === false) {
            fclose($handle);
            return false;
        }

        $written = 0;
        while (!feof($handle)) {
            $data = fread($handle, 8192);
            if ($data === false || $data === '') {
                break;
            }
            $written += fwrite($localhandle, $data);
            if ($written > 10485760) {
                fclose($handle);
                fclose($localhandle);
                @unlink($localfile);
                COM_errorLog('MediaGallery: remote thumbnail exceeded 10 MB limit.', 1);
                return false;
            }
        }

        fclose($handle);
        fclose($localhandle);
    } else {
        $fp = @fopen($localfile, 'wb');
        if ($fp === false) {
            return false;
        }

        $ch = curl_init($remotefile);
        curl_setopt($ch, CURLOPT_FILE, $fp);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_TIMEOUT, 15);
        curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTPS);
        if (defined('CURLOPT_REDIR_PROTOCOLS')) {
            curl_setopt($ch, CURLOPT_REDIR_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTPS);
        }

        $ok = curl_exec($ch);
        $cginfo = curl_getinfo($ch);
        $curlError = curl_errno($ch);
        $curlErrorText = curl_error($ch);
        curl_close($ch);
        fclose($fp);

        if (!$ok || $curlError || !isset($cginfo['http_code']) || intval($cginfo['http_code']) !== 200) {
            @unlink($localfile);
            COM_errorLog('MG_getRemoteThumbnail: HTTP code = '
                . (isset($cginfo['http_code']) ? $cginfo['http_code'] : 0)
                . "\n\tcurl_errno = " . $curlError
                . "\n\tcurl_error text = " . $curlErrorText);
            return false;
        }

        if (@filesize($localfile) > 10485760) {
            @unlink($localfile);
            COM_errorLog('MediaGallery: remote thumbnail exceeded 10 MB limit.', 1);
            return false;
        }
    }

    if (!is_file($localfile) || @filesize($localfile) === 0) {
        @unlink($localfile);
        return false;
    }

    if ($_MG_CONF['verbose']) {
        COM_errorLog('Exiting MG_getRemoteThumbnail');
    }

    return true;
}
?>