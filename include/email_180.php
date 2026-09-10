<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - Geeklog                                           |
// +--------------------------------------------------------------------------+
// | email_180.php                                                            |
// |                                                                          |
// | Native Geeklog email helpers for MediaGallery 1.8.0                      |
// +--------------------------------------------------------------------------+

if (stripos($_SERVER['PHP_SELF'], basename(__FILE__)) !== false) {
    die('This file can not be used on its own.');
}

/**
 * Build HTML and plaintext moderation notification bodies.
 *
 * @param int    $aid       Album ID
 * @param string $albumTitle
 * @param string $username
 * @return array            HTML body, plaintext body
 */
function MG_buildModerationEmail180($aid, $albumTitle, $username)
{
    global $_CONF, $_MG_CONF, $LANG_MG01, $LANG31;

    $template = COM_newTemplate(CTL_plugin_templatePath('mediagallery', 'emails'));
    $template->set_file(array(
        'email_html' => 'moderation-html.thtml',
    ));

    $template->preprocess_fn = 'CTL_removeLineFeeds';
    $template->set_file(array(
        'email_plaintext' => 'moderation-plaintext.thtml',
    ));

    $moderationUrl = $_MG_CONF['site_url']
        . '/admin.php?album_id=' . intval($aid) . '&mode=moderate';

    $albumTitlePlain = trim(strip_tags($albumTitle));
    $usernamePlain = trim(strip_tags($username));

    $template->set_var(array(
        'LB'                       => LB,
        'email_divider'            => isset($LANG31['email_divider']) ? $LANG31['email_divider'] : '----------------------------------------',
        'email_divider_html'       => isset($LANG31['email_divider_html']) ? $LANG31['email_divider_html'] : '<hr>',
        'lang_new_upload'          => $LANG_MG01['new_upload_body'],
        'lang_details'             => $LANG_MG01['details'],
        'lang_album_title'         => 'Album',
        'lang_uploaded_by'         => $LANG_MG01['uploaded_by'],
        'lang_review'              => 'Review submission',
        'username_html'            => htmlspecialchars($usernamePlain, ENT_QUOTES, COM_getCharset()),
        'username_plaintext'       => $usernamePlain,
        'album_title_html'         => htmlspecialchars($albumTitlePlain, ENT_QUOTES, COM_getCharset()),
        'album_title_plaintext'    => $albumTitlePlain,
        'moderation_url'           => $moderationUrl,
        'moderation_url_html'      => htmlspecialchars($moderationUrl, ENT_QUOTES, COM_getCharset()),
        'site_name'                => htmlspecialchars($_CONF['site_name'], ENT_QUOTES, COM_getCharset()),
        'site_name_plaintext'      => strip_tags($_CONF['site_name']),
        'site_slogan'              => htmlspecialchars($_CONF['site_slogan'], ENT_QUOTES, COM_getCharset()),
        'site_slogan_plaintext'    => strip_tags($_CONF['site_slogan']),
        'site_url'                 => htmlspecialchars($_CONF['site_url'], ENT_QUOTES, COM_getCharset()),
        'site_url_plaintext'       => $_CONF['site_url'],
    ));

    return array(
        $template->parse('output', 'email_html'),
        $template->parse('output', 'email_plaintext'),
    );
}

/**
 * Send a moderation notification using Geeklog's configured mail backend.
 *
 * @param string $email
 * @param string $subject
 * @param array  $message HTML/plaintext bodies from MG_buildModerationEmail180
 * @return bool
 */
function MG_sendModerationEmail180($email, $subject, $message)
{
    if (empty($email)) {
        return false;
    }

    return COM_mail($email, $subject, $message, '', true);
}

/**
 * Native replacement for the legacy PHPMailer-based moderator notification.
 *
 * This function is intentionally separate during the 1.8 transition. Once all
 * upload entry points call it, the bundled PHPMailer path can be removed.
 *
 * @param int $aid Album ID
 * @return bool
 */
function MG_notifyModerators180($aid)
{
    global $_USER, $_MG_CONF, $_CONF, $_TABLES, $LANG_MG01;

    $sql = "SELECT moderate, album_title, mod_group_id "
         . "FROM {$_TABLES['mg_albums']} WHERE album_id = " . intval($aid);
    $result = DB_query($sql);

    if (DB_numRows($result) !== 1) {
        return false;
    }

    $album = DB_fetchArray($result);
    if (intval($album['moderate']) !== 1 || SEC_hasRights('mediagallery.admin')) {
        return true;
    }

    $uid = isset($_USER['uid']) ? intval($_USER['uid']) : 1;
    $username = ($uid < 2) ? 'Anonymous' : COM_getDisplayName($uid);
    $subject = $LANG_MG01['new_upload_subject'] . $_CONF['site_name'];
    $message = MG_buildModerationEmail180($aid, $album['album_title'], $username);

    // Preserve the existing notification throttle behavior at plugin level.
    $last = COM_checkSpeedlimit('mgnotify');
    if ($last > 0) {
        return true;
    }

    $groups = MG_getGroupList(intval($album['mod_group_id']));
    if (empty($groups)) {
        COM_errorLog('MG Upload: Error - Did not find any moderator groups to email');
        return false;
    }

    $groupList = implode(',', array_map('intval', $groups));
    $sql = "SELECT DISTINCT u.uid, u.username, u.fullname, u.email "
         . "FROM {$_TABLES['group_assignments']} ga "
         . "INNER JOIN {$_TABLES['users']} u ON u.uid = ga.ug_uid "
         . "WHERE u.uid > 1 "
         . "AND ga.ug_main_grp_id IN ({$groupList})";

    $result = DB_query($sql);
    $sent = 0;

    while ($row = DB_fetchArray($result)) {
        if (empty($row['email'])) {
            continue;
        }

        if ($_MG_CONF['verbose']) {
            COM_errorLog('MG Upload: Sending notification email to: '
                . $row['email'] . ' - ' . $row['username']);
        }

        if (MG_sendModerationEmail180($row['email'], $subject, $message)) {
            $sent++;
        } else {
            COM_errorLog('MG Upload: Unable to send moderation email to ' . $row['email']);
        }
    }

    if ($sent > 0) {
        COM_updateSpeedlimit('mgnotify');
        return true;
    }

    COM_errorLog('MG Upload: Error - Did not find any moderators to email');
    return false;
}
