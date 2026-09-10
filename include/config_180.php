<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | MediaGallery 1.8.0 runtime configuration                                 |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

/**
 * Apply MediaGallery 1.8.0 runtime configuration.
 *
 * @return void
 */
function MG_applyRuntimeConfiguration180()
{
    global $_CONF, $_MG_CONF;

    $_MG_CONF['pi_version'] = '1.8.0';
    $_MG_CONF['var_current_code'] = version_compare(
        $_MG_CONF['installed_version'],
        $_MG_CONF['pi_version'],
        '>='
    );

    // Runtime/derived locations. These are intentionally not stored in the
    // Geeklog Configuration API.
    $_MG_CONF['path_html'] = $_CONF['path_html'] . 'mediagallery/';
    $_MG_CONF['site_url'] = $_CONF['site_url'] . '/mediagallery';
    $_MG_CONF['admin_url'] = $_CONF['site_admin_url'] . '/plugins/mediagallery/';
    $_MG_CONF['path_admin'] = $_CONF['path_html'] . 'admin/plugins/mediagallery/';
    $_MG_CONF['template_path'] = $_CONF['path'] . 'plugins/mediagallery/templates';

    $hasSiteImageStorage = !empty($_CONF['path_images']) && !empty($_CONF['images_url']);

    if ($hasSiteImageStorage) {
        $_MG_CONF['path_mediaobjects'] = rtrim($_CONF['path_images'], '/\\') . '/mediagallery/';
        $_MG_CONF['mediaobjects_url'] = rtrim($_CONF['images_url'], '/') . '/mediagallery';

        // In a multisite setup path_data should already be site-specific.
        // Keep non-public work files out of the shared plugin directory.
        if (!empty($_CONF['path_data'])) {
            $workRoot = rtrim($_CONF['path_data'], '/\\') . '/mediagallery/';
            $_MG_CONF['tmp_path'] = $workRoot . 'tmp/';
            $_MG_CONF['ftp_path'] = $workRoot . 'uploads/';
        }
    } else {
        // Historical behavior for normal/single-site installations.
        $_MG_CONF['path_mediaobjects'] = $_CONF['path_html'] . 'mediagallery/mediaobjects/';
        $_MG_CONF['mediaobjects_url'] = $_CONF['site_url'] . '/mediagallery/mediaobjects';
    }
}

/**
 * Add the live 1.8.0 settings that were historically hard-coded.
 *
 * The migration is idempotent: existing administrator values are never
 * overwritten, and valid false/zero values are not mistaken for missing keys.
 *
 * @return bool
 */
function MG_updateConfig180()
{
    global $_CONF;

    require_once $_CONF['path_system'] . 'classes/config.class.php';

    $c = config::get_instance();
    $group = 'mediagallery';
    $existing = $c->get_config($group);

    if (!is_array($existing)) {
        $existing = array();
    }

    // Put the new settings in a separate fieldset under the existing General
    // tab. This avoids reshuffling existing Configuration API entries during
    // upgrade and keeps the migration safe for 1.7.x installations.
    if (!array_key_exists('rating_speedlimit', $existing)) {
        $c->add('fs_runtime180', NULL, 'fieldset', 0, 3, NULL, 0, true, $group, 0);
    }

    $settings = array(
        // name                       default                         type      select set
        array('link_to_member_album',        1,                             'select', 0),
        array('rating_speedlimit',           45,                            'text',   0),
        array('mediamanage_items',           200,                           'text',   0),
        array('use_default_resolution',      0,                             'select', 0),
        array('use_large_stars',             0,                             'select', 0),
        array('use_upload_time',             0,                             'select', 0),
        array('ffmpeg_command_args',         ' -i %s -f mjpeg -t 0.01 -y %s','text',  0),
        array('disable_lightbox',            0,                             'select', 0),
        array('update_parent_lastupdated',   1,                             'select', 0),
        array('allow_user_edit',             0,                             'select', 0),
        array('enable_remote_images',        1,                             'select', 0),
        array('click_image_and_go_next',     1,                             'select', 0),
        array('hide_jumpbox_on_mediaview',   1,                             'select', 0),
        array('enable_loop_pagination',      1,                             'select', 0),
        array('random_img_ratio',            0,                             'select', 0),
    );

    $order = 900;
    foreach ($settings as $setting) {
        list($name, $default, $type, $selectSet) = $setting;

        if (array_key_exists($name, $existing)) {
            continue;
        }

        $c->add(
            $name,
            $default,
            $type,
            0,
            3,
            $selectSet,
            $order++,
            true,
            $group,
            0
        );
    }

    return true;
}

/**
 * Provide readable labels for the 1.8.0 Configuration API additions.
 *
 * These English fallbacks are used until each translation file is updated.
 * Existing translated MediaGallery labels are left untouched.
 *
 * @return void
 */
function MG_addConfigLanguage180()
{
    global $LANG_configsections, $LANG_confignames;

    if (!isset($LANG_configsections['mediagallery'])) {
        $LANG_configsections['mediagallery'] = array();
    }
    if (!isset($LANG_confignames['mediagallery'])) {
        $LANG_confignames['mediagallery'] = array();
    }

    if (!isset($LANG_configsections['mediagallery']['fs_runtime180'])) {
        $LANG_configsections['mediagallery']['fs_runtime180'] = 'Runtime and advanced behavior';
    }

    $labels = array(
        'link_to_member_album'      => 'Show link to member album',
        'rating_speedlimit'         => 'Rating speed limit (seconds)',
        'mediamanage_items'         => 'Maximum media items in management screen',
        'use_default_resolution'    => 'Use default video resolution',
        'use_large_stars'           => 'Use large rating stars',
        'use_upload_time'           => 'Use upload time instead of capture time',
        'ffmpeg_command_args'       => 'FFmpeg thumbnail command arguments',
        'disable_lightbox'          => 'Disable lightbox slideshow',
        'update_parent_lastupdated' => 'Update parent album timestamps',
        'allow_user_edit'           => 'Allow media owner to edit media',
        'enable_remote_images'      => 'Enable remote images',
        'click_image_and_go_next'   => 'Click image to display next media',
        'hide_jumpbox_on_mediaview' => 'Hide album jump box on media view',
        'enable_loop_pagination'    => 'Loop media pagination',
        'random_img_ratio'          => 'Random image aspect ratio',
    );

    foreach ($labels as $name => $label) {
        if (!isset($LANG_confignames['mediagallery'][$name])) {
            $LANG_confignames['mediagallery'][$name] = $label;
        }
    }
}

/**
 * Return runtime storage information for diagnostics/admin UI.
 *
 * @return array
 */
function MG_getStorageInfo180()
{
    global $_CONF, $_MG_CONF;

    return array(
        'mode' => (!empty($_CONF['path_images']) && !empty($_CONF['images_url']))
            ? 'site-images'
            : 'legacy',
        'media_path' => isset($_MG_CONF['path_mediaobjects']) ? $_MG_CONF['path_mediaobjects'] : '',
        'media_url' => isset($_MG_CONF['mediaobjects_url']) ? $_MG_CONF['mediaobjects_url'] : '',
        'tmp_path' => isset($_MG_CONF['tmp_path']) ? $_MG_CONF['tmp_path'] : '',
        'uploads_path' => isset($_MG_CONF['ftp_path']) ? $_MG_CONF['ftp_path'] : '',
    );
}
