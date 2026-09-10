<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | upload.php                                                               |
// |                                                                          |
// | Legacy asynchronous upload endpoint                                      |
// +--------------------------------------------------------------------------+
// | Copyright (C) 2015-2019 by the following authors:                        |
// |                                                                          |
// | Yoshinori Tahara       taharaxp AT gmail DOT com                         |
// | Kenji ITO              msytralkk AT gmai DOT com                         |
// |                                                                          |
// | Based on the Media Gallery Plugin for glFusion CMS                       |
// | Copyright (C) 2002-2009 by the following authors:                        |
// |                                                                          |
// | Mark R. Evans          mark AT glfusion DOT org                          |
// | Mark A. Howard         mark AT usable-web DOT com                        |
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

require_once '../../lib-common.php';

if (!in_array('mediagallery', $_PLUGINS)) {
    COM_errorLog('Upload: MediaGallery is disabled', 1);
    COM_404();
    exit;
}

$postedUid = isset($_POST['uid']) ? COM_applyFilter($_POST['uid'], true) : 0;
$aid = isset($_POST['aid']) ? COM_applyFilter($_POST['aid'], true) : 0;

// The authenticated Geeklog session is authoritative. MediaGallery 1.7.x
// replaced $_USER using a uid supplied by POST, which allowed the request to
// select another Geeklog identity. 1.8.0 never trusts posted identity data.
$sessionUid = isset($_USER['uid']) ? intval($_USER['uid']) : 1;
if ($sessionUid < 2) {
    COM_errorLog('Upload: Anonymous upload rejection.', 1);
    echo 'Anonymous upload rejected';
    exit(0);
}

// Keep accepting the legacy uid field for old clients, but require it to
// identify the already authenticated session user when it is supplied.
if ($postedUid > 0 && intval($postedUid) !== $sessionUid) {
    COM_errorLog(
        'Upload: Rejected posted uid ' . intval($postedUid)
        . ' because authenticated uid is ' . $sessionUid,
        1
    );
    echo 'Invalid upload session';
    exit(0);
}

if ($aid < 1) {
    COM_errorLog('Upload: Invalid album id.', 1);
    echo 'Invalid album';
    exit(0);
}

if ($_MG_CONF['verbose']) {
    COM_errorLog('*** Inside MediaGallery upload endpoint ***', 1);
    COM_errorLog('authenticated uid=' . $sessionUid, 1);
    COM_errorLog('received aid=' . $aid, 1);
}

$_GROUPS = SEC_getUserGroups($sessionUid);
$_RIGHTS = explode(',', SEC_getUserPermissions());

require_once $_CONF['path'] . 'plugins/mediagallery/include/newmedia.php';

$rc = MG_saveUpload($aid);
echo $rc;
exit(0);
