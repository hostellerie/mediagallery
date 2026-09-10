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

/**
 * Return true when an IP address is public and routable.
 *
 * @param string $ip
 * @return bool
 */
function MG_isPublicIp180($ip)
{
    return filter_var(
        $ip,
        FILTER_VALIDATE_IP,
        FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE
    ) !== false;
}

/**
 * Validate an HTTP(S) URL before MediaGallery fetches it server-side.
 *
 * This blocks credentials in URLs and hosts resolving to loopback, private or
 * reserved address space. Streaming/embed URLs that are only stored and never
 * fetched are handled separately by their existing media-type validation.
 *
 * @param string $url
 * @return bool
 */
function MG_validateRemoteFetchUrl180($url)
{
    $url = trim((string) $url);
    if ($url === '' || filter_var($url, FILTER_VALIDATE_URL) === false) {
        return false;
    }

    $parts = parse_url($url);
    if (!is_array($parts) || empty($parts['scheme']) || empty($parts['host'])) {
        return false;
    }

    $scheme = strtolower($parts['scheme']);
    if ($scheme !== 'http' && $scheme !== 'https') {
        return false;
    }

    if (isset($parts['user']) || isset($parts['pass'])) {
        return false;
    }

    $host = trim($parts['host'], '[]');
    $hostLower = strtolower($host);
    if ($hostLower === 'localhost' || substr($hostLower, -10) === '.localhost') {
        return false;
    }

    if (filter_var($host, FILTER_VALIDATE_IP) !== false) {
        return MG_isPublicIp180($host);
    }

    $ips = array();
    if (function_exists('dns_get_record')) {
        $records = @dns_get_record($host, DNS_A | DNS_AAAA);
        if (is_array($records)) {
            foreach ($records as $record) {
                if (!empty($record['ip'])) {
                    $ips[] = $record['ip'];
                }
                if (!empty($record['ipv6'])) {
                    $ips[] = $record['ipv6'];
                }
            }
        }
    }

    if (empty($ips)) {
        $resolved = @gethostbyname($host);
        if ($resolved !== $host) {
            $ips[] = $resolved;
        }
    }

    if (empty($ips)) {
        return false;
    }

    foreach ($ips as $ip) {
        if (!MG_isPublicIp180($ip)) {
            return false;
        }
    }

    return true;
}
