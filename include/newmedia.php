<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | newmedia.php                                                             |
// |                                                                          |
// | Media Upload routines                                                    |
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
// +--------------------------------------------------------------------------+

use Geeklog\Input;

if (stripos($_SERVER['PHP_SELF'], basename(__FILE__)) !== false) {
    die('This file can not be used on its own!');
}

require_once $_CONF['path'] . 'plugins/mediagallery/include/classAlbum.php';
require_once $_CONF['path'] . 'plugins/mediagallery/include/lib-upload.php';
require_once $_CONF['path'] . 'plugins/mediagallery/include/sort.php';

/**
 * Upload form.
 *
 * The historical SWFUpload rendering code lived after an unconditional return
 * and was therefore unreachable. MediaGallery 1.8 keeps the active browser
 * upload path only.
 *
 * @param int $album_id
 * @return string
 */
function MG_uploadForm($album_id)
{
    return MG_userUpload($album_id);
}

/**
 * Save upload(s) from the legacy upload endpoint.
 *
 * @param int $album_id
 * @return string
 */
function MG_saveUpload($album_id)
{
    global $_TABLES, $_MG_CONF, $LANG_MG01, $LANG_MG02, $new_media_id;

    $file = isset($_FILES) && is_array($_FILES) ? $_FILES : array();
    $album = new mgAlbum($album_id);

    if ($_MG_CONF['verbose']) {
        COM_errorLog('*** Inside MG_saveUpload()***');
        COM_errorLog('uploading to album_id=' . $album_id);
        COM_errorLog('album owner_id=' . $album->owner_id);
    }

    if (!isset($album->id) || $album_id == 0) {
        COM_errorLog('MediaGallery: Upload was unable to determine album id');
        return $LANG_MG01['upload_err_album_id'];
    }

    $successfull_upload = 0;

    foreach ($file as $tagname => $object) {
        $filename = $object['name'];
        $filetype = $object['type'];
        $filesize = $object['size'];
        $filetmp = $object['tmp_name'];
        $error = $object['error'];
        $caption = '';
        $description = '';
        $thumbnail = '';

        if ($_MG_CONF['verbose']) {
            COM_errorLog('filename=' . $filename, 1);
            COM_errorLog('filesize=' . $filesize, 1);
            COM_errorLog('filetype=' . $filetype, 1);
            COM_errorLog('filetmp=' . $filetmp, 1);
            COM_errorLog('error=' . $error, 1);
        }

        if (!MG_validateUploadFilename180($filename)) {
            COM_errorLog('MediaGallery: rejected unsafe upload filename: ' . basename($filename), 1);
            return $LANG_MG02['format_not_allowed'];
        }

        if (($album->max_filesize != 0) && ($filesize > $album->max_filesize)) {
            COM_errorLog('MediaGallery: File ' . $filename . ' exceeds maximum allowed filesize for this album');
            COM_errorLog('MediaGallery: Max filesize for this album=' . $album->max_filesize);
            return sprintf($LANG_MG02['upload_exceeds_max_filesize'], $filename);
        }

        $opt = array(
            'caption' => $caption,
            'description' => $description,
            'filetype' => $filetype,
            'atttn' => 0,
            'thumbnail' => $thumbnail,
        );
        list($rc, $msg) = MG_getFile($filetmp, $filename, $album_id, $opt);

        if ($rc == true) {
            $successfull_upload++;
        } else {
            COM_errorLog('MG_saveUpload error: ' . $msg, 1);
            return $msg;
        }
    }

    if (!empty($_CONF['debug_image_upload'])) {
        COM_errorLog(
            'MG DEBUG saveUserUpload after files: success=' . intval($successfull_upload)
            . ' status_length=' . strlen((string) $statusMsg)
        );
    }

    if ($successfull_upload) {
        if (!empty($_CONF['debug_image_upload'])) {
            COM_errorLog('MG DEBUG saveUserUpload before moderator notification');
        }
        MG_notifyModerators180($album_id);
        if (!empty($_CONF['debug_image_upload'])) {
            COM_errorLog('MG DEBUG saveUserUpload after moderator notification');
        }
    }

    $dbCount = DB_count($_TABLES['mg_media_albums'], 'album_id', intval($album_id));
    $aCount = DB_getItem($_TABLES['mg_albums'], 'media_count', 'album_id=' . intval($album_id));
    if ($dbCount != $aCount) {
        DB_change($_TABLES['mg_albums'], 'media_count', $dbCount, 'album_id', intval($album_id));
        COM_errorLog("MediaGallery: Upload processing - Counts don't match - dbCount = $dbCount aCount = $aCount");
    }

    MG_SortMedia($album_id);

    return 'FILEID:' . $new_media_id;
}

/**
 * Browser upload form.
 *
 * @param int $album_id
 * @return string
 */
function MG_userUpload($album_id)
{
    global $_USER, $_TABLES, $_MG_CONF, $LANG_MG01, $LANG_MG03;

    $root_album = new mgAlbum(0);
    $album_selectbox = MG_buildAlbumBox($root_album, $album_id, 3, -1, 'upload');

    $result = DB_query("SELECT * FROM {$_TABLES['mg_category']} ORDER BY cat_id ASC");
    $catRow = array();
    while ($row = DB_fetchArray($result)) {
        $catRow[] = $row;
    }

    $cRows = count($catRow);
    $cat_selects = array('', '', '', '');
    if ($cRows > 0) {
        for ($slot = 0; $slot < 4; $slot++) {
            $select = '<select name="cat_id[' . $slot . ']">';
            $select .= '<option value="0">' . $LANG_MG01['no_category'] . '</option>';
            foreach ($catRow as $row) {
                $select .= '<option value="' . intval($row['cat_id']) . '">' . $row['cat_name'] . '</option>';
            }
            $select .= '</select>';
            $cat_selects[$slot] = $select;
        }
    }

    $user_quota = DB_getItem($_TABLES['mg_userprefs'], 'quota', 'uid=' . intval($_USER['uid']));
    if ($user_quota > 0) {
        $disk_used = MG_quotaUsage($_USER['uid']);
        $user_quota = $user_quota / 1024;
        $disk_used = $disk_used / 1024;
        $quota = sprintf($LANG_MG01['user_quota'], $user_quota, $disk_used, $user_quota - $disk_used);
    } else {
        $quota = '';
    }

    $post_max_size = MG_return_bytes(ini_get('post_max_size')) / 1048576;
    $upload_max_size_b = MG_return_bytes(ini_get('upload_max_filesize'));
    $max_upload_size = $upload_max_size_b / 1048576;
    $msg_upload_size = sprintf($LANG_MG03['upload_size'], $post_max_size, $max_upload_size);

    $T = COM_newTemplate(MG_getTemplatePath($album_id));
    $T->set_file('mupload', 'userupload.thtml');
    $T->set_var(array(
        'start_block' => COM_startBlock($LANG_MG03['upload_media']),
        'end_block' => COM_endBlock(),
        'navbar' => MG_navbar($LANG_MG01['browser_upload'], $album_id),
        'admin_url' => $_MG_CONF['admin_url'],
        's_form_action' => $_MG_CONF['site_url'] . '/admin.php',
        'lang_upload_help' => $LANG_MG03['upload_help'],
        'lang_upload_size' => $msg_upload_size,
        'lang_zip_help' => ($_MG_CONF['zip_enabled'] == 1 ? $LANG_MG03['zip_file_help'] . '<br' . XHTML . '><br' . XHTML . '>' : ''),
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
        'lang_do_not_convert_orig' => $LANG_MG01['do_not_convert_orig'],
        'lang_file_number' => $LANG_MG01['file_number'],
        'cat_select_0' => $cat_selects[0],
        'cat_select_1' => $cat_selects[1],
        'cat_select_2' => $cat_selects[2],
        'cat_select_3' => $cat_selects[3],
        'album_id' => $album_id,
        'action' => 'upload',
        'max_file_size' => '<input type="hidden" name="MAX_FILE_SIZE" value="' . $upload_max_size_b . '"' . XHTML . '>',
        'lang_quota' => $quota,
        'album_select' => $album_selectbox,
        'max_upload_size' => $max_upload_size,
        'post_max_size' => $post_max_size,
        'gltoken_name' => CSRF_TOKEN,
        'gltoken' => SEC_createToken(),
    ));

    return $T->finish($T->parse('output', 'mupload'));
}

/**
 * Save browser upload(s).
 *
 * @param int $album_id
 * @return string
 */
function MG_saveUserUpload($album_id)
{
    global $_USER, $_CONF, $_TABLES, $_MG_CONF, $LANG_MG02, $LANG_MG03;

    if (!SEC_checkToken()) {
        COM_errorLog('MediaGallery: browser upload rejected because of an invalid CSRF token.', 1);
        return COM_showMessageText($LANG_MG02['generic_error']);
    }

    if (!empty($_CONF['debug_image_upload'])) {
        COM_errorLog('MG DEBUG saveUserUpload: CSRF accepted album_id=' . intval($album_id));
    }

    $retval = COM_startBlock($LANG_MG03['upload_results'], '', COM_getBlockTemplate('_admin_block', 'header'));

    $T = COM_newTemplate(MG_getTemplatePath($album_id));
    $T->set_file('mupload', 'useruploadstatus.thtml');

    $statusMsg = '';
    $file = isset($_FILES['newmedia']) ? $_FILES['newmedia'] : array();
    $thumbs = isset($_FILES['thumbnail']) ? $_FILES['thumbnail'] : array();
    $captions = (isset($_POST['caption']) && is_array($_POST['caption'])) ? $_POST['caption'] : array();
    $descriptions = (isset($_POST['description']) && is_array($_POST['description'])) ? $_POST['description'] : array();
    $keywordsValues = (isset($_POST['keywords']) && is_array($_POST['keywords'])) ? $_POST['keywords'] : array();
    $categories = (isset($_POST['cat_id']) && is_array($_POST['cat_id'])) ? $_POST['cat_id'] : array();
    $attachValues = (isset($_POST['attachtn']) && is_array($_POST['attachtn'])) ? $_POST['attachtn'] : array();
    $dncValues = (isset($_POST['dnc']) && is_array($_POST['dnc'])) ? $_POST['dnc'] : array();

    if (!isset($file['name']) || !is_array($file['name'])) {
        return COM_showMessageText($LANG_MG02['generic_error']);
    }

    $album = new mgAlbum($album_id);
    $successfull_upload = 0;
    $br = '<br' . XHTML . '>';

    foreach ($file['name'] as $key => $name) {
        $filename = isset($file['name'][$key]) ? $file['name'][$key] : '';
        $filetype = isset($file['type'][$key]) ? $file['type'][$key] : '';
        $filesize = isset($file['size'][$key]) ? $file['size'][$key] : 0;
        $filetmp = isset($file['tmp_name'][$key]) ? $file['tmp_name'][$key] : '';
        $error = isset($file['error'][$key]) ? $file['error'][$key] : UPLOAD_ERR_NO_FILE;
        $caption = isset($captions[$key]) ? COM_stripslashes($captions[$key]) : '';
        $description = isset($descriptions[$key]) ? COM_stripslashes($descriptions[$key]) : '';
        $keywords = isset($keywordsValues[$key]) ? COM_stripslashes($keywordsValues[$key]) : '';
        $category = isset($categories[$key]) ? intval($categories[$key]) : 0;
        $thumbnail = isset($thumbs['tmp_name'][$key]) ? $thumbs['tmp_name'][$key] : '';
        $dnc = !empty($dncValues[$key]) ? 1 : 0;

        if ($filename == '') {
            continue;
        }

        if (!MG_validateUploadFilename180($filename)) {
            COM_errorLog('MediaGallery: rejected unsafe upload filename: ' . basename($filename), 1);
            $statusMsg .= $filename . ' ' . $LANG_MG02['format_not_allowed'] . $br;
            continue;
        }

        if ($album->max_filesize != 0 && $filesize > $album->max_filesize) {
            COM_errorLog('MG Upload: File ' . $filename . ' exceeds maximum allowed filesize for this album');
            $statusMsg .= sprintf($LANG_MG02['upload_exceeds_max_filesize'], $filename) . $br;
            continue;
        }

        $attach_tn = !empty($attachValues[$key]) ? 1 : 0;

        if ($error != UPLOAD_ERR_OK) {
            switch ($error) {
                case UPLOAD_ERR_INI_SIZE:
                    $tmpmsg = sprintf($LANG_MG02['upload_too_big'], $filename);
                    break;
                case UPLOAD_ERR_FORM_SIZE:
                    $tmpmsg = sprintf($LANG_MG02['upload_too_big_html'], $filename);
                    break;
                case UPLOAD_ERR_PARTIAL:
                    $tmpmsg = sprintf($LANG_MG02['partial_upload'], $filename);
                    break;
                case UPLOAD_ERR_NO_FILE:
                    continue 2;
                case UPLOAD_ERR_NO_TMP_DIR:
                    $tmpmsg = $LANG_MG02['missing_tmp'];
                    break;
                case UPLOAD_ERR_CANT_WRITE:
                    $tmpmsg = $LANG_MG02['disk_fail'];
                    break;
                default:
                    $tmpmsg = $LANG_MG02['unknown_err'];
                    break;
            }
            $statusMsg .= $tmpmsg . $br;
            COM_errorLog('MediaGallery: upload error - ' . $tmpmsg);
            continue;
        }

        $user_quota = DB_getItem($_TABLES['mg_userprefs'], 'quota', 'uid=' . intval($_USER['uid']));
        if ($user_quota > 0) {
            $disk_used = MG_quotaUsage($_USER['uid']);
            if ($disk_used + $filesize > $user_quota) {
                COM_errorLog('MG Upload: File ' . $filename . ' would exceed the user quota');
                $statusMsg .= sprintf($LANG_MG02['upload_exceeds_quota'], $filename) . $br;
                continue;
            }
        }

        $opt = array(
            'caption' => $caption,
            'description' => $description,
            'filetype' => $filetype,
            'atttn' => $attach_tn,
            'thumbnail' => $thumbnail,
            'keywords' => $keywords,
            'category' => $category,
            'dnc' => $dnc,
        );
        list($rc, $msg) = MG_getFile($filetmp, $filename, $album_id, $opt);

        $statusMsg .= $filename . ' ' . $msg . $br;
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
        COM_errorLog("MediaGallery: Upload processing - Counts don't match - dbCount = $dbCount aCount = $aCount");
    }

    if (!empty($_CONF['debug_image_upload'])) {
        COM_errorLog('MG DEBUG saveUserUpload before MG_SortMedia');
    }
    MG_SortMedia($album_id);
    if (!empty($_CONF['debug_image_upload'])) {
        COM_errorLog('MG DEBUG saveUserUpload after MG_SortMedia');
    }

    $T->set_var('status_message', $statusMsg);
    $tmp = $_MG_CONF['site_url'] . '/album.php?aid=' . $album_id . '&amp;page=1';
    $T->set_var('redirect', sprintf($LANG_MG03['album_redirect'], $tmp));
    $T->parse('output', 'mupload');
    if (!empty($_CONF['debug_image_upload'])) {
        COM_errorLog('MG DEBUG saveUserUpload parsed template length=' . strlen((string) $T->get_var('output')));
    }
    $retval .= $T->finish($T->get_var('output'));
    $retval .= COM_endBlock(COM_getBlockTemplate('_admin_block', 'footer'));

    if (!empty($_CONF['debug_image_upload'])) {
        COM_errorLog('MG DEBUG saveUserUpload return length=' . strlen((string) $retval));
    }

    return $retval;
}

/**
 * Save file upload(s) from the legacy async endpoint.
 *
 * @param int $album_id
 * @return string
 */
function MG_saveFileUpload($album_id)
{
    global $_TABLES, $_MG_CONF, $LANG_MG01, $LANG_MG02, $new_media_id;

    $file = array();
    $album = new mgAlbum($album_id);

    if ($_MG_CONF['verbose']) {
        COM_errorLog('*** Inside MG_saveFileUpload()***');
        COM_errorLog('uploading to album_id=' . $album_id);
        COM_errorLog('album owner_id=' . $album->owner_id);
    }

    if (!isset($album->id) || $album_id == 0) {
        COM_errorLog('MediaGallery: FileUpload was unable to determine album id');
        return $LANG_MG01['swfupload_err_album_id'];
    }

    $successfull_upload = 0;
    $upload = isset($_FILES['files']) ? $_FILES['files'] : null;

    if ($upload && isset($upload['tmp_name']) && is_array($upload['tmp_name'])) {
        foreach ($upload['tmp_name'] as $index => $value) {
            $file[$index] = array(
                'name' => $upload['name'][$index],
                'type' => $upload['type'][$index],
                'size' => $upload['size'][$index],
                'tmp_name' => $upload['tmp_name'][$index],
                'error' => $upload['error'][$index],
            );
        }
    } elseif ($upload) {
        $file[0] = array(
            'name' => $upload['name'],
            'type' => $upload['type'],
            'size' => $upload['size'],
            'tmp_name' => $upload['tmp_name'],
            'error' => $upload['error'],
        );
    } else {
        return json_encode(array());
    }

    $info = array();

    foreach ($file as $object) {
        $filename = $object['name'];
        $filetype = $object['type'];
        $filesize = $object['size'];
        $filetmp = $object['tmp_name'];
        $caption = 'No Name';
        $description = 'No Description';

        if (!MG_validateUploadFilename180($filename)) {
            COM_errorLog('MediaGallery: rejected unsafe upload filename: ' . basename($filename), 1);
            return $LANG_MG02['format_not_allowed'];
        }

        if ($album->max_filesize != 0 && $filesize > $album->max_filesize) {
            COM_errorLog('MediaGallery: File ' . $filename . ' exceeds maximum allowed filesize for this album');
            return sprintf($LANG_MG02['upload_exceeds_max_filesize'], $filename);
        }

        $opt = array(
            'caption' => $caption,
            'description' => $description,
            'filetype' => $filetype,
            'atttn' => 0,
            'thumbnail' => '',
        );
        list($rc, $msg) = MG_getFile($filetmp, $filename, $album_id, $opt);

        if (!$rc) {
            COM_errorLog('MG_saveFileUpload error: ' . $msg, 1);
            return $msg;
        }

        $successfull_upload++;
        $temp = new stdClass();
        $temp->name = $filename;
        $temp->size = $filesize;
        $temp->type = $filetype;
        $temp->mid = $new_media_id;
        $temp->caption = $caption;
        $temp->description = $description;
        $info[] = $temp;
    }

    if ($successfull_upload) {
        MG_notifyModerators180($album_id);
    }

    $dbCount = DB_count($_TABLES['mg_media_albums'], 'album_id', intval($album_id));
    $aCount = DB_getItem($_TABLES['mg_albums'], 'media_count', 'album_id=' . intval($album_id));
    if ($dbCount != $aCount) {
        DB_change($_TABLES['mg_albums'], 'media_count', $dbCount, 'album_id', intval($album_id));
        COM_errorLog("MediaGallery: Upload processing - Counts don't match - dbCount = $dbCount aCount = $aCount");
    }

    MG_SortMedia($album_id);

    return json_encode($info);
}