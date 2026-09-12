from pathlib import Path

path = Path('include/classMedia.php')
text = path.read_text(encoding='utf-8', errors='surrogateescape')

old = """        if ($info['media_tn_attached'] == 1) {\n            $pimage = self::getFilePath('tn', $info['media_filename'], 'jpg', 1);\n            $image  = self::getFileUrl ('tn', $info['media_filename'], 'jpg', 1);\n        } else {\n            $fname = self::getDefaultThumbnail($info, $tn_size);\n            $pimage = $_MG_CONF['path_mediaobjects']      . $fname;\n            $image  = $_MG_CONF['mediaobjects_url'] . '/' . $fname;\n        }\n        $size = @getimagesize($pimage);\n        if ($size == false) {\n            $fname = 'missing.png';\n            $pimage = $_MG_CONF['path_mediaobjects']      . $fname;\n            $image  = $_MG_CONF['mediaobjects_url'] . '/' . $fname;\n            $size = @getimagesize($pimage);\n        }\n\n        return array($image, $pimage, $size);\n"""

new = """        if ($info['media_tn_attached'] == 1) {\n            $pimage = self::getFilePath('tn', $info['media_filename'], 'jpg', 1);\n            $image  = self::getFileUrl ('tn', $info['media_filename'], 'jpg', 1);\n        } else {\n            $fname = self::getDefaultThumbnail($info, $tn_size);\n\n            /*\n             * Generated thumbnails belong to the site's media storage.\n             * Built-in placeholder/type icons belong to the plugin itself and\n             * must stay available independently of multisite media storage.\n             */\n            if (strpos($fname, '/') === false) {\n                $pimage = $_MG_CONF['path_html'] . 'mediaobjects/' . $fname;\n                $image  = $_MG_CONF['site_url'] . '/mediaobjects/' . $fname;\n            } else {\n                $pimage = $_MG_CONF['path_mediaobjects'] . $fname;\n                $image  = $_MG_CONF['mediaobjects_url'] . '/' . $fname;\n            }\n        }\n\n        $size = @getimagesize($pimage);\n        if ($size === false) {\n            $fname = 'missing.png';\n            $pimage = $_MG_CONF['path_html'] . 'mediaobjects/' . $fname;\n            $image  = $_MG_CONF['site_url'] . '/mediaobjects/' . $fname;\n            $size = @getimagesize($pimage);\n        }\n\n        return array($image, $pimage, $size);\n"""

count = text.count(old)
if count != 1:
    raise SystemExit('Expected exactly one getThumbInfo block, found %d' % count)

text = text.replace(old, new)
path.write_text(text, encoding='utf-8', errors='surrogateescape')
