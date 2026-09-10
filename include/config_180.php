<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | MediaGallery 1.8.0 runtime configuration                                 |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

function MG_prepareWorkDirectory180($path)
{
    if (is_dir($path)) {
        return is_writable($path);
    }

    if (@mkdir($path, 0755, true)) {
        return true;
    }

    COM_errorLog('Media Gallery 1.8.0: unable to create working directory ' . $path);
    return false;
}

function MG_applyRuntimeConfiguration180()
{
    global $_CONF, $_MG_CONF;

    $_MG_CONF['pi_version'] = '1.8.0';
    $_MG_CONF['var_current_code'] = version_compare(
        $_MG_CONF['installed_version'],
        $_MG_CONF['pi_version'],
        '>='
    );

    $_MG_CONF['path_html'] = $_CONF['path_html'] . 'mediagallery/';
    $_MG_CONF['site_url'] = $_CONF['site_url'] . '/mediagallery';
    $_MG_CONF['admin_url'] = $_CONF['site_admin_url'] . '/plugins/mediagallery/';
    $_MG_CONF['path_admin'] = $_CONF['path_html'] . 'admin/plugins/mediagallery/';
    $_MG_CONF['template_path'] = $_CONF['path'] . 'plugins/mediagallery/templates';

    $hasSiteImageStorage = !empty($_CONF['path_images']) && !empty($_CONF['images_url']);

    if ($hasSiteImageStorage) {
        $_MG_CONF['path_mediaobjects'] = rtrim($_CONF['path_images'], '/\\') . '/mediagallery/';
        $_MG_CONF['mediaobjects_url'] = rtrim($_CONF['images_url'], '/') . '/mediagallery';

        if (!empty($_CONF['path_data'])) {
            $workRoot = rtrim($_CONF['path_data'], '/\\') . '/mediagallery/';
            $_MG_CONF['tmp_path'] = $workRoot . 'tmp/';
            $_MG_CONF['ftp_path'] = $workRoot . 'uploads/';

            MG_prepareWorkDirectory180($_MG_CONF['tmp_path']);
            MG_prepareWorkDirectory180($_MG_CONF['ftp_path']);
        }
    } else {
        $_MG_CONF['path_mediaobjects'] = $_CONF['path_html'] . 'mediagallery/mediaobjects/';
        $_MG_CONF['mediaobjects_url'] = $_CONF['site_url'] . '/mediagallery/mediaobjects';
    }
}

function MG_getConfigSettings180()
{
    return array(
        array('link_to_member_album',        1,                              'select', 0),
        array('rating_speedlimit',           45,                             'text',   0),
        array('mediamanage_items',           200,                            'text',   0),
        array('use_default_resolution',      0,                              'select', 0),
        array('use_large_stars',             0,                              'select', 0),
        array('use_upload_time',             0,                              'select', 0),
        array('ffmpeg_command_args',         ' -i %s -f mjpeg -t 0.01 -y %s', 'text',  0),
        array('disable_lightbox',            0,                              'select', 0),
        array('update_parent_lastupdated',   1,                              'select', 0),
        array('allow_user_edit',             0,                              'select', 0),
        array('enable_remote_images',        1,                              'select', 0),
        array('click_image_and_go_next',     1,                              'select', 0),
        array('hide_jumpbox_on_mediaview',   1,                              'select', 0),
        array('enable_loop_pagination',      1,                              'select', 0),
        array('random_img_ratio',            0,                              'select', 0),
    );
}

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

    if (!array_key_exists('rating_speedlimit', $existing)) {
        $c->add('fs_runtime180', NULL, 'fieldset', 0, 3, NULL, 0, true, $group, 0);
    }

    $order = 900;
    foreach (MG_getConfigSettings180() as $setting) {
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
 * Ensure fresh 1.8.0 installations receive the same Configuration API keys
 * as upgraded installations. This is intentionally idempotent.
 */
function MG_ensureConfig180()
{
    global $_CONF, $_MG_CONF;

    require_once $_CONF['path_system'] . 'classes/config.class.php';

    $c = config::get_instance();
    $existing = $c->get_config('mediagallery');

    if (!is_array($existing) || !array_key_exists('rating_speedlimit', $existing)) {
        MG_updateConfig180();
        $existing = $c->get_config('mediagallery');
    }

    // Refresh only the new 1.8 settings into runtime configuration. This keeps
    // administrator values authoritative even on the first request after an
    // installation or upgrade.
    if (is_array($existing)) {
        foreach (MG_getConfigSettings180() as $setting) {
            $name = $setting[0];
            if (array_key_exists($name, $existing)) {
                $_MG_CONF[$name] = $existing[$name];
            }
        }
    }
}

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
