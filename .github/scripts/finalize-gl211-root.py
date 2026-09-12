from pathlib import Path


def replace_exact(path, old, new, count=None):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    found = text.count(old)
    expected = count if count is not None else 1
    if found != expected:
        raise SystemExit(f'{path}: expected {expected} occurrence(s), found {found}: {old!r}')
    p.write_text(text.replace(old, new), encoding='utf-8')

# Official Geeklog minimum version.
replace_exact('autoinstall.php', "'pi_gl_version'   => '2.0.0'", "'pi_gl_version'   => '2.1.1'")
replace_exact("autoinstall.php", "COM_versionCompare(VERSION, '2.0.0', '<')", "COM_versionCompare(VERSION, '2.1.1', '<')")

# Root is a virtual album container: it may contain albums, never media.
replace_exact(
    'public_html/index.php',
    "    if ($root_album->member_uploads || $root_album->access == 3) {\n"
    "        $options .= '<option value=\"upload\">' . $LANG_MG01['add_media'] . '</option>' . LB;\n"
    "    }\n",
    ''
)

# Distribution target and fixed archive filename.
replace_exact('.github/workflows/build-dist.yml', 'ARCHIVE="mediagallery_1.8.0_2.0.0.zip"', 'ARCHIVE="mediagallery_1.8.0_2.1.1.zip"')
replace_exact('.github/workflows/build-dist.yml', 'Geeklog target: 2.0.0+', 'Geeklog target: 2.1.1+')
replace_exact('.github/workflows/build-dist.yml', 'Build mediagallery_1.8.0_2.0.0.zip for ${SOURCE_SHA} [skip ci]', 'Build mediagallery_1.8.0_2.1.1.zip for ${SOURCE_SHA} [skip ci]')

replace_exact('dist/README.md', 'dist/mediagallery_1.8.0_2.0.0.zip', 'dist/mediagallery_1.8.0_2.1.1.zip')
replace_exact('TESTING-1.8.md', 'dist/mediagallery_1.8.0_2.0.0.zip', 'dist/mediagallery_1.8.0_2.1.1.zip')
replace_exact('IMPLEMENTATION_NOTES.md', 'dist/mediagallery_1.8.0_2.0.0.zip', 'dist/mediagallery_1.8.0_2.1.1.zip', count=2)

# Strengthen the compatibility statement already present in implementation notes.
replace_exact(
    'IMPLEMENTATION_NOTES.md',
    '- Target Geeklog 2.1.1 through 2.2.2 where practical.',
    '- Require Geeklog 2.1.1 or newer; Geeklog 2.0.x is not a supported target for MediaGallery 1.8.0.'
)

# Update the build trigger description if it still refers to the old target/archive.
trigger = Path('.github/dist-trigger')
if trigger.exists():
    text = trigger.read_text(encoding='utf-8')
    text = text.replace('mediagallery_1.8.0_2.0.0.zip', 'mediagallery_1.8.0_2.1.1.zip')
    text = text.replace('Geeklog 2.0.0+', 'Geeklog 2.1.1+')
    trigger.write_text(text, encoding='utf-8')

# Verify the intended behavioral and metadata changes.
index = Path('public_html/index.php').read_text(encoding='utf-8')
if "<option value=\"upload\">' . $LANG_MG01['add_media']" in index:
    raise SystemExit('Root admin box still exposes Add Media')
if "<option value=\"create\">' . $LANG_MG01['create_album']" not in index:
    raise SystemExit('Root admin box no longer exposes Create Album')

auto = Path('autoinstall.php').read_text(encoding='utf-8')
if "'pi_gl_version'   => '2.1.1'" not in auto or "COM_versionCompare(VERSION, '2.1.1', '<')" not in auto:
    raise SystemExit('Geeklog 2.1.1 minimum was not applied consistently')

workflow = Path('.github/workflows/build-dist.yml').read_text(encoding='utf-8')
if 'mediagallery_1.8.0_2.0.0.zip' in workflow or 'Geeklog target: 2.0.0+' in workflow:
    raise SystemExit('Distribution workflow still contains old Geeklog 2.0.0 target')

print('MediaGallery Geeklog 2.1.1 minimum and root-album UI policy applied.')
