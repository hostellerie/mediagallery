<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | functions.inc                                                            |
// |                                                                          |
// | This file does two things: 1) it implements the necessary glFusion Plugin|
// | API method and 2) implements all the common code needed by the Media     |
// | Gallery PHP files.                                                       |
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

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

global $_TABLES, $_DB_table_prefix; // Needs to be set for when plugin enabled (if plugin already disabled)
$_MG_CONF = array();
$_MG_CONF['pi_version'] = '1.7.3';
$_MG_CONF['installed_version'] = DB_getItem($_TABLES['plugins'], 'pi_version', "pi_name = 'mediagallery'");
$_MG_CONF['var_current_code'] = version_compare($_MG_CONF['installed_version'], $_MG_CONF['pi_version'], '>=');
$_MG_CONF['custom_image_width'] = 0;
$_MG_CONF['custom_image_height'] = 0;

/**
* Add to $_TABLES array the tables mediagallery plugin uses
*/
$_TABLES['mg_albums']           = $_DB_table_prefix . 'mg_albums';
$_TABLES['mg_media']            = $_DB_table_prefix . 'mg_media';
$_TABLES['mg_media_albums']     = $_DB_table_prefix . 'mg_media_albums';
$_TABLES['mg_usage_tracking']   = $_DB_table_prefix . 'mg_usage_tracking';
$_TABLES['mg_mediaqueue']       = $_DB_table_prefix . 'mg_mediaqueue'; // renamed from mg_media_queue to mg_mediaqueue
$_TABLES['mg_media_album_queue']= $_DB_table_prefix . 'mg_media_album_queue';
$_TABLES['mg_playback_options'] = $_DB_table_prefix . 'mg_playback_options';
$_TABLES['mg_userprefs']        = $_DB_table_prefix . 'mg_userprefs';
$_TABLES['mg_exif_tags']        = $_DB_table_prefix . 'mg_exif_tags';
$_TABLES['mg_watermarks']       = $_DB_table_prefix . 'mg_watermarks';
$_TABLES['mg_category']         = $_DB_table_prefix . 'mg_category';
$_TABLES['mg_sessions']         = $_DB_table_prefix . 'mg_sessions';
$_TABLES['mg_session_items']    = $_DB_table_prefix . 'mg_session_items';
$_TABLES['mg_session_log']      = $_DB_table_prefix . 'mg_session_log';
$_TABLES['mg_sort']             = $_DB_table_prefix . 'mg_sort';
$_TABLES['mg_rating']           = $_DB_table_prefix . 'mg_rating';
//$_TABLES['mg_mediasubmission']  = $_DB_table_prefix . 'mg_mediaqueue';
//$_TABLES['mg_mediasubmission']  = $_DB_table_prefix . 'mg_media_queue';

$_TABLES['mg_old_mediaqueue']   = $_DB_table_prefix . 'mg_media_queue';
$_TABLES['mg_config']           = $_DB_table_prefix . 'mg_config';

/**
 * Media Gallery Global Configuration Options
 */

/*
 * Media Gallery Path Configuration. If you want to move the directory where
 * the Media Gallery programs are stored and accessed, change the
 * $_MG_CONF['path_mg'] to the new directory name.
 *
 * You normally do not need to change any of the other paths.
 */
$_MG_CONF['path_html']  = $_CONF['path_html'] . 'mediagallery/';
$_MG_CONF['site_url']   = $_CONF['site_url'] . '/mediagallery';
$_MG_CONF['admin_url']  = $_CONF['site_admin_url'] . '/plugins/mediagallery/';
$_MG_CONF['path_admin'] = $_CONF['path_html'] . 'admin/plugins/mediagallery/';

$_MG_CONF['path_mediaobjects'] = $_CONF['path_html'] . 'mediagallery/mediaobjects/';
$_MG_CONF['mediaobjects_url']  = $_CONF['site_url']  . '/mediagallery/mediaobjects';

$_MG_CONF['template_path']     = $_CONF['path'] . 'plugins/mediagallery/templates';

$_MG_CONF['watermark_types'] = array('image/jpeg','image/jpg','image/png','image/bmp');

$_MG_CONF['link_to_member_album'] = 1;


/*
 * By default, Media Gallery plays MP4 video files as QuickTime
 * videos, using the QuickTime player.
 *
 * If you prefer to use the Flash Video Player for MP4 files,
 * set this value to true.
 *
 */
$_MG_CONF['play_mp4_flv'] = false;
//$_MG_CONF['play_mp4_flv'] = true;

/*
 * Number of seconds to wait between ratings
 */
$_MG_CONF['rating_speedlimit'] = 45;

/*
 * Set the maximum number of media items to display in the Media Manage Screen
 */

$_MG_CONF['mediamanage_items'] = 200;

/*
 * If set to 1, MG will not automatically populate the video playback
 *  resolution, instead it will use the default settings
 */

$_MG_CONF['use_default_resolution'] = 0;

/*
 * if set to 1, MG will use the larger stars in the album view for ratings
 */

$_MG_CONF['use_large_stars'] = 0;

/*
 * By default, Media Gallery will play MPEG videos with Apple's QuickTime
 * player. If you wish to use Microsoft's Windows Media Player instead,
 * set this variable to 1.
 */

$_MG_CONF['use_wmp_mpeg'] = 0;

/*
 * By default, Media Gallery will attempt to extract the actual image capture
 * date from the meta data included by many digital cameras and graphics
 * packages.  If you prefer to always use the upload date (the date you added
 * the image to your Media Gallery album) as the displayed date, set this
 * variable to 1.
 */

$_MG_CONF['use_upload_time'] = 0;

/**
 * FFMPEG Command line options
 *
 * There are lots of versions of ffmpeg out there, some work with one set of
 * switches and some don't.  You can easily modify the commands used to create
 * thumbnails from videos by modifying the arguments below.  The first %s is
 * the source video and the second %s is the destination thumbnail, both %s
 * need to be in the command.
 */

$_MG_CONF['ffmpeg_command_args'] = ' -i %s -f mjpeg -t 0.01 -y %s';

// $_MG_CONF['ffmpeg_command_args'] = ' -i %s -f mjpeg -an -r 1 -ss 00:00:03 -vframes 1 -y %s';
// $_MG_CONF['ffmpeg_command_args'] = ' -i %s -f singlejpeg -an -r 1 -ss 00:00:03 -vframes 1 -y %s';
// --- RIVA FLV Encoded / converter for Windows command line
// $_MG_CONF['ffmpeg_command_args'] = ' -an -y  -i "%s" -t 0.001 -s 640x480 -deinterlace   -hq -f image2 "%s"';


/*
 * Default thumbnails for non-media type files
 *
 * This allows you to specify new default thumbnails for non-media file types.
 * Place the thumbnail image in the mediaobjects/ directory.
 *
 */

$_MG_CONF['dt']['pdf'] = 'pdf.png';
$_MG_CONF['dt']['zip'] = 'zip.png';

/*
 * The JavaScript used by the lightbox slideshow can cause
 * conflicts with other JS libraries.  You can set this to true to disable
 * the lightbox slideshow feature.
 */
$_MG_CONF['disable_lightbox'] = false;

/*
 * If you want Media Gallery to update the 'last updated' time for all parent
 * albums, set this to true.
 */
$_MG_CONF['update_parent_lastupdated'] = true; //false;

/*
 * If you want to allow users who 'own' (uploaded) a media item to be able
 * to also edit the media item, set this value to true.
 */
$_MG_CONF['allow_user_edit'] = false; // Do we need this?

/*
 * Media Gallery provides limited support for including remotely hosted
 * images in your albums.  Your web host must support the CURL PHP extension
 * or allow opening remote URLs to take full advantage of this features.
 * To enable remote image support, set this value to true.
 */
$_MG_CONF['enable_remote_images'] = true;

/*
 * Set whether or not click image and go next image
 *   true: display the next image
 *   false: change the display size (full size or normal size)
 */
$_MG_CONF['click_image_and_go_next'] = true;

/*
 * Set whether or not hide the dialog select the destination album, on the media display page
 */
$_MG_CONF['hide_jumpbox_on_mediaview'] = true;

/*
 * Set whether or not loop turning over the media display page at the top or the end
 */
$_MG_CONF['enable_loop_pagination'] = true;

/*
 * Set the default of the shape (aspect ratio) of a random image on the side block area
 * 0:original, 1:square
 */
$_MG_CONF['random_img_ratio'] = 0;


/* --------------------------------------------------------------------------------- */

define("MG_JPG",1);
define("MG_PNG",2);
define("MG_TIF",4);
define("MG_GIF",8);
define("MG_BMP",16);
define("MG_TGA",32);
define("MG_PSD",64);
define("MG_MP3",128);
define("MG_OGG",256);
define("MG_ASF",512);
define("MG_SWF",1024);
define("MG_MOV",2048);
define("MG_MP4",4096);
define("MG_MPG",8192);
define("MG_ZIP",16384);
define("MG_OTHER",32768);
define("MG_PDF",65536);
define("MG_FLV",131072);
define("MG_RFLV",262144);
define("MG_EMB",524288);

if (!defined ('UC_SELECTED')) define('UC_SELECTED', (XHTML == '') ? 'selected' : 'selected="selected"');
if (!defined ('UC_CHECKED'))  define('UC_CHECKED',  (XHTML == '') ? 'checked'  : 'checked="checked"'  );
if (!defined ('UC_READONLY')) define('UC_READONLY', (XHTML == '') ? 'readonly' : 'readonly="readonly"');
if (!defined ('UC_DISABLED')) define('UC_DISABLED', (XHTML == '') ? 'disabled' : 'disabled="disabled"');

// This is a list of valid extensions for image media thumbnails / display images
$_MG_CONF['validExtensions'] = array('.jpg','.png','.gif','.bmp');

// placeholder until implemented
$_MG_CONF['ad_shopping_cart'] = 0;

$swfjsinclude = 0;
$mgLightBox = 0;

$_MG_CONF['random_skin'] = 'default';

$_MG_CONF['tmp_path'] = $_CONF['path'] . 'plugins/mediagallery/tmp/';

$_MG_CONF['rater_units_num'] = 5;

/**
* Load the plugin configuration
*/

require_once $_CONF['path_system'] . 'classes/config.class.php';
$plg_config = config::get_instance();
$temp = $plg_config->get_config('mediagallery');
if (is_array($temp)) {
    $_MG_CONF = array_merge($_MG_CONF, $temp);
}

if ($_CONF['loginrequired'] == 1) {
    $_MG_CONF['loginrequired'] = 1;
}

/*
$_MG_CONF['up_mp3_player_enabled'] = 0;

if ($_MG_CONF['installed_version']) {
    $_MG_CONF['dfid'] = '19';
	if (COM_versionCompare(VSERSION, '2.2.2', '>=') {
        $_MG_CONF['dateformat'] = Locale::dateFormatIdToString($_MG_CONF['dfid']);
	} else {
        $_MG_CONF['dateformat'] = DB_getItem($_TABLES['dateformats'], 'format', "dfid = {$_MG_CONF['dfid']}");
	}

    // safety checks....
    if ($_MG_CONF['album_display_columns'] < 1) {
        $_MG_CONF['album_display_columns'] = 1;
    }
    if ($_MG_CONF['album_display_rows'] < 1) {
        $_MG_CONF['album_display_rows'] = 9;
    }
}
*/
if (version_compare($_MG_CONF['installed_version'], '1.7.0', '>=')) {
	if (COM_versionCompare(VERSION, '2.2.2', '>=')) {
        $_MG_CONF['dateformat'] = \Geeklog\Locale::dateFormatIdToString($_MG_CONF['dfid']);
	} else {
        $_MG_CONF['dateformat'] = empty($_MG_CONF['dfid'])
					? ''
					: DB_getItem($_TABLES['dateformats'], 'format', "dfid = {$_MG_CONF['dfid']}");
	}
}

$_MG_CONF['path_to_imagemagick'] = '';
if ($_CONF['image_lib'] == 'imagemagick') {
    $tmpstr = $_CONF['path_to_mogrify'];
    if (strtolower(substr($tmpstr, -4)) == '.exe') {
        $tmpstr = substr($tmpstr, 0, strlen($tmpstr) - 4);
    }
    if (strtolower(substr($tmpstr, -8)) == '/mogrify') {
        $tmpstr = substr($tmpstr, 0, strlen($tmpstr) - 7); // Note that the path must end in a slash
    }
    $_MG_CONF['path_to_imagemagick'] = $tmpstr;
}


$_MG_CONF['ad_valid_formats'] =
    $_MG_CONF['ad_valid_format_jpg'] * MG_JPG +
    $_MG_CONF['ad_valid_format_png'] * MG_PNG +
    $_MG_CONF['ad_valid_format_tif'] * MG_TIF +
    $_MG_CONF['ad_valid_format_gif'] * MG_GIF +
    $_MG_CONF['ad_valid_format_bmp'] * MG_BMP +
    $_MG_CONF['ad_valid_format_tga'] * MG_TGA +
    $_MG_CONF['ad_valid_format_psd'] * MG_PSD +
    $_MG_CONF['ad_valid_format_mp3'] * MG_MP3 +
    $_MG_CONF['ad_valid_format_ogg'] * MG_OGG +
    $_MG_CONF['ad_valid_format_asf'] * MG_ASF +
    $_MG_CONF['ad_valid_format_swf'] * MG_SWF +
    $_MG_CONF['ad_valid_format_mov'] * MG_MOV +
    $_MG_CONF['ad_valid_format_mp4'] * MG_MP4 +
    $_MG_CONF['ad_valid_format_mpg'] * MG_MPG +
    $_MG_CONF['ad_valid_format_flv'] * MG_FLV +
    $_MG_CONF['ad_valid_format_rflv'] * MG_RFLV +
    $_MG_CONF['ad_valid_format_emb'] * MG_EMB +
    $_MG_CONF['ad_valid_format_zip'] * MG_ZIP +
    $_MG_CONF['ad_valid_format_other'] * MG_OTHER;

$_MG_CONF['member_valid_formats'] =
    $_MG_CONF['member_valid_format_jpg'] * MG_JPG +
    $_MG_CONF['member_valid_format_png'] * MG_PNG +
    $_MG_CONF['member_valid_format_tif'] * MG_TIF +
    $_MG_CONF['member_valid_format_gif'] * MG_GIF +
    $_MG_CONF['member_valid_format_bmp'] * MG_BMP +
    $_MG_CONF['member_valid_format_tga'] * MG_TGA +
    $_MG_CONF['member_valid_format_psd'] * MG_PSD +
    $_MG_CONF['member_valid_format_mp3'] * MG_MP3 +
    $_MG_CONF['member_valid_format_ogg'] * MG_OGG +
    $_MG_CONF['member_valid_format_asf'] * MG_ASF +
    $_MG_CONF['member_valid_format_swf'] * MG_SWF +
    $_MG_CONF['member_valid_format_mov'] * MG_MOV +
    $_MG_CONF['member_valid_format_mp4'] * MG_MP4 +
    $_MG_CONF['member_valid_format_mpg'] * MG_MPG +
    $_MG_CONF['member_valid_format_flv'] * MG_FLV +
    $_MG_CONF['member_valid_format_rflv'] * MG_RFLV +
    $_MG_CONF['member_valid_format_emb'] * MG_EMB +
    $_MG_CONF['member_valid_format_zip'] * MG_ZIP +
    $_MG_CONF['member_valid_format_other'] * MG_OTHER;

// Restored from master. Remaining functions follow unchanged in the source branch and will be refactored in a subsequent commit.
