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
 * Validate a local import source against an allowed root directory.
 *
 * Both paths are resolved with realpath(). The source must exist and resolve
 * either to the root itself or to a descendant of that root. This prevents a
 * forged FTP/batch form field from importing arbitrary local server files.
 *
 * @param string $source
 * @param string $allowedRoot
 * @param bool   $allowDirectory
 * @return bool
 */
function MG_validateLocalImportPath180($source, $allowedRoot, $allowDirectory = true)
{
    if ($source === '' || $allowedRoot === '') {
        return false;
    }

    if (strpos($source, "\0") !== false || strpos($allowedRoot, "\0") !== false) {
        return false;
    }

    $root = realpath($allowedRoot);
    $path = realpath($source);

    if ($root === false || $path === false) {
        return false;
    }

    if (!$allowDirectory && !is_file($path)) {
        return false;
    }

    $root = rtrim(str_replace('\\', '/', $root), '/') . '/';
    $pathNormalized = str_replace('\\', '/', $path);

    if ($pathNormalized === rtrim($root, '/')) {
        return $allowDirectory;
    }

    return strpos($pathNormalized . (is_dir($path) ? '/' : ''), $root) === 0;
}

/**
 * Validate an FTP/batch import filename and its resolved path.
 *
 * @param string $source
 * @param string $allowedRoot
 * @param bool   $allowDirectory
 * @return bool
 */
function MG_validateLocalImportSource180($source, $allowedRoot, $allowDirectory = true)
{
    if (!MG_validateLocalImportPath180($source, $allowedRoot, $allowDirectory)) {
        return false;
    }

    if (is_dir($source)) {
        return $allowDirectory;
    }

    return MG_validateUploadFilename180(basename($source));
}

/**
 * Validate every pending source in an FTP batch session before processing.
 *
 * A recursive import may discover new files/directories on a later request.
 * Running this preflight before each MG_continueSession() call ensures that
 * symlinks or forged session data can never escape the configured ftp_path.
 *
 * @param string $sessionId
 * @param string $reason Receives a short failure reason.
 * @return bool
 */
function MG_validateFtpBatchSession180($sessionId, &$reason)
{
    global $_TABLES, $_USER, $_MG_CONF;

    $reason = '';
    $sessionId = (string) $sessionId;

    if ($sessionId === '') {
        $reason = 'missing_session';
        return false;
    }

    $escapedId = DB_escapeString($sessionId);
    $result = DB_query(
        "SELECT session_uid, session_action FROM {$_TABLES['mg_sessions']} "
        . "WHERE session_id='" . $escapedId . "'"
    );

    if (DB_numRows($result) !== 1) {
        $reason = 'invalid_session';
        return false;
    }

    $session = DB_fetchArray($result);
    if ((int) $session['session_uid'] !== (int) $_USER['uid']
        && !SEC_hasRights('mediagallery.admin')) {
        $reason = 'access_denied';
        return false;
    }

    if ($session['session_action'] !== 'ftpimport') {
        return true;
    }

    if (empty($_MG_CONF['ftp_path']) || realpath($_MG_CONF['ftp_path']) === false) {
        $reason = 'invalid_ftp_root';
        return false;
    }

    $items = DB_query(
        "SELECT data, mid FROM {$_TABLES['mg_session_items']} "
        . "WHERE session_id='" . $escapedId . "' AND status=0"
    );

    while ($item = DB_fetchArray($items)) {
        $source = $item['data'];
        $isDirectory = ((int) $item['mid'] === 1);

        if (!MG_validateLocalImportSource180(
            $source,
            $_MG_CONF['ftp_path'],
            $isDirectory
        )) {
            COM_errorLog(
                'MediaGallery 1.8: rejected FTP batch source outside ftp_path or with unsafe filename: '
                . $source
            );
            $reason = 'invalid_source';
            return false;
        }
    }

    return true;
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
