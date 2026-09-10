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

    $template = COM_newTemplate(MG_getTemplatePath($aid), 'emails');
    $template->set_file(array(
        'email_html' => 'moderation-html.thtml',
    ));

    // Plaintext templates use {LB}; remove physical line feeds first so the
    // resulting layout is consistent with Geeklog's core email templates.
    $template->preprocess_fn = 'CTL_removeLineFeeds';
    $template->set_file(array(
        'email_plaintext' => 'moderation-plaintext.thtml',
    ));

    $moderationUrl = $_MG_CONF['site_url']
        . '/admin.php?album_id=' . intval($aid) . '&mode=moderate';

    $template->set_var(array(
        'LB'                => LB,
        'email_divider'     => isset($LANG31['email_divider']) ? $LANG31['email_divider'] : '----------------------------------------',
        'email_divider_html'=> isset($LANG31['email_divider_html']) ? $LANG31['email_divider_html'] : '<hr>',
        'lang_new_upload'   => $LANG_MG01['new_upload_body'],
        'lang_details'      => $LANG_MG01['details'],
        'lang_album_title'  => 'Album',
        'lang_uploaded_by'  => $LANG_MG01['uploaded_by'],
        'lang_review'       => 'Review submission',
        'username'          => $username,
        'album_title'       => strip_tags($albumTitle),
        'moderation_url'    => $moderationUrl,
        'site_name'         => $_CONF['site_name'],
        'site_slogan'       => $_CONF['site_slogan'],
        'site_url'          => $_CONF['site_url'],
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

    // Passing true tells COM_mail that $message contains HTML and plaintext
    // variants, matching the pattern used by current Geeklog plugins.
    return COM_mail($email, $subject, $message, '', true);
}
