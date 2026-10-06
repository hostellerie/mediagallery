<?php

// +--------------------------------------------------------------------------+
// | Media Gallery Plugin - reusable media picker                             |
// +--------------------------------------------------------------------------+

if (stripos($_SERVER['PHP_SELF'], basename(__FILE__)) !== false) {
    die('This file can not be used on its own.');
}

/**
 * Build a MediaGallery autotag from validated values.
 *
 * @param string $type    Autotag name
 * @param string $id      Media or album id
 * @param array  $options Optional width, height, align, link and caption
 * @return string
 */
function MG_buildAutotag($type, $id, $options = array())
{
    $allowedTypes = array('media', 'img', 'mlink', 'album', 'slideshow');
    if (!in_array($type, $allowedTypes, true)) {
        $type = 'media';
    }

    $id = preg_replace('/[^A-Za-z0-9_-]/', '', (string) $id);
    if ($id === '') {
        return '';
    }

    $tag = '[' . $type . ':' . $id;

    foreach (array('width', 'height') as $dimension) {
        if (isset($options[$dimension])) {
            $value = intval($options[$dimension]);
            if ($value > 0 && $value <= 4096) {
                $tag .= ' ' . $dimension . ':' . $value;
            }
        }
    }

    if (isset($options['align']) && in_array($options['align'], array('left', 'right', 'center', 'none'), true)) {
        $tag .= ' align:' . $options['align'];
    }

    if (isset($options['link'])) {
        $link = intval($options['link']);
        if ($link >= 0 && $link <= 2) {
            $tag .= ' link:' . $link;
        }
    }

    if (!empty($options['caption'])) {
        $caption = trim(str_replace(array('[', ']'), '', strip_tags($options['caption'])));
        if ($caption !== '') {
            $tag .= ' ' . $caption;
        }
    }

    return $tag . ']';
}

/**
 * Return a button that opens the reusable MediaGallery picker.
 *
 * The consuming plugin owns the target editor. MediaGallery only returns an
 * autotag through a same-origin postMessage event.
 *
 * @param array $options target, tag, label and class
 * @return string
 */
function MG_getMediaPickerButton($options = array())
{
    global $_CONF, $_MG_CONF, $_SCRIPTS;

    if (!isset($_MG_CONF['site_url']) || !is_object($_SCRIPTS)) {
        return '';
    }

    $target = isset($options['target']) ? (string) $options['target'] : '#form-forum-text';
    if (!preg_match('/^(#[A-Za-z][A-Za-z0-9_-]*|[A-Za-z]+\\[name="[A-Za-z][A-Za-z0-9_-]*"\\])$/', $target)) {
        return '';
    }

    $tag = isset($options['tag']) ? (string) $options['tag'] : 'media';
    if (!in_array($tag, array('media', 'img', 'mlink'), true)) {
        $tag = 'media';
    }

    if (isset($options['label']) && trim($options['label']) !== '') {
        $label = trim($options['label']);
    } elseif (isset($_CONF['language']) && strpos($_CONF['language'], 'french') === 0) {
        $label = 'Ajouter un média';
    } else {
        $label = 'Add media';
    }

    $class = isset($options['class']) ? trim($options['class']) : 'mg-picker-button';
    $class = preg_replace('/[^A-Za-z0-9 _-]/', '', $class);

    $_SCRIPTS->setJavaScriptFile(
        'mediagallery-media-picker',
        MG_assetUrl180('/mediagallery/js/media-picker.js')
    );
    $_SCRIPTS->setCSSFile(
        'mediagallery-media-picker',
        MG_assetUrl180('/mediagallery/media-picker.css')
    );

    $url = $_MG_CONF['site_url'] . '/picker.php?target=' . rawurlencode($target)
         . '&tag=' . rawurlencode($tag);
    $charset = empty($_CONF['default_charset']) ? 'UTF-8' : $_CONF['default_charset'];

    return '<button type="button" class="' . htmlspecialchars($class, ENT_QUOTES, $charset)
         . '" data-mg-picker-url="' . htmlspecialchars($url, ENT_QUOTES, $charset) . '">'
         . htmlspecialchars($label, ENT_QUOTES, $charset) . '</button>';
}
