from pathlib import Path


def replace_once(path, old, new, label, encoding='utf-8'):
    p = Path(path)
    text = p.read_text(encoding=encoding)
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one %s marker in %s, found %d' % (label, path, count))
    p.write_text(text.replace(old, new, 1), encoding=encoding)

# Simplify the two still-effective playback panels to dimensions only.
Path('templates/edit_asf_options.thtml').write_text('''<fieldset class="mg-playback-dimensions">\n  <legend>{lang_playback_options}</legend>\n  <input type="hidden" name="playback_geometry" value="1"{xhtml}>\n  <dl class="form_block">\n    <dt><label for="mg-playback-width">{lang_width}</label></dt>\n    <dd><input type="number" id="mg-playback-width" name="width" value="{width}" min="1" step="1" inputmode="numeric"{xhtml}> <span class="description">{lang_width_help}</span></dd>\n    <dt><label for="mg-playback-height">{lang_height}</label></dt>\n    <dd><input type="number" id="mg-playback-height" name="height" value="{height}" min="1" step="1" inputmode="numeric"{xhtml}> <span class="description">{lang_height_help}</span></dd>\n  </dl>\n</fieldset>\n''', encoding='utf-8')
Path('templates/edit_mov_options.thtml').write_text('''<fieldset class="mg-playback-dimensions">\n  <legend>{lang_playback_options}</legend>\n  <input type="hidden" name="playback_geometry" value="1"{xhtml}>\n  <dl class="form_block">\n    <dt><label for="mg-playback-width">{lang_width}</label></dt>\n    <dd><input type="number" id="mg-playback-width" name="width" value="{width}" min="1" step="1" inputmode="numeric"{xhtml}> <span class="description">{lang_width_help}</span></dd>\n    <dt><label for="mg-playback-height">{lang_height}</label></dt>\n    <dd><input type="number" id="mg-playback-height" name="height" value="{height}" min="1" step="1" inputmode="numeric"{xhtml}> <span class="description">{lang_height_help}</span></dd>\n  </dl>\n</fieldset>\n''', encoding='utf-8')

# Large PHP file: preserve PHP 5.6 syntax and only remove dead UI/save paths.
p = Path('include/mediamanage.php')
text = p.read_text(encoding='utf-8')
text = text.replace("        'mp3_options' => 'edit_mp3_options.thtml',\n        'swf_options' => 'edit_swf_options.thtml',\n", '', 1)
text = text.replace("        'flv_options' => 'edit_flv_options.thtml',\n", '', 1)

# Remove MP3 panel construction entirely.
start = text.find("    if ($row['mime_type'] == 'audio/mpeg') {")
end = text.find("    if ($row['mime_type'] == 'application/x-shockwave-flash' ||", start)
if start < 0 or end < 0:
    raise SystemExit('MP3 playback UI block markers not found')
text = text[:start] + text[end:]

# Remove SWF/FLV panel construction entirely.
start = text.find("    if ($row['mime_type'] == 'application/x-shockwave-flash' ||")
end = text.find("    if ($row['media_mime_ext'] == 'mov' ||", start)
if start < 0 or end < 0:
    raise SystemExit('SWF/FLV playback UI block markers not found')
text = text[:start] + text[end:]

# Reduce ASF setup to width/height values only, while still loading existing per-media overrides.
asf_start = text.find("    if ( $row['mime_type'] == 'video/x-ms-asf' ||")
asf_end = text.find("    if ($row['media_mime_ext'] == 'mov' ||", asf_start)
if asf_start < 0 or asf_end < 0:
    raise SystemExit('ASF/MOV markers not found')
asf_block = text[asf_start:asf_end]
old_asf = asf_block
# Keep condition and DB override loop, discard legacy option/select setup.
cond_end = asf_block.find("        // pull defaults, then override...")
loop_start = asf_block.find("        for ($i=0; $i < $poNumRows; $i++) {")
loop_end = asf_block.find("        }\n\n", loop_start) + len("        }\n\n")
if cond_end < 0 or loop_start < 0 or loop_end < len("        }\n\n"):
    raise SystemExit('ASF inner markers not found')
condition = asf_block[:cond_end]
loop = asf_block[loop_start:loop_end]
new_asf = condition + "        $playback_options['height'] = $_MG_CONF['asf_height'];\n        $playback_options['width']  = $_MG_CONF['asf_width'];\n\n" + loop + "        $T->set_var(array(\n            'height' => $playback_options['height'],\n            'width'  => $playback_options['width'],\n        ));\n        $T->parse('playback_options', 'asf_options');\n    }\n\n"
text = text[:asf_start] + new_asf + text[asf_end:]

# Reduce MOV setup to width/height only.
mov_start = text.find("    if ($row['media_mime_ext'] == 'mov' ||")
# The next stable marker is remoteurl assignment.
mov_end = text.find("    $remoteurl = $row['remote_url'];", mov_start)
if mov_start < 0 or mov_end < 0:
    raise SystemExit('MOV block markers not found')
mov_block = text[mov_start:mov_end]
cond_end = mov_block.find("        // pull defaults, then override...")
loop_start = mov_block.find("        for ($i=0; $i < $poNumRows; $i++) {")
loop_end = mov_block.find("        }\n\n", loop_start) + len("        }\n\n")
if cond_end < 0 or loop_start < 0 or loop_end < len("        }\n\n"):
    raise SystemExit('MOV inner markers not found')
condition = mov_block[:cond_end]
loop = mov_block[loop_start:loop_end]
new_mov = condition + "        $playback_options['height'] = $_MG_CONF['mov_height'];\n        $playback_options['width']  = $_MG_CONF['mov_width'];\n\n" + loop + "        $T->set_var(array(\n            'height' => $playback_options['height'],\n            'width'  => $playback_options['width'],\n        ));\n        $T->parse('playback_options', 'mov_options');\n    }\n\n"
text = text[:mov_start] + new_mov + text[mov_end:]

# Replace legacy playback save branches with dimensions-only persistence.
save_start = text.find("    // process playback options if any...")
save_end = text.find("    if ($attachtn == 1 && $thumbnail != '') {", save_start)
if save_start < 0 or save_end < 0:
    raise SystemExit('playback save block markers not found')
new_save = '''    // HTML5 playback no longer uses the old ActiveX/Flash/QuickTime option set.\n    // Preserve only per-media video dimensions; historical rows stay untouched for upgrades.\n    if (isset($_POST['playback_geometry'])) {\n        $width  = isset($_POST['width'])  ? COM_applyFilter($_POST['width'], true)  : 0;\n        $height = isset($_POST['height']) ? COM_applyFilter($_POST['height'], true) : 0;\n        if ($width > 0) {\n            MG_savePBOption($media_id, 'width', $width, true);\n        }\n        if ($height > 0) {\n            MG_savePBOption($media_id, 'height', $height, true);\n        }\n    }\n\n'''
text = text[:save_start] + new_save + text[save_end:]
p.write_text(text, encoding='utf-8')

# Stop passing dead legacy values to maintained HTML5 templates.
p = Path('include/lib-media.php')
text = p.read_text(encoding='latin-1')
# ASF: remove unused vars from template set_var, retain width/height/movie.
for key in ['autostart', 'enablecontextmenu', 'stretchtofit', 'showstatusbar', 'uimode', 'playcount', 'bgcolor', 'autostart0', 'enablecontextmenu0', 'stretchtofit0', 'showstatusbar0']:
    import re
    text = re.sub(r"\n\s*'" + re.escape(key) + r"'\s*=>[^\n]+,", '', text, count=1)
# Remove the now-dead uimode switch block once.
start = text.find("            switch ($playback_options['uimode']) {")
if start >= 0:
    end = text.find("            $u_image = $V->finish", start)
    text = text[:start] + text[end:]
# MOV: controller no longer adds fake plugin chrome height; old vars are not consumed by HTML5 template.
text = text.replace("                'height'           => $playback_options['height'] + ($playback_options['controller'] ? 20 : 0),", "                'height'           => $playback_options['height'],", 1)
for key in ['autoref', 'autoplay', 'controller', 'kioskmode', 'loop', 'scale', 'bgcolor']:
    import re
    text = re.sub(r"\n\s*'" + re.escape(key) + r"'\s*=>[^\n]+,", '', text, count=1)
# MP3: stop loading per-media playback rows that no longer affect <audio>; keep fixed responsive geometry.
mp3_start = text.find('function MG_displayMP3')
mp3_switch = text.find('    switch ($playback_type)', mp3_start)
if mp3_start < 0 or mp3_switch < 0:
    raise SystemExit('MP3 display markers not found')
prefix = text[mp3_start:mp3_switch]
# Remove default playback-options block and DB override from MP3 only.
def_start = prefix.find('    // set the default playback options...')
prefs_start = prefix.find('    $_MG_USERPREFS = MG_getUserPrefs();')
if def_start >= 0 and prefs_start > def_start:
    prefix = prefix[:def_start] + prefix[prefs_start:]
text = text[:mp3_start] + prefix + text[mp3_switch:]
# Remove dead MP3 vars from set_var.
for key in ['autostart', 'enablecontextmenu', 'stretchtofit', 'showstatusbar', 'loop', 'playcount', 'uimode']:
    import re
    pattern = r"\n\s*'" + re.escape(key) + r"'\s*=>[^\n]+,"
    # Search only after MG_displayMP3 in resulting text.
    before = text[:mp3_start]
    after = text[mp3_start:]
    after = re.sub(pattern, '', after, count=1)
    text = before + after
p.write_text(text, encoding='latin-1')

# Roadmap: mark legacy playback-control review complete and accessibility dependency resolved.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
text = text.replace('  - [ ] Resolve remaining generated-control/global-management labeling together with obsolete playback-control cleanup.\n', '  - [x] Remove obsolete per-media playback controls instead of labeling settings that no longer affect HTML5 rendering; retain only video width/height controls.\n  - [ ] Resolve remaining generated-control/global-management labeling.\n', 1)
needle = '- [ ] Review remaining legacy playback-related controls and remove settings without a useful HTML5 equivalent.\n'
if needle in text:
    text = text.replace(needle, '- [x] Review remaining legacy playback-related controls and remove settings without a useful HTML5 equivalent.\n', 1)
p.write_text(text, encoding='utf-8')
