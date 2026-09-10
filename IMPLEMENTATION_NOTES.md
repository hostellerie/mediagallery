# MediaGallery 1.8.0 Implementation Notes

This file tracks implementation decisions made while modernizing the plugin.

## Implemented

- Created a transitional 1.8.0 bootstrap in `functions.inc`.
- Preserved the complete 1.7.3 implementation as `functions_legacy.inc` while modernization is introduced incrementally.
- Added `include/config_180.php` for 1.8.0 runtime configuration and Configuration API migration.
- Added explicit upgrade support from known 1.7.x identifiers, including 1.7.0 and 1.7.3.
- Bumped the development plugin version to 1.8.0 through the runtime/bootstrap and autoinstall metadata.
- Added optional multisite storage based on `$_CONF['path_images']` + `$_CONF['images_url']`.
- Preserved the historical `mediagallery/mediaobjects/` location when `images_url` is absent.
- Isolated multisite temporary and FTP/upload staging paths under site-specific `$_CONF['path_data']` when available.
- Added controlled creation of multisite `tmp` and `uploads` work directories, with logging on failure.
- Added idempotent Configuration API migration for live settings that were previously hard-coded.
- Guarded Configuration API migration so it does not run before the plugin configuration group exists during installation.
- Ensured fresh 1.8.0 installs receive the same additional settings as upgraded installations.
- Added English fallback labels for the new configuration entries until translation files are updated.
- Modernized the main album template with a semantic H1, navigation landmarks and a more accessible search control.
- Modernized album/media cell markup without changing existing template variables.
- Added a canonical URL to individual media pages so display/sort/pagination variants do not create duplicate indexable media URLs.
- Added self-canonical album URLs, keeping page 2+ canonicalized to their own pagination URL while dropping sort variants.
- Added album HTML page titles and page-number suffixes on paginated album pages.
- Corrected the sort form so it preserves the visible one-based page number instead of the internal zero-based index.
- Added the native Geeklog `album_list` service requested by issue #10 and documented it in `docs/SERVICES.md`.
- Added HTML and plaintext moderation email templates under `templates/emails/`.
- Added a native `COM_mail()` moderation notification path and switched all current upload entry points to it.
- Fixed the old moderation email album-title mismatch (`album_title` was selected but `title` was read).
- Preserved the historical 10-minute moderation notification throttle using Geeklog's speed-limit API.
- Added a compatibility fallback for email template lookup when `CTL_plugin_templatePath()` is unavailable on an older Geeklog runtime.
- Added Geeklog CSRF protection to the active browser upload form using `SEC_createToken()`, `CSRF_TOKEN` and `SEC_checkToken()`.
- Removed the unreachable SWFUpload form-rendering block that lived after an unconditional return in `MG_uploadForm()`.
- Hardened the legacy asynchronous upload endpoint so user identity comes from the authenticated Geeklog session rather than a POSTed `uid`.
- Added a manual GitHub Actions workflow that builds an installable `dist/mediagallery-VERSION.zip`, creates a SHA-256 checksum and publishes both as a 14-day workflow artifact.
- Added a `dist/README.md` and ignores for generated distribution binaries.
- Expanded syntax linting to PHP 5.6, 7.4, 8.1 and 8.3.
- Fixed the invalid Geeklog 2.2.2 user/user_attributes query in `admin/purgealbums.php` that caused a parse error.
- Verified one complete CI syntax-lint run successfully on PHP 5.6, 7.4, 8.1 and 8.3 after that fix.

## Configuration loading

- Keep only internal/runtime constants hard-coded long term.
- Load administrator preferences from the Geeklog Configuration API.
- Compute derived paths after configuration is loaded.
- Do not restore the historical `config.php` file.
- The current `functions_legacy.inc` split is transitional and should be folded back into a clean final `functions.inc` before release candidate if practical.

## Media storage

- Standard installations keep `public_html/mediagallery/mediaobjects/`.
- If both `$_CONF['path_images']` and `$_CONF['images_url']` are defined, use the site-specific image root and append `/mediagallery/`.
- Never derive site identity from `HTTP_HOST` inside MediaGallery.
- Never move existing media automatically during upgrade.

## Temporary storage

When site-specific media storage is active and `$_CONF['path_data']` is available, 1.8.0 derives:

```text
{path_data}/mediagallery/tmp/
{path_data}/mediagallery/uploads/
```

The runtime attempts to create these private working directories when missing and logs an error if creation fails. Upload code must still report a useful writable-directory error when the server permissions prevent their use.

## Configuration API migration

The current migration adds these previously hard-coded settings when missing:

- `link_to_member_album`
- `rating_speedlimit`
- `mediamanage_items`
- `use_default_resolution`
- `use_large_stars`
- `use_upload_time`
- `ffmpeg_command_args`
- `disable_lightbox`
- `update_parent_lastupdated`
- `allow_user_edit`
- `enable_remote_images`
- `click_image_and_go_next`
- `hide_jumpbox_on_mediaview`
- `enable_loop_pagination`
- `random_img_ratio`

Existing administrator values are never overwritten. False/zero values are preserved because migration checks key existence rather than truthiness.

## Interoperability service

MediaGallery 1.8.0 now implements Geeklog's native service convention:

```php
PLG_invokeService(
    'mediagallery',
    'album_list',
    array(
        'uid'       => $uid,
        'root'      => 'member',
        'recursive' => true,
        'visible'   => true,
    ),
    $output,
    $svc_msg
);
```

The service applies MediaGallery access rules and avoids requiring consumers such as Documents to query `mg_*` tables directly. `member_album_root = 0` is treated as a valid root value.

## Email modernization

The active upload entry points now use `MG_notifyModerators180()`, which builds HTML/plaintext templates and delegates transport to Geeklog `COM_mail()`.

The old `MG_notifyModerators()` implementation remains in `include/lib-upload.php` as legacy/dead code. It still references the historical bundled PHPMailer path, but that `include/lib/phpmailer/` directory is no longer present in the current repository tree. The legacy function should therefore be removed after functional verification of the new mail path rather than preserving or restoring the obsolete PHPMailer dependency.

## Distribution archives

Use the GitHub Actions workflow **Build MediaGallery installable archive** when a package is needed for online testing.

The workflow is manual (`workflow_dispatch`) and creates:

```text
dist/mediagallery-VERSION.zip
dist/mediagallery-VERSION.zip.sha256
```

The archive contains a single top-level `mediagallery/` directory. Generated binaries are uploaded as workflow artifacts for 14 days and are not committed to Git.

## Template / SEO work

Completed:

- semantic `<h1>` for album title;
- navigation landmarks and accessible album search field;
- semantic wrappers for album/media thumbnail cells;
- canonical URL for individual media pages;
- self-canonical album pagination with sort parameters excluded;
- album HTML titles with page-number suffixes for page 2+;
- confirmed default/none frame templates already use the media title as image `alt` text.

Still to do:

- audit escaping of `{media_tag}` before it is placed in `alt`/`title` attributes;
- move remaining inline presentation CSS into plugin stylesheets where safe;
- audit obsolete audio-player/SWF/QuickTime/WMP/MooTools/legacy JavaScript includes before removal;
- avoid adding invented meta descriptions where MediaGallery does not have suitable source content.

## Security audit items

Completed in the current pass:

- the active browser upload form now carries and validates Geeklog's standard CSRF token;
- the legacy asynchronous upload endpoint no longer trusts a POSTed user ID;
- `MG_getFile()` remains the final album permission check for uploaded media.

Current finding:

- if getID3 cannot identify a file, the legacy upload pipeline can fall back to the client-supplied MIME type or file extension;
- the generic-file path stores the original extension under the public media tree on traditional installations;
- current executable-extension rewriting only covers a small legacy list (`php`, `pl`, `cgi`, `py`, `sh`, `rb`) and must be broadened before 1.8.0 release.

Still review:

- whether the legacy async upload endpoint can be removed completely after confirming there are no active callers;
- upload MIME/extension validation and executable extension handling;
- remote-media URL validation;
- permission checks around album mutations;
- temporary file names and cleanup;
- HTML attribute escaping in frame templates;
- obsolete executable media formats and legacy playback paths.

## Required tests before merging

- Upgrade an actual 1.7.0 installation.
- Upgrade a 1.7.3 installation.
- New 1.8.0 installation.
- Geeklog 2.1.1 and 2.2.2 Configuration API behavior.
- Multisite with separate table prefixes/databases and separate `path_images` / `images_url` / `path_data`.
- Standard site with no `images_url` to confirm legacy media paths remain unchanged.
- Verify `tmp` and `uploads` creation/writability handling.
- Verify all added configuration controls display and save correctly.
- Test moderator email in both HTML-capable and plaintext clients and with Geeklog SMTP/sendmail configuration.
- Test `album_list` for owner, anonymous/non-owner, administrator and hidden albums.
- Test media canonical output and album H1 with multiple skins.
- Test album page titles/canonical URLs on page 1, page 2+ and sort variants.
- Test browser upload success and rejection of invalid/missing CSRF tokens.
- Test the hardened legacy async upload endpoint with an authenticated session and a mismatched POSTed `uid`.
- Test executable and ambiguous uploads (`php`, `phtml`, `phar`, double extensions, unknown MIME) after upload hardening is implemented.
- Keep PHP 5.6, PHP 7.4, PHP 8.1 and PHP 8.3 syntax lint green.
