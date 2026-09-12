# MediaGallery 1.8.0 Roadmap

MediaGallery 1.8.0 is a modernization and hardening release focused on safe upgrades, persistent media storage, Geeklog 2.1.1+ compatibility, multisite isolation, upload security, removal of obsolete playback technologies, template/SEO/accessibility improvements, and interoperability with other Geeklog plugins.

The working branch is `modernize-1.8.0`. The supported Geeklog baseline is 2.1.1; Geeklog 2.0.x is not a target for 1.8.0.

This roadmap reflects the current implementation state. Completed items are checked; remaining work is concentrated around release-candidate validation and final cleanup.

## 1. Compatibility and release baseline

- [x] Require Geeklog 2.1.1 or newer.
- [x] Validate current runtime behavior on Geeklog 2.1.1 and 2.2.2.
- [x] Keep syntax compatible with PHP 5.6, 7.4, 8.1 and 8.3 while this compatibility policy remains in force.
- [x] Keep PHP lint CI green on the supported syntax range.
- [x] Avoid Geeklog core modifications.
- [x] Do not reintroduce the historical MediaGallery `config.php`.
- [x] Preserve existing database content and administrator configuration during upgrade.
- [ ] Complete the PHP 8.2/8.3 runtime warning/deprecation audit before RC.
- [ ] Run the final regression matrix on Geeklog 2.1.1 and 2.2.2.

## 2. Persistent media storage and multisite

Media files are persistent user data and no longer live inside the replaceable plugin public directory.

MediaGallery 1.8.0 uses:

```php
$_MG_CONF['path_mediaobjects'] = rtrim($_CONF['path_images'], '/\\') . '/mediagallery/';
```

The historical `public_html/mediagallery/mediaobjects/` location is a legacy migration source only.

- [x] Centralize storage path/URL resolution.
- [x] Store all 1.8 public media under `path_images/mediagallery/`.
- [x] Keep shared-code multisite media isolated through each site's `path_images` / `images_url` pair.
- [x] Keep temporary/upload staging isolated under each site's `path_data/mediagallery/`.
- [x] Avoid `HTTP_HOST`-derived site identity.
- [x] Create required public/private storage directories with explicit error handling.
- [x] Implement copy-and-verify legacy-media migration in `include/storage_180.php`.
- [x] Never delete the legacy source automatically during migration.
- [x] Refuse conflicting destination files instead of silently overwriting them.
- [x] Provide `tools/migrate-media-storage.php` for safe 1.7.x pre-migration.
- [x] Protect subsequent ZIP upgrades because persistent media now live outside `public_html/mediagallery/`.
- [x] Propagate migration failures so a failed upgrade cannot be marked as installed successfully.
- [x] Confirm that adding media and then re-uploading the plugin ZIP preserves existing media on tested 2.1.1/2.2.2 installations.
- [ ] Validate the pre-migration path on disposable 1.7.0 and 1.7.3 copies.

### Legacy ZIP upgrade rule

Geeklog's plugin uploader replaces the old public plugin directory before loading the new plugin's upgrade code. A 1.7.x installation still storing media in `public_html/mediagallery/mediaobjects/` must therefore run the provided pre-migration tool before uploading the 1.8 ZIP.

## 3. Configuration API cleanup

- [x] Add `include/config_180.php` for runtime configuration and 1.8 migration.
- [x] Add missing Configuration API entries without resetting existing values.
- [x] Correctly distinguish missing settings from valid `0` / `false` settings.
- [x] Keep calculated/internal values out of administrator-editable configuration.
- [x] Remove fresh-install FlowPlayer configuration.
- [x] Remove fresh-install Flash Media configuration controls.
- [x] Keep obsolete legacy rows harmless on upgraded sites where deletion has not yet been proven safe.
- [ ] Verify whether obsolete 1.7.x Flash/FlowPlayer `conf_values` rows can be safely removed on both Geeklog 2.1.1 and 2.2.2.
- [ ] Review remaining legacy playback-related controls and remove settings with no useful HTML5 equivalent.

## 4. Upload, import and remote-media security

- [x] Geeklog CSRF protection on browser upload, Remote Media and FTP import forms.
- [x] Correct browser slot association for captions, descriptions, keywords, category, attached thumbnail and DNC.
- [x] Correct DNC handling and preservation of originals when requested.
- [x] Real format conversion when DNC is disabled instead of only changing MIME/extension metadata.
- [x] Unsafe executable/server-side filename rejection.
- [x] Defense-in-depth filename validation inside `MG_getFile()`.
- [x] FTP source confinement with `realpath()`.
- [x] Revalidation of hidden FTP paths and recursive batch sources.
- [x] Batch continuation/cancellation ownership validation.
- [x] CLI import filename protection.
- [x] Remote Media restricted to public HTTP(S), with private/reserved/localhost rejection, redirect blocking and bounded downloads.
- [x] Root Album (`album_id=0`) upload prevention.
- [x] Prefer content-derived MIME (`getID3`, then `fileinfo`) and validate MIME/extension coherence for explicitly handled formats while leaving unknown extensions generic.
- [ ] Live-test MIME mismatch rejection and generic-file compatibility on Geeklog 2.1.1 and 2.2.2.
- [x] Clean deterministic upload-failure and special-image `wip` temporary files.
- [x] Add conservative stale-temp cleanup for genuinely interrupted/killed requests: private MediaGallery tmp only, 48-hour age threshold, no symlink traversal, and at most one scan per hour.
- [ ] Live-test stale-temp cleanup with old and recent files/directories on Geeklog 2.1.1 and 2.2.2.
- [x] Add CSRF protection to global album permission/attribute mutations and watermark manage/upload/delete mutations while preserving their existing access rules.
- [x] Harden album/static sort mutations with Geeklog CSRF tokens and revalidate static-sort album write access server-side.
- [x] Harden resize/rebuild confirmations, media manager save/delete/move/batch actions and direct rotation with Geeklog CSRF tokens; direct rotation now uses POST and revalidates album write access plus album/media membership.
- [x] Revalidate media edit/reset mutations server-side and correct reset handlers to read their posted album id.
- [x] Bind posted media IDs to the authorized album before manager edits, batch delete/move/rotate/watermark, cover selection and normal media editing.
- [ ] Continue audit of remaining caption/moderation/delete-session mutations before RC.
- [x] Remove the orphaned legacy asynchronous upload endpoint and its dedicated `MG_saveUpload()` handler after confirming the active browser upload uses `admin.php` / `MG_saveUserUpload()`.

## 5. Image-processing backend requirements

Image upload requires a working image-processing backend for thumbnail/display generation. PDF/ZIP uploads can work even when no image backend is available.

The Geeklog 2.1.1 / PHP 5.6 validation confirmed that image uploads succeed once GD is installed.

- [x] Confirm image upload on Geeklog 2.1.1 / PHP 5.6 with GD available.
- [x] Confirm persistent image output under `images/mediagallery/`.
- [x] Add centralized runtime capability detection for GD, ImageMagick and NetPBM.
- [x] Guard resize, conversion, rotation and watermark operations before backend-specific calls.
- [x] Return a clear MediaGallery error when the configured backend is unavailable instead of reaching undefined image functions.
- [x] Document image-backend requirements in the development README.
- [ ] Validate the new missing-backend error live once with GD intentionally disabled on the Geeklog 2.1.1/PHP 5.6 test instance.

## 6. Playback modernization

- [x] Remove executable Flash playback from default rendering.
- [x] Replace QuickTime/Windows Media ActiveX paths with HTML5 video/audio or download fallback.
- [x] Route MPEG/MOV/MP4 through maintained HTML5 rendering.
- [x] Move MP3/WMA playback to HTML5 audio where meaningful.
- [x] Replace FLV/SWF playback with safe download fallbacks.
- [x] Replace XSPF Flash play-all/radio paths with maintained album/playlist fallbacks.
- [x] Redirect legacy `fslideshow.php` to the maintained slideshow.
- [x] Remove unused SWF binaries, SWFObject helper code and duplicate obsolete JavaScript assets.
- [x] Remove fresh-install SWF configuration dependencies.
- [x] Fix undefined `$media_size_disp` use in legacy popup/download rendering.
- [ ] Decide which remaining ASF/MOV/MP3 playback controls are still meaningful.
- [ ] Decide whether legacy per-media playback options should be normalized or ignored.
- [ ] Decide whether the old `mms` mode should be retired.

## 7. Email modernization

- [x] Replace the bundled PHPMailer-based moderator notification path.
- [x] Use Geeklog `COM_mail()` transport.
- [x] Provide HTML and plaintext notification templates.
- [x] Preserve notification permissions and throttle behavior.
- [ ] Complete a live moderator-email test through the configured Geeklog mail backend before RC.

## 8. Templates, accessibility and SEO

- [x] Semantic `<h1>` album titles.
- [x] Navigation landmarks and accessible album search control.
- [x] Semantic thumbnail wrappers.
- [x] Canonical URLs on individual media pages.
- [x] Self-canonical album pagination while excluding sort variants.
- [x] Page-number suffix in album titles on page 2+.
- [x] Correct sort-form page indexing.
- [x] Improve HTML attribute escaping in media popup output.
- [ ] Review remaining inline presentation styles.
- [ ] Remove or replace remaining legacy IE-only slideshow transition code.
- [ ] Audit attribute escaping across all frame/theme variants.
- [ ] Review keyboard accessibility and form labeling across remaining admin/public templates.
- [ ] Add structured data only where MediaGallery has reliable source data and does not conflict with Geeklog core/theme output.

## 9. Interoperability and public API

MediaGallery 1.8.0 exposes album discovery through Geeklog's native service convention:

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

- [x] Implement `album_list` through `PLG_invokeService()`.
- [x] Reuse MediaGallery permission and album-tree rules rather than expose raw `mg_*` tables.
- [x] Preserve valid `member_album_root = 0` semantics.
- [ ] Complete live tests as owner, non-owner, anonymous user and administrator.

## 10. Code modernization and cleanup

- [x] Prefer Geeklog APIs where practical instead of duplicating core behavior.
- [x] Add Geeklog 2.1.1 input compatibility without core changes.
- [x] Validate request/array values in several historically unsafe paths.
- [x] Centralize 1.8 storage/runtime compatibility helpers.
- [x] Remove dead Flash/ActiveX playback assets and code paths already replaced.
- [ ] Fold `functions_legacy.inc` back into a clean final bootstrap if practical before RC.
- [ ] Remove confirmed dead compatibility branches once final supported versions are fixed.
- [ ] Complete PHP 8.x warning/deprecation cleanup.
- [ ] Review ZIP extraction security and any remaining legacy archive/import code.

## 11. Distribution

- [x] Use one installable archive: `dist/mediagallery_1.8.0_2.1.1.zip`.
- [x] Keep one top-level `mediagallery/` directory in the ZIP.
- [x] Exclude `.github/`, `dist/`, `.gitignore` and build-only directories.
- [x] Validate archive filenames against Geeklog 2.2.2 filename rules.
- [x] Validate presence of the 1.8 storage and migration helpers in the archive.
- [x] Keep archive generation intentional rather than rebuilding after every source commit.
- [ ] Rebuild the final RC archive only after remaining source/documentation changes are complete.

## 12. Release-candidate validation matrix

### Fresh installs

- [ ] Fresh 1.8.0 on Geeklog 2.1.1.
- [ ] Fresh 1.8.0 on Geeklog 2.2.2.
- [ ] Confirm Configuration UI has no obsolete FlowPlayer/Flash controls.
- [ ] Confirm upload/edit/delete, thumbnail generation, RSS, search and comments.
- [ ] Confirm clear failure/message when no image backend is available.

### Upgrades

- [ ] Upgrade disposable MediaGallery 1.7.0 copy.
- [ ] Upgrade disposable MediaGallery 1.7.3 copy.
- [ ] Run pre-migration to `images/mediagallery/` and verify source remains untouched.
- [ ] Confirm migration is idempotent.
- [ ] Confirm conflicting destination files fail safely without overwrite.
- [ ] Confirm legacy upgrade without preflight is refused when local-media rows exist but files are unavailable.
- [ ] Confirm administrator settings are preserved.

### Multisite

- [ ] Shared plugin code with separate DB/table prefix or databases.
- [ ] Separate `path_images`, `images_url` and `path_data`.
- [ ] Confirm Site A cannot write into or serve Site B's storage.
- [ ] Confirm temporary/upload directories are isolated.

### Upload/security regression

- [ ] Browser upload success and invalid/missing CSRF rejection.
- [ ] Four-slot browser upload option association.
- [ ] DNC off/on tests for PNG/GIF/BMP and `discard_original` variants.
- [ ] Executable/double-extension/unknown-MIME rejection.
- [ ] Remote Media public/private/redirect/oversize cases.
- [ ] FTP valid source, forged outside path, unsafe extension and escaping symlink.
- [ ] Batch continuation/cancellation as owner, another user and administrator.
- [ ] Stale-temp cleanup keeps recent/active entries and removes only fully stale trees.

### Functional regression

- [ ] Moderator email HTML/plaintext through Geeklog mail backend.
- [ ] `album_list` service permissions matrix.
- [ ] Media/album canonical output with multiple skins and paginated sort variants.
- [ ] MP3/WMA/MOV/ASF/SWF/FLV legacy-media rendering.
- [ ] ASF/MOV popup/download paths without undefined-variable warnings.
- [ ] Existing `fslideshow.php` URLs and `fslideshow` autotags.

## 13. Final RC cleanup

Before producing the 1.8.0 release candidate:

- [x] Add explicit image-backend capability detection and clear error reporting.
- [ ] Finish PHP 8.2/8.3 runtime audit.
- [ ] Resolve remaining dead playback/configuration controls.
- [ ] Decide fate of `functions_legacy.inc`; the legacy async upload endpoint has been removed.
- [ ] Complete remaining template/accessibility cleanup without breaking custom skins.
- [ ] Update final `CHANGELOG`, `README` and upgrade documentation.
- [ ] Run the full live-test matrix above.
- [ ] Build and validate the RC ZIP.

## Release principle

MediaGallery 1.8.0 should be safer to upgrade than 1.7.x, keep persistent user media outside replaceable plugin code, work naturally in single-site and shared-code multisite installations, use Geeklog-native services and mail where available, and fail explicitly when required runtime capabilities such as image processing are missing.
