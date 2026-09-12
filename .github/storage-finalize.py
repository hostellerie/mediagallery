from pathlib import Path
import re


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'{label}: anchor not found')
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# 1. Upgrade semantics + local-media guard
# ---------------------------------------------------------------------------
p = Path('autoinstall.php')
text = p.read_text(encoding='utf-8')

for function, version in (
    ('MG_upgrade_1612', '1.6.12'),
    ('MG_upgrade_170', '1.7.0'),
    ('MG_upgrade_180', '1.8.0'),
):
    pattern = re.compile(
        r'(\$result = ' + re.escape(function) + r'\(\);\n\s*if \(\$result != 0\) \{\n)'
        r'\s*return \$result;\n'
        r'(\s*\})'
    )
    replacement = (
        r"\1                COM_errorLog('Media Gallery upgrade failed while migrating to "
        + version
        + r".', 1);\n                return 72;\n\2"
    )
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f'{function}: stage return anchor not found')

text = replace_once(
    text,
    """        return 0;
    }

    DB_query("UPDATE {$_TABLES['plugins']} """,
    """        return 72;
    }

    DB_query("UPDATE {$_TABLES['plugins']} """,
    'final-version failure',
)

text = replace_once(
    text,
    """        COM_errorLog('Media Gallery upgrade: unable to update plugin version metadata.', 1);
        return 0;
    }

    return 1;
""",
    """        COM_errorLog('Media Gallery upgrade: unable to update plugin version metadata.', 1);
        return 72;
    }

    return true;
""",
    'top-level success',
)

text = replace_once(
    text,
    "    $mediaRows = isset($_TABLES['mg_media']) ? DB_count($_TABLES['mg_media']) : 0;\n",
    """    $localMediaRows = 0;
    if (isset($_TABLES['mg_media'])) {
        $result = DB_query("SELECT COUNT(*) AS local_count FROM {$_TABLES['mg_media']} WHERE remote_media = 0");
        if ($result !== false) {
            $row = DB_fetchArray($result);
            $localMediaRows = isset($row['local_count']) ? (int) $row['local_count'] : 0;
        }
    }
""",
    'local media count',
)
text = replace_once(
    text,
    'if ($mediaRows > 0 && !$legacyHasUserMedia && !$targetHasUserMedia) {',
    'if ($localMediaRows > 0 && !$legacyHasUserMedia && !$targetHasUserMedia) {',
    'local media guard',
)
p.write_text(text, encoding='utf-8')


# ---------------------------------------------------------------------------
# 2. Remove temporary upload-response tracing
# ---------------------------------------------------------------------------
p = Path('public_html/admin.php')
text = p.read_text(encoding='utf-8')
text = replace_once(
    text,
    """        case 'upload' :
            require_once $include . 'newmedia.php';
            $uploadResult = MG_saveUserUpload($album_id);
            if (!empty($_MG_CONF['verbose'])) {
                COM_errorLog(
                    'MG DEBUG admin after MG_saveUserUpload: type=' . gettype($uploadResult)
                    . ' length=' . strlen((string) $uploadResult)
                );
            }
            $display .= $uploadResult;
            break;
""",
    """        case 'upload' :
            require_once $include . 'newmedia.php';
            $display .= MG_saveUserUpload($album_id);
            break;
""",
    'admin upload debug',
)
text = replace_once(
    text,
    """    if (isset($action) && $action === 'upload' && !empty($_MG_CONF['verbose'])) {
        COM_errorLog('MG DEBUG admin before MG_createHTMLDocument: length=' . strlen((string) $display));
    }
    $display = MG_createHTMLDocument($display);
    if (isset($action) && $action === 'upload' && !empty($_MG_CONF['verbose'])) {
        COM_errorLog(
            'MG DEBUG admin after MG_createHTMLDocument: type=' . gettype($display)
            . ' length=' . strlen((string) $display)
        );
        COM_errorLog('MG DEBUG admin before COM_output');
    }
    COM_output($display);
""",
    """    $display = MG_createHTMLDocument($display);
    COM_output($display);
""",
    'admin output debug',
)
p.write_text(text, encoding='utf-8')

p = Path('include/newmedia.php')
text = p.read_text(encoding='utf-8')

# Stray trace injected into legacy MG_saveUpload().
text = replace_once(
    text,
    """    if (!empty($_MG_CONF['verbose'])) {
        COM_errorLog(
            'MG DEBUG saveUserUpload after files: success=' . intval($successfull_upload)
            . ' status_length=' . strlen((string) $statusMsg)
        );
    }

    if ($successfull_upload) {
        if (!empty($_MG_CONF['verbose'])) {
            COM_errorLog('MG DEBUG saveUserUpload before moderator notification');
        }
        MG_notifyModerators180($album_id);
        if (!empty($_MG_CONF['verbose'])) {
            COM_errorLog('MG DEBUG saveUserUpload after moderator notification');
        }
    }
""",
    """    if ($successfull_upload) {
        MG_notifyModerators180($album_id);
    }
""",
    'legacy MG_saveUpload debug',
)

text = replace_once(
    text,
    """    if (!empty($_MG_CONF['verbose'])) {
        COM_errorLog('MG DEBUG saveUserUpload: CSRF accepted album_id=' . intval($album_id));
    }

""",
    '',
    'saveUserUpload CSRF debug',
)
text = replace_once(
    text,
    """    if (!empty($_MG_CONF['verbose'])) {
        COM_errorLog('MG DEBUG saveUserUpload before MG_SortMedia');
    }
    MG_SortMedia($album_id);
    if (!empty($_MG_CONF['verbose'])) {
        COM_errorLog('MG DEBUG saveUserUpload after MG_SortMedia');
    }
""",
    """    MG_SortMedia($album_id);
""",
    'saveUserUpload sort debug',
)
text = replace_once(
    text,
    """    if (!empty($_MG_CONF['verbose'])) {
        COM_errorLog('MG DEBUG saveUserUpload parsed template length=' . strlen((string) $T->get_var('output')));
    }
""",
    '',
    'saveUserUpload template debug',
)
text = replace_once(
    text,
    """    if (!empty($_MG_CONF['verbose'])) {
        COM_errorLog('MG DEBUG saveUserUpload return length=' . strlen((string) $retval));
    }

""",
    '',
    'saveUserUpload return debug',
)
p.write_text(text, encoding='utf-8')


# ---------------------------------------------------------------------------
# 3. Documentation: persistent media storage and mandatory 1.7 preflight
# ---------------------------------------------------------------------------
p = Path('README')
text = p.read_text(encoding='utf-8')
start = text.index('Multisite media storage\n-----------------------')
end = text.index('Configuration\n-------------', start)
section = """Persistent media storage
------------------------
MediaGallery 1.8.0 stores public media below Geeklog's image root instead of inside the replaceable plugin directory.

Standard single-site installations use:

    $_CONF['path_images'] . 'mediagallery/'

with the public URL:

    {site_url}/images/mediagallery

When `$_CONF['images_url']` is explicitly defined, MediaGallery uses it as the public image URL root. This is the recommended multisite setup, for example:

    $_CONF['path_images'] = $_CONF['path'] . 'public_html/images/example/';
    $_CONF['images_url']  = $_CONF['site_url'] . '/images/example';

which produces:

    .../public_html/images/example/mediagallery/
    https://example.com/images/example/mediagallery

The historical `public_html/mediagallery/mediaobjects/` directory remains a migration source only. It is no longer the 1.8 runtime storage location. This is necessary because Geeklog's native plugin ZIP uploader replaces the complete `public_html/mediagallery/` directory during an update.

### Mandatory preflight when upgrading 1.7.x with Geeklog's ZIP uploader

Geeklog removes the old plugin public directory before it loads the new plugin upgrade code. Therefore a 1.7.x site that still stores media below `public_html/mediagallery/mediaobjects/` must migrate those files before uploading the 1.8.0 ZIP.

Extract the 1.8.0 archive on the server and run:

    php tools/migrate-media-storage.php /path/to/geeklog

The tool copies files to the persistent images location, verifies every source file by relative path and size, and deliberately leaves the legacy source untouched. Only after it reports `Migration OK` should the 1.8.0 ZIP be uploaded through Geeklog.

Fresh 1.8.0 installations seed the same persistent storage automatically. Once a site uses `images/.../mediagallery/`, subsequent plugin ZIP updates cannot remove user media.

"""
text = text[:start] + section + text[end:]
text = text.replace(
    'The 1.8.0 upgrade must preserve existing configuration values, add only missing Configuration API settings, avoid duplicate settings and never move media automatically.',
    'The 1.8.0 upgrade preserves existing configuration values, adds only missing Configuration API settings, and migrates legacy media by copy-and-verify semantics without deleting the source.'
)
p.write_text(text, encoding='utf-8')

p = Path('IMPLEMENTATION_NOTES.md')
text = p.read_text(encoding='utf-8')
old = """- site-specific media storage when both `$_CONF['path_images']` and `$_CONF['images_url']` are defined;
- historical `public_html/mediagallery/mediaobjects/` storage preserved when `images_url` is absent;
- site-specific `tmp` and FTP/upload staging under `$_CONF['path_data']/mediagallery/` when multisite storage is active;
- controlled creation of private work directories with error logging;
- no automatic relocation of existing media during upgrade;
"""
new = """- persistent public media storage under `$_CONF['path_images']/mediagallery/` for all 1.8.0 installations;
- `$_CONF['images_url']` respected when explicitly supplied, with `{site_url}/images` used only for the standard single-site image path;
- shared-code multisite isolation through each site's own `path_images` / `images_url` pair;
- `include/storage_180.php` copy-and-verify migration with no source deletion and conflict refusal;
- CLI preflight tool `tools/migrate-media-storage.php` for 1.7.x sites before Geeklog's public-plugin-directory replacement;
- site-specific `tmp` and FTP/upload staging under `$_CONF['path_data']/mediagallery/`;
- controlled creation of public/private work directories with error logging;
- upgrade failures propagate as Geeklog errors instead of marking 1.8.0 installed after a failed migration;
"""
text = replace_once(text, old, new, 'implementation storage bullets')
text = text.replace(
    '- standard single-site install with legacy media paths;',
    '- standard single-site install with persistent `images/mediagallery/` storage;\n- 1.7.3 preflight migration to `images/mediagallery/`, then ZIP upgrade, with source and destination verification;\n- verify a legacy ZIP upgrade without preflight is refused when local media rows exist but no user-media files are available;'
)
p.write_text(text, encoding='utf-8')

p = Path('TESTING-1.8.md')
text = p.read_text(encoding='utf-8')
start = text.index('## Multisite\n')
end_marker = 'Record PHP warnings/notices together with the Geeklog version, PHP version, action performed and relevant MediaGallery settings.'
end = text.index(end_marker, start)
section = """## Persistent media storage

On a standard single-site installation:

- confirm `path_mediaobjects` resolves below `public_html/images/mediagallery/`;
- upload an image and confirm `orig`, `disp` and `tn` files are created there;
- re-upload the same MediaGallery 1.8.0 plugin ZIP and confirm the existing image remains intact;
- confirm placeholder/type assets such as `missing.png` and `generic.png` are present in persistent storage.

On a shared-code installation with site-specific `path_images`, `images_url` and `path_data`:

- confirm each site resolves its own `mediagallery` media path and URL;
- confirm `tmp` and FTP/upload staging directories are site-specific;
- confirm uploads on one site do not appear in another site's storage.

## Upgrade from 1.7.x

On disposable copies only:

- back up the database and `public_html/mediagallery/mediaobjects/`;
- extract the 1.8.0 package without installing it;
- run `php tools/migrate-media-storage.php /path/to/geeklog`;
- confirm the tool reports all source files verified in the persistent destination and leaves the source untouched;
- only then upload the 1.8.0 ZIP through Geeklog;
- test both MediaGallery 1.7.0 and 1.7.3 sources;
- confirm existing albums/media remain accessible from the new images storage;
- confirm existing administrator settings are preserved;
- confirm re-running the migration is idempotent;
- create a conflicting destination file with a different size and confirm migration fails without overwriting it;
- confirm a site containing only remote-media records does not falsely require local media files;
- confirm obsolete Flash/FlowPlayer configuration rows, if still present in the database, do not affect the 1.8 runtime.

"""
text = text[:start] + section + text[end:]
p.write_text(text, encoding='utf-8')


# ---------------------------------------------------------------------------
# 4. Distribution validation
# ---------------------------------------------------------------------------
p = Path('.github/workflows/build-dist.yml')
text = p.read_text(encoding='utf-8')
anchor = "          unzip -Z1 \"dist/${ARCHIVE}\" | grep -qx 'mediagallery/BUILD_INFO.txt'\n"
insert = (
    anchor
    + "          unzip -Z1 \"dist/${ARCHIVE}\" | grep -qx 'mediagallery/include/storage_180.php'\n"
    + "          unzip -Z1 \"dist/${ARCHIVE}\" | grep -qx 'mediagallery/tools/migrate-media-storage.php'\n"
)
text = replace_once(text, anchor, insert, 'dist validation')
p.write_text(text, encoding='utf-8')

print('MediaGallery 1.8 storage finalization patch prepared successfully.')
