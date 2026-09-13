from pathlib import Path
import re


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')

# Global album attributes: associate visible row labels with generated controls by
# wrapping each value control in an implicit label; give each "update" checkbox
# a contextual accessible name. This avoids requiring producer-side ids.
p = Path('templates/global_album_attr.thtml')
text = p.read_text(encoding='utf-8')
pat = re.compile(r'<td class="mg_alignright">(\{lang_[^}]+\})</td>\n    <td([^>]*)>(.*?)</td>\n    <td><input type="checkbox" name="([^"]+_active)" value="1"\{xhtml\}></td>', re.S)

def repl(m):
    label, attrs, control, active = m.groups()
    return ('<td class="mg_alignright">%s</td>\n'
            '    <td%s><label>%s %s</label></td>\n'
            '    <td><input type="checkbox" name="%s" value="1" aria-label="{lang_update}: %s"{xhtml}></td>'
            % (label, attrs, label, control, active, label))
text, count = pat.subn(repl, text)
if count < 20:
    raise SystemExit('global attr row association count too low: %d' % count)
# Formats: explicit labels for all checkboxes.
formats = [('jpg','1'),('png','2'),('tif','4'),('gif','8'),('bmp','16'),('tga','32'),('psd','64'),('mp3','128'),('ogg','256'),('asf','512'),('swf','1024'),('mov','2048'),('mp4','4096'),('mpg','8192'),('flv','131072'),('rflv','262144'),('emb','524288'),('zip','16384'),('other','32768')]
for name, value in formats:
    # tolerate whitespace / nbsp between control and old span
    pattern = re.compile(r'<input type="checkbox" name="format_%s" value="%s"\{xhtml\}>\s*(?:&nbsp;)*\s*<span>\{lang_%s\}</span>' % (name, value, name))
    replacement = '<input type="checkbox" id="mg-global-format-%s" name="format_%s" value="%s"{xhtml}> <label for="mg-global-format-%s">{lang_%s}</label>' % (name, name, value, name, name)
    text, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise SystemExit('format label marker mismatch: %s' % name)
text = text.replace('<td><input type="checkbox" name="formats_active" value="1"{xhtml}></td>', '<td><input type="checkbox" name="formats_active" value="1" aria-label="{lang_update}: {lang_allowed_formats}"{xhtml}></td>', 1)
text = text.replace('<th>{lang_attribute}</th>', '<th scope="col">{lang_attribute}</th>', 1)
text = text.replace('<th align="left">{lang_value}</th>', '<th scope="col" align="left">{lang_value}</th>', 1)
text = text.replace('<th>{lang_update}</th>', '<th scope="col">{lang_update}</th>', 1)
write(p, text)

# Global permissions: implicit labels for simple generated/direct controls and
# contextual names for update checkboxes. Keep Geeklog's permission editor intact.
p = Path('templates/global_album_perm.thtml')
text = p.read_text(encoding='utf-8')
rows = [
    ('{lang_group}', '{group_select}', 'group_active'),
    ('{lang_member_upload}', '<input type="checkbox" name="member_upload" value="1"{xhtml}>', 'upload_active'),
    ('{lang_moderate_album}', '<input type="checkbox" name="moderation" value="1"{xhtml}>', 'moderate_active'),
    ('{lang_mod_group}', '{mod_group_select}', 'mod_group_active'),
    ('{lang_email_mods_on_submission}', '<input type="checkbox" name="email_mod" value="1"{xhtml}>', 'email_mod_active'),
]
for label, control, active in rows:
    old = '    <td class="mg_alignright">%s</td>\n    <td>%s</td>\n    <td><input type="checkbox" name="%s" value="1"{xhtml}></td>' % (label, control, active)
    new = '    <td class="mg_alignright">%s</td>\n    <td><label>%s %s</label></td>\n    <td><input type="checkbox" name="%s" value="1" aria-label="{lang_update}: %s"{xhtml}></td>' % (label, label, control, active, label)
    if old not in text:
        raise SystemExit('global perm marker missing: %s' % active)
    text = text.replace(old, new, 1)
text = text.replace('<td><input type="checkbox" name="perm_active" value="1"{xhtml}></td>', '<td><input type="checkbox" name="perm_active" value="1" aria-label="{lang_update}: {lang_permissions}"{xhtml}></td>', 1)
text = text.replace('<th>{lang_attribute}</th>', '<th scope="col">{lang_attribute}</th>', 1)
text = text.replace('<th align="left">{lang_value}</th>', '<th scope="col" align="left">{lang_value}</th>', 1)
text = text.replace('<th>{lang_update}</th>', '<th scope="col">{lang_update}</th>', 1)
write(p, text)

# Member creation and purge lists: generated checkbox fragments become implicitly
# labelled without changing their producer-side names/values.
for path in ['templates/createmembers.thtml', 'templates/purgealbums.thtml']:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    text = text.replace('<td>{select}</td>', '<td><label>{select} <span>{lang_select}</span></label></td>', 1)
    text = text.replace('onclick="javascript:doCheckAll_', 'onclick="doCheckAll_')
    text = text.replace('onclick="javascript:doUnCheckAll_', 'onclick="doUnCheckAll_')
    text = re.sub(r'<th( style="[^"]*")?>(\{lang_[^}]+\})</th>', r'<th scope="col"\1>\2</th>', text)
    write(p, text)

# Session list: direct row checkbox and column semantics.
p = Path('templates/sessions.thtml')
text = p.read_text(encoding='utf-8')
text = text.replace('<input type="checkbox" name="sel[]" value="{session_id}"{xhtml}>', '<input type="checkbox" name="sel[]" value="{session_id}" aria-label="{lang_select}: {session_description}"{xhtml}>', 1)
text = text.replace('onclick="javascript:doCheckAll_sessions()"', 'onclick="doCheckAll_sessions()"', 1)
text = text.replace('onclick="javascript:doUnCheckAll_sessions()"', 'onclick="doUnCheckAll_sessions()"', 1)
text = re.sub(r'<th( style="[^"]*")?>(\{lang_[^}]+\})</th>', r'<th scope="col"\1>\2</th>', text)
write(p, text)

# Watermark upload: explicit associations for the two direct controls.
p = Path('templates/wm_upload.thtml')
text = p.read_text(encoding='utf-8')
text = text.replace('<dt>{lang_file}</dt>\n      <dd><input type="file" dir="ltr" name="newmedia[]"{xhtml}></dd>', '<dt><label for="mg-watermark-file">{lang_file}</label></dt>\n      <dd><input type="file" id="mg-watermark-file" dir="ltr" name="newmedia[]"{xhtml}></dd>', 1)
text = text.replace('<dt>{lang_description}</dt>\n      <dd><textarea name="description[]"', '<dt><label for="mg-watermark-description">{lang_description}</label></dt>\n      <dd><textarea id="mg-watermark-description" name="description[]"', 1)
write(p, text)

# Roadmap: close the broad keyboard/form-label audit after the remaining global
# and maintenance controls are covered. Live browser/AT testing remains part of RC regression.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
text = text.replace('- [ ] Review keyboard accessibility and form labeling across remaining admin/public templates.\n', '- [x] Review keyboard accessibility and form labeling across remaining admin/public templates.\n', 1)
text = text.replace('  - [ ] Resolve remaining global album-management and maintenance-form labeling.\n', '  - [x] Label global album-management update controls plus member/purge/session/watermark maintenance forms.\n', 1)
write(p, text)
