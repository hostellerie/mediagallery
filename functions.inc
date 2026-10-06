<?php
// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | MediaGallery 1.9.0 bootstrap                                             |
// +--------------------------------------------------------------------------+

if (strpos(strtolower($_SERVER['PHP_SELF']), strtolower(basename(__FILE__))) !== false) {
    die('This file can not be used on its own!');
}

/*
 * Keep the proven legacy implementation isolated while the maintained
 * modernization layers provide current configuration, interoperability,
 * storage, security and UI behavior.
 */
require_once __DIR__ . '/version.php';

require_once __DIR__ . '/include/input_compat_180.php';
require_once __DIR__ . '/functions_legacy.inc';
require_once __DIR__ . '/include/interoperability_180.php';

require_once __DIR__ . '/include/config_180.php';
require_once __DIR__ . '/include/schema_180.php';
require_once __DIR__ . '/include/email_180.php';
require_once __DIR__ . '/include/upload_security_180.php';
require_once __DIR__ . '/include/tmp_cleanup_180.php';
require_once __DIR__ . '/services.inc.php';
require_once __DIR__ . '/include/media_picker_180.php';

MG_addConfigLanguage180();
MG_ensureConfig180();
MG_ensureAlbumSchema180();
MG_applyRuntimeConfiguration180();
MG_cleanupStaleTemp180();
