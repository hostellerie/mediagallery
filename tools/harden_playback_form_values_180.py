from pathlib import Path

p = Path('include/mediamanage.php')
text = p.read_text(encoding='utf-8')
replacements = {
    "'bgcolor'                    => $playback_options['bgcolor'],": "'bgcolor'                    => MG_escapeHTML($playback_options['bgcolor']),",
    "'flashvars'      => isset($playback_options['flashvars']) ? $playback_options['flashvars'] : '',": "'flashvars'      => isset($playback_options['flashvars']) ? MG_escapeHTML($playback_options['flashvars']) : '',",
    "'bgcolor'        => $playback_options['bgcolor'],": "'bgcolor'        => MG_escapeHTML($playback_options['bgcolor']),",
    "'bgcolor'             => $playback_options['bgcolor'],": "'bgcolor'             => MG_escapeHTML($playback_options['bgcolor']),",
}
for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one playback marker, found %d: %s' % (count, old))
    text = text.replace(old, new, 1)
p.write_text(text, encoding='utf-8')

p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
marker = '- [x] Remove translated delete-confirmation text from JavaScript string literals and escape it for HTML data attributes.\n'
addition = marker + '- [x] Escape persisted legacy playback text/color values when rendering maintained edit-form attributes.\n'
if text.count(marker) != 1:
    raise SystemExit('Roadmap marker mismatch')
p.write_text(text.replace(marker, addition, 1), encoding='utf-8')
