<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | autoinstall.php                                                          |
// |                                                                          |
// | This file provides helper functions for the automatic plugin install.    |
// +--------------------------------------------------------------------------+
// | Copyright (C) 2015 by the following authors:                             |
// |                                                                          |
// | Yoshinori Tahara       taharaxp AT gmail DOT com                         |
// |                                                                          |
// | Based on the Media Gallery Plugin for glFusion CMS                       |
// | Copyright (C) 2002-2008 by the following authors:                        |
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

function plugin_autoinstall_mediagallery($pi_name)
{
    $pi_name         = 'mediagallery';
    $pi_display_name = 'Media Gallery';
    $pi_admin        = $pi_name . ' Admin';
    $pi_config       = $pi_name . ' Config';

    $info = array(
        'pi_name'         => $pi_name,
        'pi_display_name' => $pi_display_name,
        'pi_version'      => '1.8.0',
        'pi_gl_version'   => '2.0.0',
        'pi_homepage'     => 'https://github.com/hostellerie/mediagallery'
    );

    $groups = array(
        $pi_admin  => 'Users in this group can administer the Media Gallery plugin',
        $pi_config => 'Users in this group can configure the Media Gallery plugin'
    );

    $features = array(
        $pi_name . '.admin'  => 'Ability to administer the Media Gallery Plugin',
        $pi_name . '.config' => 'Ability to configure the Media Gallery Plugin'
    );

    $mappings = array(
        $pi_name . '.admin'  => array($pi_admin),
        $pi_name . '.config' => array($pi_config)
    );

    $tables = array(
        'mg_albums',
        'mg_media',
        'mg_media_albums',
        'mg_usage_tracking',
        'mg_mediaqueue',
        'mg_media_album_queue',
        'mg_playback_options',
        'mg_userprefs',
        'mg_exif_tags',
        'mg_watermarks',
        'mg_category',
        'mg_sessions',
        'mg_session_items',
        'mg_session_log',
        'mg_sort',
        'mg_rating',
    );

    $requires = array(
        array(
            'db'      => 'mysql',
            'version' => '4.1'
        )
    );

    return array(
        'info'      => $info,
        'groups'    => $groups,
        'features'  => $features,
        'mappings'  => $mappings,
        'tables'    => $tables,
        'requires'  => $requires
    );
}

function plugin_load_configuration_mediagallery($pi_name)
{
    global $_CONF;

    $base_path = $_CONF['path'] . 'plugins/' . $pi_name . '/';

    require_once $_CONF['path_system'] . 'classes/config.class.php';
    require_once $base_path . 'install_defaults.php';

    if (!plugin_initconfig_mediagallery()) {
        return false;
    }

    // Add the 1.8.0 settings on fresh installs as well as upgrades without
    // duplicating them or resetting values.
    require_once $base_path . 'include/config_180.php';
    return MG_updateConfig180();
}

function plugin_postinstall_mediagallery($pi_name)
{
    global $_TABLES;

    $pi_name = 'mediagallery';

    $admin_group_id  = DB_getItem($_TABLES['groups'], 'grp_id', "grp_name = 'mediagallery Admin'");
    $config_group_id = DB_getItem($_TABLES['groups'], 'grp_id', "grp_name = 'mediagallery Config'");

    $MG_SQL = array();

    $MG_SQL[] = "INSERT INTO {$_TABLES['blocks']} (is_enabled, name, type, title, blockorder, content, rdfurl, rdfupdated, onleft, phpblockfn, help, group_id, owner_id, perm_owner, perm_group, perm_members,perm_anon) VALUES (0, 'mgrandom', 'phpblock', 'Random Image',        0, '', '', 0, 1, 'phpblock_mg_randommedia','', 4, 2, 3, 3, 2, 2);";
    $MG_SQL[] = "INSERT INTO {$_TABLES['blocks']} (is_enabled, name, type, title, blockorder, content, rdfurl, rdfupdated, onleft, phpblockfn, help, group_id, owner_id, perm_owner, perm_group, perm_members,perm_anon) VALUES (0, 'mgenroll', 'phpblock', 'Member Album Enroll', 0, '', '', 0, 1, 'phpblock_mg_maenroll',   '', 4, 2, 3, 3, 2, 0);";
    $MG_SQL[] = "INSERT INTO {$_TABLES['vars']} VALUES ('{$pi_name}_gid', $admin_group_id)";
    $MG_SQL[] = "INSERT INTO {$_TABLES['vars']} VALUES ('{$pi_name}_cid', $config_group_id)";
    $MG_SQL[] = "INSERT INTO {$_TABLES['vars']} VALUES ('mg_last_usage_purge', 0)";

    foreach ($MG_SQL as $sql) {
        DB_query($sql);
        if (DB_error()) {
            COM_errorLog("SQL error in Media Gallery plugin postinstall, SQL: " . $sql);
            return false;
        }
    }

    return true;
}

function plugin_compatible_with_this_version_mediagallery($pi_name)
{
    global $_CONF, $_DB_dbms;

    $dbFile = $_CONF['path'] . 'plugins/' . $pi_name . '/sql/' . $_DB_dbms . '_install.php';
    if (!file_exists($dbFile)) {
        return false;
    }

    if (COM_versionCompare(VERSION, '2.0.0', '<')) {
        return false;
    }

    return true;
}

function MG_upgrade()
{
    global $_TABLES;

    $pi_name = 'mediagallery';
    $func = "plugin_autoinstall_$pi_name";
    $inst_parms = $func($pi_name);
    $code_version  = $inst_parms['info']['pi_version'];
    $pi_gl_version = $inst_parms['info']['pi_gl_version'];
    $pi_homepage   = $inst_parms['info']['pi_homepage'];
    $installed_version = DB_getItem($_TABLES['plugins'], 'pi_version', "pi_name = '$pi_name'");

    if ($installed_version == $code_version) {
        return true;
    }

    $func = "plugin_compatible_with_this_version_$pi_name";
    if (!$func($pi_name)) {
        return 3002;
    }

    $current_version = $installed_version;
    if (COM_versionCompare($current_version, '1.6.5', '<')) {
        return 3;
    }

    $done = false;
    while (!$done) {
        switch ($current_version) {
        case '1.6.5':
        case '1.6.6':
        case '1.6.7':
        case '1.6.8':
        case '1.6.9':
        case '1.6.10':
        case '1.6.11':
            if (MG_upgrade_1612() != 0) {
                break 2;
            }
            $current_version = '1.6.12';
            break;

        case '1.6.12':
        case '1.6.13':
        case '1.6.14':
        case '1.6.15':
        case '1.6.16':
        case '1.6.17':
            if (MG_upgrade_170() != 0) {
                break 2;
            }
            $current_version = '1.7.0';
            break;

        case '1.7.0':
        case '1.7.1':
        case '1.7.2':
        case '1.7.2.1':
        case '1.7.2.2':
        case '1.7.2.3':
        case '1.7.2.4':
        case '1.7.2.5':
        case '1.7.3':
            if (MG_upgrade_180() != 0) {
                break 2;
            }
            $current_version = '1.8.0';
            break;

        case '1.8.0':
        default:
            $done = true;
            break;
        }
    }

    DB_query("UPDATE {$_TABLES['plugins']} "
           . "SET pi_version = '" . DB_escapeString($code_version) . "', "
           . "pi_gl_version = '" . DB_escapeString($pi_gl_version) . "', "
           . "pi_homepage = '" . DB_escapeString($pi_homepage) . "' "
           . "WHERE pi_name = '" . DB_escapeString($pi_name) . "'");

    return 1;
}

function MG_upgrade_180()
{
    global $_CONF;

    require_once $_CONF['path'] . 'plugins/mediagallery/include/config_180.php';

    if (!MG_updateConfig180()) {
        COM_errorLog('Media Gallery 1.8.0: unable to update Configuration API entries.', 1);
        return 1;
    }

    COM_errorLog('Media Gallery 1.8.0: configuration/storage upgrade completed without moving media files.');

    return 0;
}

function MG_upgrade_1612()
{
    global $_TABLES;

    $grp_id = DB_getItem($_TABLES['groups'], 'grp_id', "grp_name = 'mediagallery Admin'");

    $_SQL = array();
    $_SQL[] = "REPLACE INTO {$_TABLES['mg_config']} VALUES ('ad_group_id', '$grp_id')";

    foreach ($_SQL as $sql) {
        COM_errorLOG("Media Gallery plugin 1.6.11 update: Executing SQL => " . $sql);
        DB_query($sql, 1);

        if (DB_error()) {
            COM_errorLog('SQL Error during Media Gallery plugin update', 1);
            return 1;
        }
    }

    return 0;
}

function MG_upgrade_170()
{
    global $_TABLES, $_CONF, $_DB_table_prefix;

    require_once $_CONF['path'] . 'plugins/mediagallery/install_defaults.php';
    mediagallery_update_ConfValues_1_7_0();

    $_SQL = array();

    $name_src  = $_DB_table_prefix . 'mg_postcard';
    $_SQL[] = "DROP TABLE `$name_src`";

    $name_src  = $_DB_table_prefix . 'mg_config';
    $_SQL[] = "DROP TABLE `$name_src`";

    $name_src  = $_DB_table_prefix . 'mg_albums';
    $_SQL[] = "ALTER TABLE `$name_src` DROP `enable_shutterfly`";

    $name_src  = $_DB_table_prefix . 'mg_media_queue';
    $name_dest = $_DB_table_prefix . 'mg_mediaqueue';
    $_SQL[] = "ALTER TABLE `$name_src` RENAME TO `$name_dest`";

    $name_src  = $_DB_table_prefix . 'mg_batch_sessions';
    $name_dest = $_DB_table_prefix . 'mg_sessions';
    $_SQL[] = "ALTER TABLE `$name_src` RENAME TO `$name_dest`";

    $name_src  = $_DB_table_prefix . 'mg_batch_session_log';
    $name_dest = $_DB_table_prefix . 'mg_session_log';
    $_SQL[] = "ALTER TABLE `$name_src` RENAME TO `$name_dest`";

    $name_src  = $_DB_table_prefix . 'mg_batch_session_items';
    $name_dest = $_DB_table_prefix . 'mg_session_items';
    $_SQL[] = "ALTER TABLE `$name_src` RENAME TO `$name_dest`";

    $name_src  = $_DB_table_prefix . 'mg_batch_session_items2';
    $_SQL[] = "DROP TABLE `$name_src`";

    $skins = array('border', 'default', 'mgAlbum', 'mgShadow', 'new_border', 'new_shadow', 'none');
    $sql = "SELECT * FROM {$_TABLES['mg_albums']}";
    $result = DB_query($sql);

    while ($A = DB_fetchArray($result)) {
        $_SQL[] = "UPDATE {$_TABLES['mg_albums']} SET skin='default' WHERE album_id=" . $A['album_id'];

        if (!in_array($A['image_skin'], $skins)) {
            $_SQL[] = "UPDATE {$_TABLES['mg_albums']} SET image_skin='default' WHERE album_id=" . $A['album_id'];
        }

        if (!in_array($A['display_skin'], $skins)) {
            $_SQL[] = "UPDATE {$_TABLES['mg_albums']} SET display_skin='default' WHERE album_id=" . $A['album_id'];
        }

        if (!in_array($A['album_skin'], $skins)) {
            $_SQL[] = "UPDATE {$_TABLES['mg_albums']} SET album_skin='default' WHERE album_id=" . $A['album_id'];
        }
    }

    foreach ($_SQL as $sql) {
        COM_errorLOG("Media Gallery plugin 1.7.0 update: Executing SQL => " . $sql);
        DB_query($sql, 1);

        if (DB_error()) {
            COM_errorLog('SQL Error during Media Gallery plugin update', 1);
            return 1;
        }
    }

    return 0;
}
