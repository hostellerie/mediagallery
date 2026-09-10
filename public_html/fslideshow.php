<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | fslideshow.php                                                           |
// |                                                                          |
// | Compatibility route for the historical Flash slideshow                  |
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

$album_id  = isset($_GET['aid'])  ? COM_applyFilter($_GET['aid'], true)  : 0;
$sortOrder = isset($_GET['sort']) ? COM_applyFilter($_GET['sort'], true) : 0;
$full      = isset($_GET['f'])    ? COM_applyFilter($_GET['f'], true)    : 0;

if ($album_id < 1) {
    COM_redirect($_MG_CONF['site_url'] . '/index.php');
}

$album_data = MG_getAlbumData(
    $album_id,
    array('album_id'),
    true
);

if (!isset($album_data['album_id']) || $album_data['access'] == 0) {
    $display = COM_showMessageText($LANG_MG00['access_denied_msg']);
    $display = MG_createHTMLDocument($display);
    COM_output($display);
    exit;
}

// MediaGallery 1.8 no longer executes the historical Flash slideshow.
// Keep old bookmarks/autotag-generated URLs working by forwarding them to
// the maintained slideshow implementation and preserving useful parameters.
$url = $_MG_CONF['site_url'] . '/slideshow.php?aid=' . (int) $album_id
     . '&amp;f=' . ($full ? 1 : 0)
     . '&amp;sort=' . (int) $sortOrder;

COM_redirect(str_replace('&amp;', '&', $url));
exit;
