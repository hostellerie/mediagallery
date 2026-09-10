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
 * The 1.7.x code initializes legacy defaults and loads the Geeklog
 * Configuration API first. This function then applies 1.8.0 derived values.
 * Derived paths are deliberately not stored in the Configuration API.
 *
 * Standard installations keep the historical mediaobjects directory.
 * Sites that explicitly define both path_images and images_url use the
 * site-specific image tree instead.
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

    // These locations are derived from Geeklog and are not administrator
    // preferences. Keep them out of the online plugin configuration.
    $_MG_CONF['path_html'] = $_CONF['path_html'] . 'mediagallery/';
    $_MG_CONF['site_url'] = $_CONF['site_url'] . '/mediagallery';
    $_MG_CONF['admin_url'] = $_CONF['site_admin_url'] . '/plugins/mediagallery/';
    $_MG_CONF['path_admin'] = $_CONF['path_html'] . 'admin/plugins/mediagallery/';
    $_MG_CONF['template_path'] = $_CONF['path'] . 'plugins/mediagallery/templates';

    $hasSiteImageStorage = !empty($_CONF['path_images']) && !empty($_CONF['images_url']);

    if ($hasSiteImageStorage) {
        $_MG_CONF['path_mediaobjects'] = rtrim($_CONF['path_images'], '/\\') . '/mediagallery/';
        $_MG_CONF['mediaobjects_url'] = rtrim($_CONF['images_url'], '/') . '/mediagallery';

        // path_data is already site-specific in a properly configured Geeklog
        // multisite setup. Use it for non-public working files so sites sharing
        // one plugin code tree do not share upload staging or temporary files.
        if (!empty($_CONF['path_data'])) {
            $workRoot = rtrim($_CONF['path_data'], '/\\') . '/mediagallery/';
            $_MG_CONF['tmp_path'] = $workRoot . 'tmp/';
            $_MG_CONF['ftp_path'] = $workRoot . 'uploads/';
        }
    } else {
        // Backwards-compatible MediaGallery location for normal/single-site
        // installs and for existing sites that do not define images_url.
        $_MG_CONF['path_mediaobjects'] = $_CONF['path_html'] . 'mediagallery/mediaobjects/';
        $_MG_CONF['mediaobjects_url'] = $_CONF['site_url'] . '/mediagallery/mediaobjects';
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
