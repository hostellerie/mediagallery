# MediaGallery 1.8.0 Implementation Notes

This document tracks the current state of the `modernize-1.8.0` branch and the decisions that must remain true through release.

## Compatibility target

- Upgrade existing MediaGallery 1.7.x installations without resetting administrator settings.
- Require Geeklog 2.1.1 or newer; Geeklog 2.0.x is not a supported target for MediaGallery 1.8.0.
- Keep syntax compatible with PHP 5.6, 7.4, 8.1 and 8.3 while the compatibility policy remains in force.
- Do not require changes to Geeklog core.
- Do not reintroduce the historical MediaGallery `config.php`.

## Configuration and multisite storage

Implemented:

- transitional 1.8.0 bootstrap in `functions.inc`;
- 1.7.3 implementation retained temporarily in `functions_legacy.inc`;
- `include/config_180.php` for runtime configuration and idempotent Configuration API migration;
- explicit upgrade support from known 1.7.x versions;
- persistent public media storage under `$_CONF['path_images']/mediagallery/` for all 1.8.0 installations;
- `$_CONF['images_url']` respected when explicitly supplied, with `{site_url}/images` used only for the standard single-site image path;
- shared-code multisite isolation through each site's own `path_images` / `images_url` pair;
- `include/storage_180.php` copy-and-verify migration with no source deletion and conflict refusal;
- CLI preflight tool `tools/migrate-media-storage.php` for 1.7.x sites before Geeklog's public-plugin-directory replacement;
- site-specific `tmp` and FTP/upload staging under `$_CONF['path_data']/mediagallery/`;
- controlled creation of public/private work directories with error logging;
- upgrade failures propagate as Geeklog errors instead of marking 1.8.0 installed after a failed migration;
- fresh 1.8.0 installations no longer create the obsolete FlowPlayer option or the Flash Media configuration tab/`swf_*` controls.

The configuration migration adds missing administrator-facing settings without overwriting existing values, including valid `0`/`false` values. Runtime/calculated paths remain outside the Configuration API.

Upgraded 1.7.x sites may temporarily retain obsolete Flash/FlowPlayer rows in `conf_values`. They are ignored by the 1.8 runtime. Do not delete those rows during upgrade until the deletion path has been verified on both Geeklog 2.1.1 and 2.2.2.

## Image backend validation

Implemented:

- centralized backend availability check in `include/lib/imglib/lib-image.php`;
- GD requires the actual PHP GD functions before any resize/convert/rotate/watermark operation;
- ImageMagick validates `identify` and `convert`;
- NetPBM validates a scaler plus core JPEG conversion commands;
- explicit-path configurations are checked directly while empty paths may resolve commands through `PATH`;
- missing/unusable backends now return a readable MediaGallery error and log it once per request instead of reaching undefined image functions.

The Geeklog 2.1.1 / PHP 5.6 live test confirmed that image upload succeeds after enabling GD, while PDF/ZIP uploads did not require the image backend.

## Upload and import security

Implemented:

- Geeklog CSRF tokens on browser upload, Remote Media and both FTP import forms;
- browser upload slot alignment fixed for captions, descriptions, keywords, category, attached thumbnail and DNC flags;
- DNC now correctly interprets the submitted `value="1"`;
- DNC no longer gets overwritten internally;
- when DNC is disabled and originals are retained, a supported original image is actually converted to JPEG through the configured image backend before its stored extension/MIME are changed;
- when DNC is enabled, the original image format is preserved;
- conversion failure leaves the original format intact and reports an upload error instead of recording a false JPEG MIME/extension;
- legacy async upload identity comes from the authenticated Geeklog session rather than a POSTed `uid`;
- reusable security helpers in `include/upload_security_180.php`;
- executable/server-side filename extensions rejected on browser/async uploads;
- `MG_getFile()` now performs the same unsafe-filename check itself as defense in depth;
- the old `.exe` generic MIME mapping has been removed from `MG_getFileTypeFromExt()`;
- FTP paths are resolved with `realpath()` and confined under configured `ftp_path`;
- hidden FTP paths are revalidated before session registration;
- recursive batch sources are revalidated before every continuation cycle;
- batch continuation/cancellation validates session ownership;
- CLI `climport.php` now applies the same unsafe-filename protection and no longer treats `.exe` as a generic import format;
- Remote Media fetches accept public HTTP(S) destinations only, reject credentials and private/reserved/localhost targets, disable redirects, and use bounded timeouts/download size.

Still review before RC:

- MIME/extension consistency now prefers getID3, falls back to local PHP fileinfo when getID3 is inconclusive, and rejects known-extension mismatches while preserving generic unknown-extension files;
- live regression tests remain for mismatch rejection and generic-file compatibility;
- deterministic upload failure paths now remove the main `tmpPath`, and special-image thumbnail conversion removes its `wip*.jpg` file on success/failure;
- still define a stale-temp policy for genuinely interrupted/killed PHP requests;
- global album permission/attribute changes and watermark manage/upload/delete actions now use Geeklog CSRF tokens in addition to their existing access rules;
- album sort and static media sort now use Geeklog CSRF tokens; static sort also revalidates album write access in the save handler;
- resize/rebuild, media-manager save/delete/move/batch, direct rotation, media-edit save and rating/view resets now use Geeklog CSRF validation;
- direct rotation now uses POST and verifies both album write access and the requested album/media association before touching files;
- continue audit of remaining caption/moderation/delete-session mutations before RC;
- the orphaned legacy asynchronous `public_html/upload.php` endpoint and its dedicated `MG_saveUpload()` handler have been removed; the maintained browser upload path is `admin.php` / `MG_saveUserUpload()`.

## Email modernization

Active moderation notifications now use `MG_notifyModerators180()` with HTML and plaintext email templates and Geeklog `COM_mail()` transport. The historical notification throttle is retained.

The obsolete `MG_notifyModerators()` implementation and its dependency on the removed bundled PHPMailer path have now been deleted from `include/lib-upload.php`.

## Playback modernization

Default MediaGallery rendering no longer executes Flash, QuickTime ActiveX or Windows Media ActiveX players.

Implemented:

- QuickTime/Windows Media video templates moved to HTML5 `<video>` or download fallback;
- MPEG/MOV/MP4 routing now consistently uses the HTML5 MOV/video renderer rather than legacy WMP/FLV routing flags;
- MP3/WMA/QuickTime audio templates moved to HTML5 `<audio>`;
- podcast MP3 playback moved to HTML5 `<audio>`;
- FLV and SWF formats use safe download fallbacks instead of executing Flash;
- XSPF play-all/radio Flash players replaced with album/playlist fallbacks;
- historical `fslideshow.php` redirects to the maintained slideshow;
- the `fslideshow` autotag no longer embeds Flash and links to the maintained slideshow;
- the legacy Flash markup in `fslideshow.thtml` has been removed;
- the empty SWFObject bootstrap was removed from MP3 display;
- SWFObject/QuickTime helper JavaScript files and unused duplicate jQuery Cycle builds have been removed;
- obsolete SWF binaries for MP3, FLV, XSPF, SimpleViewer and legacy slideshow playback have been removed;
- the Flash-specific `audio-player.js` helper has been removed;
- `MG_displaySWF()` and `MG_displayFLV()` are decoupled from removed `swf_*` configuration keys so fresh 1.8 installs cannot generate undefined-key warnings;
- legacy ASF/MOV popup/download rendering now uses the thumbnail size actually returned by `Media::getThumbInfo()` instead of the undefined `$media_size_disp` variable.

`public_html/players/` now contains only the non-executable placeholder/index files still retained for compatibility.

Still review before RC:

- which remaining ASF/MOV/MP3 playback controls have meaningful HTML5 equivalents and should remain visible;
- whether legacy per-media playback options should be normalized or simply ignored when no HTML5 equivalent exists;
- whether the old `mms` playback mode should be retired.

## Templates, accessibility and SEO

Implemented:

- semantic `<h1>` for album titles;
- navigation landmarks and accessible album search control;
- semantic album/media thumbnail wrappers;
- canonical URL on individual media pages;
- self-canonical album pagination, excluding sort variants;
- page-number suffix in album HTML titles on page 2+;
- correction of the sort form's zero-based/one-based page mismatch;
- HTML attribute escaping improved in the media popup.

Still review:

- remaining inline presentation styles;
- legacy IE-only slideshow transition code;
- HTML attribute escaping in all frame/theme variants;
- structured data only where MediaGallery has accurate source data;
- no invented meta descriptions.

## Interoperability service

MediaGallery 1.8.0 implements Geeklog's native service convention for album discovery:

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

The service applies MediaGallery access rules and lets plugins such as Documents consume album trees without querying `mg_*` tables directly. `member_album_root = 0` remains a valid configured root.

## Distribution archives

When an installable package is needed for online testing, update `.github/dist-trigger` or run **Build MediaGallery installable archive** manually.

The workflow builds the current `modernize-1.8.0` code, validates the archive and checksum internally, removes older generated packages, and commits one fixed archive to the same branch:

```text
dist/mediagallery_1.8.0_2.1.1.zip
```

The ZIP contains one top-level `mediagallery/` directory, includes required tracked placeholder assets, and excludes `.github/`, `dist/` and build directories. No separate checksum file is retained in `dist/`.

Do not regenerate the archive after every source commit. Regenerate it when an online/install test is actually needed so `dist/` remains an intentional test snapshot.

## Required live tests before merging

- upgrade an actual MediaGallery 1.7.0 installation;
- upgrade a 1.7.3 installation;
- fresh 1.8.0 installation;
- Geeklog 2.1.1 and 2.2.2 Configuration API behavior;
- fresh Configuration UI has no FlowPlayer or Flash Media controls and no undefined-key warnings;
- upgraded 1.7.x Configuration UI remains usable even if obsolete Flash rows still exist in `conf_values`;
- standard single-site install with persistent `images/mediagallery/` storage;
- 1.7.3 preflight migration to `images/mediagallery/`, then ZIP upgrade, with source and destination verification;
- verify a legacy ZIP upgrade without preflight is refused when local media rows exist but no user-media files are available;
- multisite with separate database/table prefix, `path_images`, `images_url` and `path_data`;
- `tmp`/uploads directory creation and permissions;
- all new Configuration API controls save/reload correctly;
- browser upload success plus invalid/missing CSRF rejection;
- four-slot browser upload option association;
- DNC off: upload PNG/GIF/BMP and verify the retained original is a real JPEG with `.jpg` extension/MIME;
- DNC on: verify PNG/GIF/BMP original format is preserved;
- DNC behavior with `discard_original = 1`;
- executable/double-extension/unknown-MIME rejection;
- Remote Media public/private/redirect/oversize cases;
- FTP valid source, forged outside path, unsafe extension and escaping symlink;
- batch continuation/cancellation as owner, another user and MediaGallery administrator;
- moderator email HTML/plaintext through configured Geeklog mail backend;
- `album_list` as owner, non-owner, anonymous and administrator;
- media/album canonical output with multiple skins and paginated sort variants;
- MP3/WMA/MOV/ASF/SWF/FLV legacy-media rendering after HTML5/fallback conversion;
- ASF/MOV popup/download paths do not emit undefined `$media_size_disp` warnings;
- old `fslideshow.php` URLs and existing `fslideshow` autotags;
- install the current `dist/mediagallery_1.8.0_2.1.1.zip` on disposable Geeklog 2.1.1 and 2.2.2 instances when the next online test point is reached.

## Release-candidate cleanup

Before an RC:

- fold the transitional `functions_legacy.inc` split back into a clean final bootstrap if practical;
- review/remove obsolete Configuration API controls whose playback technologies no longer exist;
- verify whether obsolete 1.7.x `conf_values` rows can be safely removed during upgrade on both supported Geeklog versions;
- complete template/accessibility cleanup without breaking custom skins;
- update CHANGELOG/README/UPGRADE for final 1.8.0 behavior;
- keep PHP syntax CI green for every version still claimed by the compatibility policy.
