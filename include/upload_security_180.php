<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | upload_security_180.php                                                  |
// |                                                                          |
// | Upload security helpers for MediaGallery 1.8.0                           |
// +--------------------------------------------------------------------------+

if (stripos($_SERVER['PHP_SELF'], basename(__FILE__)) !== false) {
    die('This file can not be used on its own.');
}

/**
 * Return the lowercase final filename extension without the leading dot.
 *
 * @param string $filename
 * @return string
 */
function MG_uploadExtension180($filename)
{
    $filename = basename((string) $filename);
    $pos = strrpos($filename, '.');

    if ($pos === false) {
        return '';
    }

    return strtolower(substr($filename, $pos + 1));
}

/**
 * Reject extensions that can be interpreted as executable/server-side code.
 *
 * MediaGallery historically renamed only a few script extensions after MIME
 * detection. In traditional installations originals live below a public web
 * directory, so 1.8.0 rejects these extensions before the file enters the
 * processing pipeline.
 *
 * @param string $filename
 * @return bool
 */
function MG_isUnsafeUploadFilename180($filename)
{
    $base = strtolower(basename((string) $filename));
    $ext = MG_uploadExtension180($base);

    if ($base === '.htaccess' || $base === '.htpasswd' || $base === 'web.config') {
        return true;
    }

    $blocked = array(
        'php', 'php2', 'php3', 'php4', 'php5', 'php6', 'php7', 'php8',
        'phtml', 'pht', 'phtm', 'phar', 'phps',
        'cgi', 'fcgi', 'pl', 'pm', 'py', 'rb',
        'sh', 'bash', 'zsh', 'ksh',
        'asp', 'aspx', 'asa', 'asax', 'ashx', 'asmx',
        'jsp', 'jspx', 'jspf',
        'cfm', 'cfc',
        'shtml', 'shtm', 'stm'
    );

    return in_array($ext, $blocked, true);
}

/**
 * Validate a user supplied upload filename.
 *
 * @param string $filename
 * @return bool
 */
function MG_validateUploadFilename180($filename)
{
    if ($filename === '' || $filename === null) {
        return false;
    }

    if (strpos($filename, "\0") !== false) {
        return false;
    }

    return !MG_isUnsafeUploadFilename180($filename);
}
