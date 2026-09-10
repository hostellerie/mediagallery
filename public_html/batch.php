<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | batch.php                                                                |
// |                                                                          |
// | Batch system interface                                                   |
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

require_once $_CONF['path'] . 'plugins/mediagallery/include/common.php';
require_once $_CONF['path'] . 'plugins/mediagallery/include/lib-batch.php';
require_once $_CONF['path'] . 'plugins/mediagallery/include/upload_security_180.php';

if (COM_isAnonUser() && $_MG_CONF['loginrequired'] == 1) {
    $display = SEC_loginRequiredForm();
    $display = MG_createHTMLDocument($display);
    COM_output($display);
    exit;
}

/**
* Main
*/

$mode       = isset($_REQUEST['mode']) ? COM_applyFilter($_REQUEST['mode']) : '';
$session_id = isset($_GET['sid'])      ? COM_applyFilter($_GET['sid'])      : '';

if (empty($session_id)) {
    COM_redirect($_MG_CONF['site_url'] . '/index.php');
}

$escapedSessionId = DB_escapeString($session_id);
$sessionResult = DB_query(
    "SELECT session_uid, session_origin FROM {$_TABLES['mg_sessions']} "
    . "WHERE session_id='" . $escapedSessionId . "'"
);

if (DB_numRows($sessionResult) !== 1) {
    COM_errorLog('MediaGallery: unable to retrieve batch session data.');
    COM_redirect($_MG_CONF['site_url'] . '/index.php');
}

$sessionInfo = DB_fetchArray($sessionResult);
if ((int) $sessionInfo['session_uid'] !== (int) $_USER['uid']
    && !SEC_hasRights('mediagallery.admin')) {
    $display = COM_showMessageText($LANG_MG00['access_denied_msg']);
    $display = MG_createHTMLDocument($display);
    COM_output($display);
    exit;
}

if (isset($_POST['cancel_button'])) {
    $session_origin = $sessionInfo['session_origin'];
    if (empty($session_origin)) {
        COM_redirect($_MG_CONF['site_url'] . '/index.php');
    }
    MG_endSession($session_id);
    COM_redirect($session_origin);
}

if ($mode != 'continue') {
    COM_redirect($_MG_CONF['site_url'] . '/index.php');
}

$refresh_rate = $_MG_CONF['def_refresh_rate'];
if (isset($_POST['refresh_rate'])) {
    $refresh_rate = COM_applyFilter($_POST['refresh_rate'], true);
} else if (isset($_GET['refresh'])) {
    $refresh_rate = COM_applyFilter($_GET['refresh'], true);
}

$item_limit = $_MG_CONF['def_item_limit'];
if (isset($_POST['item_limit'])) {
    $item_limit = COM_applyFilter($_POST['item_limit'], true);
} else if (isset($_GET['limit'])) {
    $item_limit = COM_applyFilter($_GET['limit'], true);
}

// MediaGallery 1.8 validates every pending FTP source before a batch cycle.
// This protects recursive imports too: newly discovered entries are checked
// on the next batch request before they can be processed.
$ftpValidationReason = '';
if (!MG_validateFtpBatchSession180($session_id, $ftpValidationReason)) {
    if ($ftpValidationReason === 'access_denied') {
        $display = COM_showMessageText($LANG_MG00['access_denied_msg']);
    } else {
        $display = COM_showMessageText(
            'MediaGallery: FTP import stopped because an invalid or unsafe source path was detected.'
        );
    }
    $display = MG_createHTMLDocument($display);
    COM_output($display);
    exit;
}

$display = MG_continueSession($session_id, $item_limit, $refresh_rate);
$display = MG_createHTMLDocument($display);
COM_output($display);
exit;

?>