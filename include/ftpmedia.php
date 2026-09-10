<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | ftpmedia.php                                                             |
// |                                                                          |
// | FTP Upload routines                                                      |
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

require_once $_CONF['path'] . 'plugins/mediagallery/include/lib-batch.php';
require_once $_CONF['path'] . 'plugins/mediagallery/include/upload_security_180.php';

/**
* FTP Import
*
* @param    int     album_id    album_id upload media
* @return   string              HTML
*
*/
function MG_ftpUpload($album_id)
{
    global $_USER, $_CONF, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG03;

    $retval = '';
    $album = new mgAlbum($album_id);

    if ($album->access == 3 || ($album->member_uploads == 1 && $_USER['uid'] >= 2)) {
        $T = COM_newTemplate(MG_getTemplatePath($album_id));
        $T->set_file('mupload', 'ftpupload.thtml');
        $T->set_var(array(
            'album_id'          => $album_id,
            'start_block'       => COM_startBlock($LANG_MG03['upload_media']),
            'end_block'         => COM_endBlock(),
            'navbar'            => MG_navbar($LANG_MG01['ftp_media'], $album_id),
            's_form_action'     => $_MG_CONF['site_url'] . '/admin.php',
            'lang_upload_help'  => $LANG_MG03['upload_help'],
            'lang_media_ftp'    => $LANG_MG01['upload_media'],
            'lang_directory'    => $LANG_MG01['directory'],
            'lang_recurse'      => $LANG_MG01['recurse'],
            'lang_delete_files' => $LANG_MG01['delete_files'],
            'lang_caption'      => $LANG_MG01['caption'],
            'lang_file'         => $LANG_MG01['file'],
            'lang_description'  => $LANG_MG01['description'],
            'lang_save'         => $LANG_MG01['save'],
            'lang_cancel'       => $LANG_MG01['cancel'],
            'lang_reset'        => $LANG_MG01['reset'],
            'lang_yes'          => $LANG_MG01['yes'],
            'lang_no'           => $LANG_MG01['no'],
            'lang_ftp_help'     => $LANG_MG03['ftp_help'],
            'ftp_path'          => $_MG_CONF['ftp_path'],
            'action'            => 'ftp',
            'gltoken_name'      => CSRF_TOKEN,
            'gltoken'           => SEC_createToken(),
        ));
        $retval .= $T->finish($T->parse('output', 'mupload'));
        return $retval;
    }

    COM_errorLog('MediaGallery: user attempted to upload to a restricted album.');
    return COM_showMessageText($LANG_MG00['access_denied_msg']);
}

function MG_listDir($dir, $album_id, $purgefiles, $recurse)
{
    global $_CONF, $_TABLES, $_MG_CONF, $LANG_MG01, $LANG_MG02, $destDirCount, $pCount;

    if (empty($_MG_CONF['ftp_path'])) {
        return COM_showMessageText($LANG_MG02['invalid_directory']);
    }

    $directory = rtrim($_MG_CONF['ftp_path'], '/\\');
    if ($dir !== '') {
        $directory .= '/' . ltrim($dir, '/\\');
    }

    if (!MG_validateLocalImportSource180($directory, $_MG_CONF['ftp_path'], true)) {
        COM_errorLog('MediaGallery 1.8: rejected FTP directory outside configured ftp_path: ' . $directory);
        return COM_showMessageText($LANG_MG02['invalid_directory']);
    }

    $directory = realpath($directory);
    if ($directory === false || !is_dir($directory)) {
        return COM_showMessageText($LANG_MG02['invalid_directory']);
    }

    if (!$dh = @opendir($directory)) {
        return COM_showMessageText($LANG_MG02['directory_error']);
    }

    $directory = rtrim($directory, '/\\') . '/';
    $rowcounter = 0;
    $retval = '';

    $T = COM_newTemplate(MG_getTemplatePath($album_id));
    $T->set_file('admin', 'filelist.thtml');
    $T->set_var(array(
        'lang_put_files'  => $LANG_MG01['put_files'],
        'lang_into_album' => $LANG_MG01['into_album'],
    ));

    $destDirCount++;
    $dest = sprintf('d%04d', $destDirCount);

    require_once $_CONF['path'] . 'plugins/mediagallery/include/classAlbum.php';
    $album_selectbox = '<select name="' . $dest . '">' . LB;
    $root_album = new mgAlbum(0);
    $root_album->buildAlbumBox($album_selectbox, $album_id, 3, -1, 'upload');
    $album_selectbox .= '</select>' . LB;

    $T->set_block('admin', 'dirRow', 'dRow');

    $pdir = ($dir == '') ? './' : $dir;
    $T->set_var(array(
        'directory'   => $pdir,
        'destination' => $album_selectbox,
        'dirdest'     => $dest,
    ));

    $T->set_block('admin', 'fileRow', 'fRow');

    $dirParts = explode('/', $dir);
    $numDirs = count($dirParts);
    $dirPath = '';
    if ($numDirs > 1) {
        for ($x = 0; $x < $numDirs - 1; $x++) {
            $dirPath .= $dirParts[$x];
            if ($x < $numDirs - 2) {
                $dirPath .= '/';
            }
        }
        $dirlink = '<a href="' . $_MG_CONF['site_url'] . '/admin.php?mode=list&amp;album_id=' . $album_id
                 . '&amp;dir=' . rawurlencode($dirPath) . '">Parent directory</a>';

        $T->set_var(array(
            'row_class'     => ($rowcounter % 2) ? '2' : '1',
            'checkbox'      => '',
            'palbum'        => '',
            'pfile'         => '',
            'dirid'         => '',
            'filename'      => $dirlink,
            'fullname'      => '',
            'filesize'      => '',
            'parent_select' => '',
            'color'         => '',
            'type'          => '',
        ));
        $T->parse('fRow', 'fileRow', true);
        $rowcounter++;
    }

    while (($file = readdir($dh)) !== false) {
        if ($file === '..' || $file === '.') {
            continue;
        }

        $filetmp = $directory . $file;
        if (!MG_validateLocalImportSource180($filetmp, $_MG_CONF['ftp_path'], true)) {
            COM_errorLog('MediaGallery 1.8: skipped unsafe FTP source: ' . $filetmp);
            continue;
        }

        $filename = basename($file);
        $file_extension = strtolower(substr(strrchr($filename, '.'), 1));
        $isadirectory = is_dir($filetmp) ? 1 : 0;

        if ($isadirectory) {
            $type = 'Directory';
            $fullDir = rawurlencode(trim($dir . '/' . $filename, '/'));
            $dirlink = '<a href="' . $_MG_CONF['site_url'] . '/admin.php?album_id=' . $album_id
                     . '&amp;mode=list&amp;dir=' . $fullDir . '">' . htmlspecialchars($filename, ENT_QUOTES, COM_getCharset()) . '</a>';
        } else {
            switch ($file_extension) {
                case 'jpg':
                case 'jpeg':
                case 'bmp':
                case 'tif':
                case 'tiff':
                case 'png':
                case 'gif':
                    $type = 'Image';
                    break;
                case 'avi':
                case 'wmv':
                case 'asf':
                case 'mov':
                case 'mp4':
                case 'mpg':
                case 'mpeg':
                    $type = 'Video';
                    break;
                case 'mp3':
                case 'ogg':
                    $type = 'Audio';
                    break;
                default:
                    $type = 'Unknown';
                    break;
            }
            $dirlink = '';
        }

        $max_filesize = DB_getItem($_TABLES['mg_albums'], 'max_filesize', 'album_id=' . intval($album_id));
        $toobig = 0;
        $fileSize = @filesize($filetmp);
        if (!$isadirectory && $max_filesize != 0 && $fileSize !== false && $fileSize > $max_filesize) {
            $toobig = 1;
        }

        $pCount++;
        $pvalue = sprintf('i%04d', $pCount);
        $safeFilename = htmlspecialchars($filename, ENT_QUOTES, COM_getCharset());
        $safeFullname = htmlspecialchars($filetmp, ENT_QUOTES, COM_getCharset());

        $T->set_var(array(
            'row_class'     => ($rowcounter % 2) ? '2' : '1',
            'checkbox'      => '<input type="checkbox" name="pic[]" value="' . $pvalue . '"' . XHTML . '>',
            'palbum'        => '<input type="hidden" name="album_lb_id_' . $pvalue . '" value="' . $dest . '"' . XHTML . '>',
            'pfile'         => '<input type="hidden" name="picfile_' . $pvalue . '" value="' . $safeFullname . '"' . XHTML . '>',
            'dirid'         => '<input type="hidden" name="dest" value="' . $dest . '"' . XHTML . '>',
            'filename'      => ($isadirectory ? $dirlink : $safeFilename),
            'fullname'      => $safeFullname,
            'filesize'      => ($isadirectory || $fileSize === false) ? '' : COM_numberFormat($fileSize / 1024) . ' kB',
            'parent_select' => '<select name="parentaid">' . LB . $album_selectbox,
            'color'         => ($toobig ? '<span class="mg-file-too-large">' : '<span>'),
            'type'          => $type,
        ));
        $T->parse('fRow', 'fileRow', true);
        $rowcounter++;
    }

    $T->parse('dRow', 'dirRow', true);
    closedir($dh);

    $retval .= $T->finish($T->parse('output', 'admin'));
    return $retval;
}

function MG_ftpProcess($album_id)
{
    global $_TABLES, $_MG_CONF, $LANG_MG00, $LANG_MG01;

    if (!SEC_checkToken()) {
        COM_errorLog('MediaGallery 1.8: rejected FTP import with invalid CSRF token.');
        $display = COM_showMessageText($LANG_MG00['access_denied_msg']);
        $display = MG_createHTMLDocument($display);
        COM_output($display);
        exit;
    }

    $session_description = $LANG_MG01['ftp_media'];
    $origin = ($album_id == 0) ? '/index.php' : '/album.php?aid=' . $album_id;
    $session_id = MG_beginSession('ftpimport', $_MG_CONF['site_url'] . $origin, $session_description);
    $purgefiles = isset($_POST['purgefiles']) ? COM_applyFilter($_POST['purgefiles'], true) : 0;
    $pics = isset($_POST['pic']) && is_array($_POST['pic']) ? $_POST['pic'] : array();

    if (count($pics) < 1) {
        COM_redirect($_MG_CONF['site_url'] . ($album_id == 0 ? '/index.php' : '/album.php?aid=' . $album_id));
    }

    $registered = 0;
    foreach ($pics as $pic_id) {
        $pic_id = COM_applyFilter($pic_id);
        $albumKey = 'album_lb_id_' . $pic_id;
        $fileKey = 'picfile_' . $pic_id;
        if (!isset($_POST[$albumKey], $_POST[$fileKey])) {
            continue;
        }

        $album_lb_id = COM_applyFilter($_POST[$albumKey]);
        if ($album_lb_id === '' || !isset($_POST[$album_lb_id])) {
            continue;
        }

        $aid = COM_applyFilter($_POST[$album_lb_id], true);
        $filename = (string) $_POST[$fileKey];

        if (!MG_validateLocalImportSource180($filename, $_MG_CONF['ftp_path'], true)) {
            COM_errorLog('MediaGallery 1.8: rejected forged or unsafe FTP import source: ' . $filename);
            continue;
        }

        $filename = realpath($filename);
        if ($filename === false) {
            continue;
        }

        $file = basename($filename);
        $mid = is_dir($filename) ? 1 : 0;
        MG_registerSession(array(
            'session_id' => $session_id,
            'mid'        => $mid,
            'aid'        => $aid,
            'data'       => $filename,
            'data2'      => $purgefiles,
            'data3'      => $file,
        ));
        $registered++;
    }

    if ($registered === 0) {
        MG_endSession($session_id);
        $display = COM_showMessageText('MediaGallery: no valid FTP import source was selected.');
        $display = MG_createHTMLDocument($display);
        COM_output($display);
        exit;
    }

    $display = MG_continueSession($session_id, 0, $_MG_CONF['def_refresh_rate']);
    $display = MG_createHTMLDocument($display);
    COM_output($display);
    exit;
}

/**
* Displays pick list of files to process...
*
* @param    int     album_id    album_id save uploaded media
* @return   string              HTML
*
*/
function MG_FTPpickFiles($album_id, $dir, $purgefiles, $recurse)
{
    global $_CONF, $_MG_CONF, $LANG_MG00, $LANG_MG01, $LANG_MG03, $destDirCount, $pCount;

    if (!SEC_checkToken()) {
        COM_errorLog('MediaGallery 1.8: rejected FTP directory selection with invalid CSRF token.');
        return COM_showMessageText($LANG_MG00['access_denied_msg']);
    }

    $destDirCount = 0;
    $pCount = 0;
    $retval = '';

    $T = COM_newTemplate(MG_getTemplatePath($album_id));
    $T->set_file('admin', 'ftpimport.thtml');
    $T->set_var(array(
        'start_block'       => COM_startBlock($LANG_MG03['upload_media']),
        'end_block'         => COM_endBlock(),
        'navbar'            => MG_navbar($LANG_MG01['ftp_media'], $album_id),
        'lang_title'        => $LANG_MG01['title'],
        'lang_description'  => $LANG_MG01['description'],
        'lang_parent_album' => $LANG_MG01['parent_album'],
        'lang_filelist'     => $LANG_MG01['file_list'],
        'lang_quick_create' => $LANG_MG01['quick_create'],
        'lang_checkall'     => $LANG_MG01['check_all'],
        'lang_uncheckall'   => $LANG_MG01['uncheck_all'],
        'dir'               => $dir,
        'purgefiles'        => $purgefiles,
        'recurse'           => $recurse,
        'album_id'          => $album_id,
        'gltoken_name'      => CSRF_TOKEN,
        'gltoken'           => SEC_createToken(),
    ));

    $filelist = MG_listDir($dir, $album_id, $purgefiles, $recurse);

    $album_jumpbox = '<select name="parentaid">';
    if (SEC_hasRights('mediagallery.admin')) {
        $album_jumpbox .= '<option value="0">' . $LANG_MG01['root_album'] . '</option>';
    } else {
        $album_jumpbox .= '<option disabled value="0">' . $LANG_MG01['root_level'] . '</option>';
    }
    $root_album = new mgAlbum(0);
    $root_album->buildJumpBox($album_jumpbox, 0, 3);
    $album_jumpbox .= '</select>';

    $T->set_var(array(
        's_form_action' => $_MG_CONF['site_url'] . '/admin.php',
        'action'        => 'ftpprocess',
        'lang_save'     => $LANG_MG01['save'],
        'lang_cancel'   => $LANG_MG01['cancel'],
        'parent_select' => $album_jumpbox,
        'filelist'      => $filelist,
    ));

    $retval .= $T->finish($T->parse('output', 'admin'));
    return $retval;
}
?>