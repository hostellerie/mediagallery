from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8', errors='surrogateescape')
    count = text.count(old)
    if count != 1:
        raise SystemExit('%s: expected 1 occurrence, found %d' % (label, count))
    p.write_text(text.replace(old, new, 1), encoding='utf-8', errors='surrogateescape')


old_route = """        case 'video/mpeg' :
        case 'video/x-mpeg' :
        case 'video/x-mpeq2a' :
            if ($_MG_CONF['use_wmp_mpeg'] == 1) {
                $function = 'MG_displayASF';
                break;
            }
        case 'video/x-motion-jpeg' :
        case 'video/quicktime' :
        case 'video/x-qtc' :
        case 'video/x-m4v' :
            $function = 'MG_displayMOV';
            if ($media['media_mime_ext'] == 'mp4' &&
                isset($_MG_CONF['play_mp4_flv']) && $_MG_CONF['play_mp4_flv'] == true) {
                $function = 'MG_displayFLV';
            }
            break;
"""
new_route = """        case 'video/mpeg' :
        case 'video/x-mpeg' :
        case 'video/x-mpeq2a' :
        case 'video/x-motion-jpeg' :
        case 'video/quicktime' :
        case 'video/x-qtc' :
        case 'video/x-m4v' :
            // MediaGallery 1.8 uses the HTML5 video renderer for MPEG/MOV/MP4.
            $function = 'MG_displayMOV';
            break;
"""
replace_once('include/lib-media.php', old_route, new_route, 'video routing')

old_mp4 = """
/*
 * By default, Media Gallery plays MP4 video files as QuickTime
 * videos, using the QuickTime player.
 *
 * If you prefer to use the Flash Video Player for MP4 files,
 * set this value to true.
 *
 */
$_MG_CONF['play_mp4_flv'] = false;
//$_MG_CONF['play_mp4_flv'] = true;
"""
old_mpeg = """
/*
 * By default, Media Gallery will play MPEG videos with Apple's QuickTime
 * player. If you wish to use Microsoft's Windows Media Player instead,
 * set this variable to 1.
 */

$_MG_CONF['use_wmp_mpeg'] = 0;
"""
replace_once('functions_legacy.inc', old_mp4, '\n', 'play_mp4_flv runtime option')
replace_once('functions_legacy.inc', old_mpeg, '\n', 'use_wmp_mpeg runtime option')

print('Video routing cleanup applied.')
