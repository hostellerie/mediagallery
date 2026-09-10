# MediaGallery 1.8.0 Implementation Notes

This document tracks the current state of the `modernize-1.8.0` branch and the decisions that must remain true through release.

## Compatibility target

- Upgrade existing MediaGallery 1.7.x installations without resetting administrator settings.
- Target Geeklog 2.1.1 through 2.2.2 where practical.
- Keep syntax compatible with PHP 5.6, 7.4, 8.1 and 8.3 while the compatibility policy remains in force.
- Do not require changes to Geeklog core.
- Do not reintroduce the historical MediaGallery `config.php`.

## Configuration and multisite storage

Implemented:

- transitional 1.8.0 bootstrap in `functions.inc`;
- 1.7.3 implementation retained temporarily in `functions_legacy.inc`;
- `include/config_180.php` for runtime configuration and idempotent Configuration API migration;
- explicit upgrade support from known 1.7.x versions;
- site-specific media storage when both `$_CONF['path_images']` and `$_CONF['images_url']` are defined;
- historical `public_html/mediagallery/mediaobjects/` storage preserved when `images_url` is absent;
- site-specific `tmp` and FTP/upload staging under `$_CONF['path_data']/mediagallery/` when multisite storage is active;
- controlled creation of private work directories with error logging;
- no automatic relocation of existing media during upgrade.

The configuration migration adds missing administrator-facing settings without overwriting existing values, including valid `0`/`false` values. Runtime/calculated paths remain outside the Configuration API.

## Upload and import security

Implemented:

- Geeklog CSRF tokens on browser upload, Remote Media and both FTP import forms;
- browser upload slot alignment fixed for captions, descriptions, keywords, category, attached thumbnail and DNC flags;
- DNC now correctly interprets the submitted `value="1"`;
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

- MIME/extension consistency for ambiguous generic files;
- temporary-file naming and cleanup on interrupted processing;
- permissions around less common album mutation/admin paths;
- whether the legacy async endpoint can be removed completely after live compatibility testing.

## Email modernization

Active moderation notifications now use `MG_notifyModerators180()` with HTML and plaintext email templates and Geeklog `COM_mail()` transport. The historical notification throttle is retained.

The obsolete `MG_notifyModerators()` implementation and its dependency on the removed bundled PHPMailer path have now been deleted from `include/lib-upload.php`.

## Playback modernization

Default MediaGallery rendering no longer executes Flash, QuickTime ActiveX or Windows Media ActiveX players.

Implemented:

- QuickTime/Windows Media video templates moved to HTML5 `<video>` or download fallback;
- MP3/WMA/QuickTime audio templates moved to HTML5 `<audio>`;
- podcast MP3 playback moved to HTML5 `<audio>`;
- FLV and SWF formats use safe download fallbacks instead of executing Flash;
- XSPF play-all/radio Flash players replaced with album/playlist fallbacks;
- historical `fslideshow.php` redirects to the maintained slideshow;
- the `fslideshow` autotag no longer embeds Flash and links to the maintained slideshow;
- the legacy Flash markup in `fslideshow.thtml` has been removed;
- the empty SWFObject bootstrap was removed from MP3 display;
- global registration of `swfobject_2.1.js` has been removed;
- obsolete SWF binaries for MP3, FLV, XSPF, SimpleViewer and legacy slideshow playback have been removed;
- the Flash-specific `audio-player.js` helper has been removed.

`public_html/players/` now contains only the non-executable placeholder/index files still retained for compatibility. The remaining SWFObject JavaScript files can be removed after a final reference audit.

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
dist/mediagallery_1.8.0_2.0.0.zip
```

The ZIP contains one top-level `mediagallery/` directory, includes required tracked placeholder assets, and excludes `.github/`, `dist/` and build directories. No separate checksum file is retained in `dist/`.

Do not regenerate the archive after every source commit. Regenerate it when an online/install test is actually needed so `dist/` remains an intentional tested snapshot.

## Required live tests before merging

- upgrade an actual MediaGallery 1.7.0 installation;
- upgrade a 1.7.3 installation;
- fresh 1.8.0 installation;
- Geeklog 2.1.1 and 2.2.2 Configuration API behavior;
- standard single-site install with legacy media paths;
- multisite with separate database/table prefix, `path_images`, `images_url` and `path_data`;
- `tmp`/uploads directory creation and permissions;
- all new Configuration API controls save/reload correctly;
- browser upload success plus invalid/missing CSRF rejection;
- four-slot browser upload option association;
- executable/double-extension/unknown-MIME rejection;
- Remote Media public/private/redirect/oversize cases;
- FTP valid source, forged outside path, unsafe extension and escaping symlink;
- batch continuation/cancellation as owner, another user and MediaGallery administrator;
- moderator email HTML/plaintext through configured Geeklog mail backend;
- `album_list` as owner, non-owner, anonymous and administrator;
- media/album canonical output with multiple skins and paginated sort variants;
- MP3/WMA/MOV/ASF/SWF/FLV legacy-media rendering after HTML5/fallback conversion;
- old `fslideshow.php` URLs and existing `fslideshow` autotags;
- install the current `dist/mediagallery_1.8.0_2.0.0.zip` on disposable Geeklog 2.1.1 and 2.2.2 instances when the next online test point is reached.

## Release-candidate cleanup

Before an RC:

- fold the transitional `functions_legacy.inc` split back into a clean final bootstrap if practical;
- remove verified-unused SWFObject/QuickTime-era JavaScript assets;
- review/remove obsolete Configuration API controls whose playback technologies no longer exist;
- complete template/accessibility cleanup without breaking custom skins;
- update CHANGELOG/README/UPGRADE for final 1.8.0 behavior;
- keep PHP syntax CI green for every version still claimed by the compatibility policy.
