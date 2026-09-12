<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | MediaGallery 1.8.0 runtime configuration                                 |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

function MG_prepareDirectory180($path)
{
    if (is_dir($path)) {
        return is_writable($path);
    }

    if (@mkdir($path, 0755, true)) {
        return true;
    }

    COM_errorLog('Media Gallery 1.8.0: unable to create directory ' . $path);
    return false;
}

function MG_prepareMediaStorage180($root)
{
    if (!MG_prepareDirectory180($root)) {
        return false;
    }

    if (!MG_prepareDirectory180($root . 'covers/')) {
        return false;
    }

    $buckets = str_split('0123456789abcdef');
    foreach (array('orig', 'disp', 'tn') as $type) {
        $typePath = $root . $type . '/';
        if (!MG_prepareDirectory180($typePath)) {
            return false;
        }

        foreach ($buckets as $bucket) {
            if (!MG_prepareDirectory180($typePath . $bucket . '/')) {
                return false;
            }
        }
    }

    return true;
}

function MG_applyRuntimeConfiguration180()
{
    global $_CONF, $_MG_CONF, $_TABLES;

    $_MG_CONF['pi_version'] = '1.8.0';

    /*
     * functions.inc is loaded by Geeklog while a plugin archive is being
     * inspected, before a fresh install has inserted the plugin row. In that
     * phase installed_version may legitimately be absent. Never assume it is
     * available merely because the runtime bootstrap has been loaded.
     */
    $installedVersion = '';
    if (isset($_MG_CONF['installed_version']) && $_MG_CONF['installed_version'] !== '') {
        $installedVersion = (string) $_MG_CONF['installed_version'];
    } elseif (isset($_TABLES['plugins'])) {
        $dbVersion = DB_getItem(
            $_TABLES['plugins'],
            'pi_version',
            "pi_name = 'mediagallery'"
        );
        if ($dbVersion !== false && $dbVersion !== null && $dbVersion !== '') {
            $installedVersion = (string) $dbVersion;
        }
    }

    $_MG_CONF['installed_version'] = $installedVersion;
    $_MG_CONF['var_current_code'] = ($installedVersion !== '')
        ? version_compare($installedVersion, $_MG_CONF['pi_version'], '>=')
        : false;

    $_MG_CONF['path_html'] = $_CONF['path_html'] . 'mediagallery/';
    $_MG_CONF['site_url'] = $_CONF['site_url'] . '/mediagallery';
    $_MG_CONF['admin_url'] = $_CONF['site_admin_url'] . '/plugins/mediagallery/';
    $_MG_CONF['path_admin'] = $_CONF['path_html'] . 'admin/plugins/mediagallery/';
    $_MG_CONF['template_path'] = $_CONF['path'] . 'plugins/mediagallery/templates';

    /*
     * Public media storage:
     * - explicit path_images + images_url => site-specific storage (multisite)
     * - otherwise => historical MediaGallery storage for full compatibility
     *
     * There is deliberately no automatic URL derivation from path_images.
     * A standard single-site installation therefore keeps its existing media
     * location unless the site explicitly opts in to site-specific storage.
     */
    if (!empty($_CONF['path_images']) && !empty($_CONF['images_url'])) {
        $_MG_CONF['path_mediaobjects'] = rtrim($_CONF['path_images'], '/\\') . '/mediagallery/';
        $_MG_CONF['mediaobjects_url'] = rtrim($_CONF['images_url'], '/') . '/mediagallery';
        MG_prepareMediaStorage180($_MG_CONF['path_mediaobjects']);
    } else {
        $_MG_CONF['path_mediaobjects'] = $_CONF['path_html'] . 'mediagallery/mediaobjects/';
        $_MG_CONF['mediaobjects_url'] = $_CONF['site_url'] . '/mediagallery/mediaobjects';
    }

    /*
     * Private working directories are site runtime values and are never stored
     * in the shared Configuration API. path_data keeps them isolated in a
     * shared-code multisite setup while remaining harmless on a single site.
     */
    if (!empty($_CONF['path_data'])) {
        $workRoot = rtrim($_CONF['path_data'], '/\\') . '/mediagallery/';
        $_MG_CONF['tmp_path'] = $workRoot . 'tmp/';
        $_MG_CONF['ftp_path'] = $workRoot . 'uploads/';

        MG_prepareDirectory180($_MG_CONF['tmp_path']);
        MG_prepareDirectory180($_MG_CONF['ftp_path']);
    }
}

function MG_getConfigSettings180()
{
    return array(
        array('link_to_member_album',        1,                               'select', 0),
        array('rating_speedlimit',           45,                              'text',   0),
        array('mediamanage_items',           200,                             'text',   0),
        array('use_default_resolution',      0,                               'select', 0),
        array('use_large_stars',             0,                               'select', 0),
        array('use_upload_time',             0,                               'select', 0),
        array('ffmpeg_command_args',         ' -i %s -f mjpeg -t 0.01 -y %s','text',   0),
        array('disable_lightbox',            0,                               'select', 0),
        array('update_parent_lastupdated',   1,                               'select', 0),
        array('allow_user_edit',             0,                               'select', 0),
        array('enable_remote_images',        1,                               'select', 0),
        array('click_image_and_go_next',     1,                               'select', 0),
        array('hide_jumpbox_on_mediaview',   1,                               'select', 0),
        array('enable_loop_pagination',      1,                               'select', 0),
        array('random_img_ratio',            0,                               'select', 0),
    );
}

function MG_updateConfig180()
{
    global $_CONF;

    require_once $_CONF['path_system'] . 'classes/config.class.php';

    $c = config::get_instance();
    $group = 'mediagallery';

    // During a fresh plugin installation the base configuration group is
    // created by plugin_initconfig_mediagallery(). Do not try to add 1.8
    // entries before that base group exists.
    if (!$c->group_exists($group)) {
        return false;
    }

    $existing = $c->get_config($group);
    if (!is_array($existing)) {
        $existing = array();
    }

    // These values are site-specific runtime paths. They must not live in the
    // shared Configuration API on either Geeklog 2.1.1 or 2.2.2.
    foreach (array('tmp_path', 'ftp_path') as $runtimePath) {
        if (array_key_exists($runtimePath, $existing)) {
            $c->del($runtimePath, $group);
            unset($existing[$runtimePath]);
        }
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

    // functions.inc can be loaded while the installer is still creating the
    // plugin. The normal install hook will create the base configuration first.
    if (!$c->group_exists('mediagallery')) {
        return;
    }

    $existing = $c->get_config('mediagallery');
    $needsUpdate = !is_array($existing)
        || !array_key_exists('rating_speedlimit', $existing)
        || array_key_exists('tmp_path', $existing)
        || array_key_exists('ftp_path', $existing);

    if ($needsUpdate) {
        if (!MG_updateConfig180()) {
            return;
        }
        $existing = $c->get_config('mediagallery');
    }

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
    global $LANG_configsections, $LANG_confignames, $LANG_fs;

    if (!isset($LANG_configsections['mediagallery'])) {
        $LANG_configsections['mediagallery'] = array();
    }
    if (!isset($LANG_confignames['mediagallery'])) {
        $LANG_confignames['mediagallery'] = array();
    }
    if (!isset($LANG_fs['mediagallery'])) {
        $LANG_fs['mediagallery'] = array();
    }

    // Geeklog's Configuration UI resolves fieldset legends from $LANG_fs,
    // not from $LANG_configsections.
    if (!isset($LANG_fs['mediagallery']['fs_runtime180'])) {
        $LANG_fs['mediagallery']['fs_runtime180'] = 'Runtime and advanced behavior';
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
