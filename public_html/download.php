<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | download.php                                                             |
// |                                                                          |
// | Download objects directly                                                |
// +--------------------------------------------------------------------------+
// | Copyright (C) 2015 by the following authors:                             |
// |                                                                          |
// | Yoshinori Tahara       taharaxp AT gmail DOT com                         |
// |                                                                          |
// | Based on the Media Gallery Plugin for glFusion CMS                       |
// | Copyright (C) 2002-2010 by the following authors:                        |
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

require_once '../lib-common.php';

if (!in_array('mediagallery', $_PLUGINS)) {
    COM_redirect($_CONF['site_url'] . '/index.php');
}

if (COM_isAnonUser() && $_MG_CONF['loginrequired'] == 1) {
    $display = SEC_loginRequiredForm();
    $display = MG_createHTMLDocument($display);
    COM_output($display);
    exit;
}

require_once $_CONF['path'] . 'plugins/mediagallery/include/common.php';

// Implements a poor mans hotlink protection, if the request
// did not originate at our site, don't allow it.
$referrer = isset($_SERVER['HTTP_REFERER']) ? $_SERVER['HTTP_REFERER'] : '';
$allowed = 0;
if ($referrer == '') {
    $allowed = 1;
} else {
    if (strpos($referrer, $_CONF['site_url']) !== false) {
        $allowed = 1;
    }
}
if ($allowed == 0) return;

$mid = isset($_GET['mid']) ? COM_applyFilter($_GET['mid']) : '';
if (empty($mid)) return;

$aid = DB_getItem($_TABLES['mg_media_albums'], 'album_id', 'media_id="' . DB_escapeString($mid) . '"');
$album_data = MG_getAlbumData($aid, array('album_id'), true);
if ($album_data['access'] == 0) {
    $display = COM_startBlock($LANG_ACCESS['accessdenied'], '',COM_getBlockTemplate('_msg_block', 'header'))
             . '<br' . XHTML . '>' . $LANG_MG00['access_denied_msg']
             . COM_endBlock(COM_getBlockTemplate('_msg_block', 'footer'));
    $display = MG_createHTMLDocument($display);
    COM_output($display);
    exit;
}

$sql = "SELECT * FROM {$_TABLES['mg_media']} WHERE media_id='" . DB_escapeString($mid) . "'";
$result = DB_query($sql);
while ($A = DB_fetchArray($result)) {
    $filename = $A['media_original_filename'];
    if (empty($filename)) {
        $filename = $A['media_filename'] . '.' . $A['media_mime_ext'];
    }

    $mime_type = $A['mime_type'];
    if ($mime_type == 'application/octet-stream' &&
            strtolower($A['media_mime_ext']) == 'pdf') {
        $mime_type = 'application/pdf';
    }

    if (!SEC_hasRights('mediagallery.admin')) {
        $media_views = $A['media_views'] + 1;
        DB_change($_TABLES['mg_media'], 'media_views', $media_views, 'media_id', DB_escapeString($mid));
    }

    $relative = 'orig/' . $A['media_filename'][0] . '/'
              . $A['media_filename'] . '.' . ltrim($A['media_mime_ext'], '.');
    $resolved = MG_resolveMediaStorageFile180($relative);

    if ($resolved === false) {
        COM_errorLog(
            'MediaGallery download: media file is missing for ' . $mid
            . ' (expected relative path: ' . $relative . ')',
            1
        );

        http_response_code(404);
        $display = COM_startBlock(
            'Media file not found',
            '',
            COM_getBlockTemplate('_msg_block', 'header')
        )
        . '<p>The database record exists, but the physical media file is missing.</p>'
        . '<p><code>' . htmlspecialchars($relative, ENT_QUOTES, COM_getCharset()) . '</code></p>'
        . COM_endBlock(COM_getBlockTemplate('_msg_block', 'footer'));
        $display = MG_createHTMLDocument($display, 'Media file not found');
        COM_output($display);
        exit;
    }

    $path = $resolved['path'];
    $size = @filesize($path);
    if ($size === false) {
        http_response_code(500);
        COM_errorLog('MediaGallery download: unable to read file size for ' . $path, 1);
        exit;
    }

    $downloadName = basename($filename);
    if ($mime_type === '') {
        $mime_type = 'application/octet-stream';
    }

    header("Pragma: public");
    header("Expires: 0");
    header("Cache-Control: must-revalidate, post-check=0,pre-check=0");
    header("Cache-Control: private", false);
    header("Content-Type: " . $mime_type);
    header("Content-Disposition: attachment; filename=\"" . $downloadName . "\"");
    header("Content-Transfer-Encoding: binary");
    header("Content-Length: " . $size);

    $fp = @fopen($path, 'rb');
    if ($fp === false) {
        COM_errorLog('MediaGallery download: unable to open media file ' . $path, 1);
        exit;
    }

    while (!feof($fp)) {
        $buf = fread($fp, 8192);
        if ($buf === false) {
            break;
        }
        echo $buf;
    }
    fclose($fp);
}
return;
?>