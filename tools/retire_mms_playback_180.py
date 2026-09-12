from pathlib import Path

p = Path('include/lib-media.php')
text = p.read_text()

old = """        case 1: // download
            $u_pic = $_MG_CONF['site_url'] . '/download.php?mid=' . $I['media_id'];
            $raw_link_url = $u_pic;
            list($u_image, $p_image, $media_size_orig) = Media::getThumbInfo($I);
            break;
        case 2: // inline
"""
new = """        case 1: // download
        case 3: // legacy MMS mode now falls back to a normal download
            $u_pic = $_MG_CONF['site_url'] . '/download.php?mid=' . $I['media_id'];
            $raw_link_url = $u_pic;
            list($u_image, $p_image, $media_size_orig) = Media::getThumbInfo($I);
            break;
        case 2: // inline
"""
if text.count(old) != 1:
    raise SystemExit('ASF download block not found exactly once')
text = text.replace(old, new)

old = """        case 3: // use mms links
            $mms_path = preg_replace(\"/http/i\", 'mms', $_MG_CONF['mediaobjects_url']);
            $u_pic = $mms_path . '/orig/'.  $I['media_filename'][0] . '/' . $I['media_filename'] . '.' . $I['media_mime_ext'];
            $raw_link_url = $u_pic;
            list($u_image, $p_image, $media_size_orig) = Media::getThumbInfo($I);
            break;
"""
if text.count(old) != 1:
    raise SystemExit('ASF MMS block not found exactly once')
text = text.replace(old, '')

old = """        case 1: // download
            $u_pic = $_MG_CONF['site_url'] . '/download.php?mid=' . $I['media_id'];
            list($u_image, $p_image, $media_size_orig) = Media::getThumbInfo($I);
            break;
        case 2: // inline
"""
new = """        case 1: // download
        case 3: // legacy MMS mode now falls back to a normal download
            $u_pic = $_MG_CONF['site_url'] . '/download.php?mid=' . $I['media_id'];
            list($u_image, $p_image, $media_size_orig) = Media::getThumbInfo($I);
            break;
        case 2: // inline
"""
if text.count(old) != 1:
    raise SystemExit('MP3 download block not found exactly once')
text = text.replace(old, new)

old = """        case 3: // use mms links
            $mms_path = preg_replace(\"/http/i\", 'mms', $_MG_CONF['mediaobjects_url']);
            $u_pic = $mms_path . '/orig/'.  $I['media_filename'][0] . '/' . $I['media_filename'] . '.' . $I['media_mime_ext'];
            list($u_image, $p_image, $media_size_orig) = Media::getThumbInfo($I);
            break;
"""
if text.count(old) != 1:
    raise SystemExit('MP3 MMS block not found exactly once')
text = text.replace(old, '')

p.write_text(text)

r = Path('ROADMAP.md')
roadmap = r.read_text()
roadmap = roadmap.replace(
    '- [ ] Decide which remaining ASF/MOV/MP3 playback controls are still meaningful.\n- [ ] Decide whether legacy per-media playback options should be normalized or ignored.\n- [ ] Decide whether the old `mms` mode should be retired.\n',
    '- [x] Keep only playback dimensions/mode behavior that still affects HTML5 rendering; legacy ActiveX/QuickTime-specific flags remain compatibility data and are ignored by maintained templates.\n- [x] Preserve legacy per-media playback rows for upgrade/custom-skin compatibility, but do not reintroduce obsolete player behavior in maintained HTML5 templates.\n- [x] Retire generated `mms:` playback links; legacy playback mode 3 now falls back to the normal MediaGallery download path.\n'
)
r.write_text(roadmap)
