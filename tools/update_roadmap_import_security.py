from pathlib import Path

p = Path('ROADMAP.md')
text = p.read_text()

old = "- [x] CLI import filename protection.\n"
new = "- [x] CLI import filename protection.\n- [x] Harden ZIP extraction against path traversal, unsafe temporary paths, symlinks, excessive entry counts and declared uncompressed payloads above 1 GiB before extraction.\n- [x] Harden recursive CLI imports by refusing symbolic links and preserving the intended subdirectory-to-subalbum mapping.\n"
if text.count(old) != 1:
    raise SystemExit('CLI roadmap marker not found exactly once')
text = text.replace(old, new)

old = "- [ ] Review ZIP extraction security and any remaining legacy archive/import code.\n"
new = "- [x] Review and harden ZIP extraction plus remaining recursive CLI import paths.\n"
if text.count(old) != 1:
    raise SystemExit('ZIP review roadmap marker not found exactly once')
text = text.replace(old, new)

old = "- [ ] FTP valid source, forged outside path, unsafe extension and escaping symlink.\n"
new = "- [ ] FTP valid source, forged outside path, unsafe extension and escaping symlink.\n- [ ] ZIP import: normal archive, `../` traversal member, symbolic-link member, excessive entry count and >1 GiB declared uncompressed payload.\n- [ ] CLI recursive import: normal nested directories, symlink source rejection and correct subdirectory-to-subalbum placement.\n"
if text.count(old) != 1:
    raise SystemExit('security regression roadmap marker not found exactly once')
text = text.replace(old, new)

p.write_text(text)
