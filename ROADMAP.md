# MediaGallery 1.8.0 Roadmap

MediaGallery 1.8.0 is a modernization, hardening and interoperability release. Implementation and release validation are complete.

**Development branch:** `modernize-1.8.0`  
**Geeklog baseline:** 2.1.1 or newer  
**Compatibility policy:** keep PHP 5.6-compatible syntax for legacy Geeklog 2.1.1 deployments while validating PHP 7.4, 8.1 and 8.3.

## Current status

### Completed foundations

- [x] Geeklog 2.1.1+ baseline without Geeklog core modifications.
- [x] PHP 5.6-compatible source syntax with PHP 7.4/8.1/8.3 lint coverage.
- [x] Persistent media storage outside the replaceable `public_html/mediagallery/` tree.
- [x] Shared-code multisite isolation through each site's Geeklog paths and URLs.
- [x] Safe 1.7.x media pre-migration tool.
- [x] Configuration API cleanup and removal of obsolete fresh-install Flash/FlowPlayer settings.
- [x] Upload, FTP/ZIP/CLI import and Remote Media hardening.
- [x] Geeklog 2.1.1-compatible batch continuation model.
- [x] Moderation repair and Geeklog-native moderator email transport.
- [x] Explicit GD/ImageMagick/NetPBM capability handling.
- [x] Modern HTML5 playback and safe legacy-media fallbacks.
- [x] Responsive public/admin templates, accessibility, SEO and structured-data improvements.
- [x] Sharper portrait/landscape album-card rendering.
- [x] `album_list` service through `PLG_invokeService()`.
- [x] Media and album lifecycle notifications through Geeklog plugin APIs.
- [x] Installable 1.8.0 test ZIP generation and validation.
- [x] Documentation cleanup: obsolete 1.6/1.7, Japanese and duplicated public documentation removed.
- [x] `README.md`, `UPGRADE`, `CHANGELOG.md`, `SERVICES.md` and documentation index updated for 1.8.0.
- [x] Administrator guide moved out of the public web tree and exposed through protected `admin/help.php`.
- [x] Administrator guide restored as a post-installation usage manual covering albums, media, Member Albums, quotas, EXIF/IPTC, RSS, batch, autotags, maintenance and troubleshooting.

## Release validation

The final validation pass is complete. MediaGallery 1.8.0 has been exercised on Geeklog 2.1.1 and Geeklog 2.2.2, including upgrades from 1.7.3 and 1.7.0, persistent storage, image upload and derivative generation, batch security, moderation, Geeklog-native mail, representative playback/fallback behavior, multisite operation, and Agent/Eclipse/Hub interoperability.

The release archive is rebuilt automatically from validated source and PHP syntax is checked on PHP 5.6, 7.4, 8.1 and 8.3.

## 1. Compatibility and bootstrap

- [x] Require Geeklog 2.1.1 or newer.
- [x] Preserve compatibility with Geeklog 2.2.2.
- [x] Avoid Geeklog core changes.
- [x] Preserve database content and administrator configuration during upgrade.
- [x] Keep source syntax compatible with PHP 5.6.
- [x] Complete the static PHP 8.x audit of MediaGallery-owned hot paths.
- [x] Correct `phpblock_mg_maenroll()` dependency loading.
- [x] Keep random-media/member-album PHP blocks compatible with Geeklog 2.1.1.
- [x] Complete the live PHP 8.2/8.3 runtime warning/deprecation audit.
- [x] Run the final Geeklog 2.1.1 / 2.2.2 regression matrix.

## 2. Persistent media storage and upgrades

Runtime media are stored below Geeklog's configured images path:

```php
$_MG_CONF['path_mediaobjects'] = rtrim($_CONF['path_images'], '/\\') . '/mediagallery/';
```

The historical `public_html/mediagallery/mediaobjects/` location is a migration source only.

- [x] Centralize storage path/URL resolution.
- [x] Store 1.8 public media below `path_images/mediagallery/`.
- [x] Isolate private temporary/upload data below each site's `path_data/mediagallery/`.
- [x] Avoid `HTTP_HOST`-derived site identity.
- [x] Create required directories with explicit error handling.
- [x] Implement copy-and-verify migration with no automatic source deletion.
- [x] Refuse conflicting destination files rather than overwrite them.
- [x] Provide `tools/migrate-media-storage.php`.
- [x] Confirm a subsequent 1.8 ZIP replacement does not remove persistent media.
- [x] Validate the full pre-migration + ZIP upgrade path from MediaGallery 1.7.3.
- [x] Repeat on a disposable MediaGallery 1.7.0 installation.
- [ ] Confirm migration idempotence and conflict refusal live.
- [ ] Confirm administrator configuration survives both upgrades.

## 3. Configuration cleanup

- [x] Runtime configuration/migration helpers added for 1.8.
- [x] Missing Configuration API entries added without resetting valid values.
- [x] Runtime-derived paths/URLs kept outside administrator-editable configuration.
- [x] Fresh-install FlowPlayer/Flash controls removed.
- [x] Playback controls with no useful HTML5 equivalent removed from maintained interfaces.
- [x] Harmless legacy rows tolerated on upgraded sites.
- [ ] Decide before RC whether obsolete 1.7.x Flash/FlowPlayer database rows should be actively removed. Default choice should be **leave them harmlessly in place** unless live upgrade tests prove removal safe on both Geeklog lines.

## 4. Upload, import, batch and security

### Implemented

- [x] Normal Geeklog CSRF protection on browser actions that start mutations.
- [x] Correct upload-slot metadata association.
- [x] Correct DNC/original-format behavior and real format conversion.
- [x] Executable/server-side filename rejection.
- [x] Defense-in-depth validation in `MG_getFile()`.
- [x] FTP path confinement and symlink rejection.
- [x] Recursive CLI import hardening.
- [x] ZIP traversal/symlink/count/size hardening.
- [x] Remote Media restricted to bounded public HTTP(S) resources.
- [x] Root Album upload prevention.
- [x] MIME/extension coherence checks for handled formats.
- [x] Deterministic failure cleanup and stale-temp cleanup.
- [x] Album/global/watermark/sort/resize/rebuild/media-manager mutations protected.
- [x] Posted media IDs bound to the authorized album.
- [x] Orphaned batch-caption and asynchronous-upload mutation paths removed.
- [x] Moderation approval/rejection repaired.

### Geeklog 2.1.1 batch model

- [x] Batch **start** operations retain normal Geeklog CSRF validation.
- [x] Internal continuation/cancellation is POST-only.
- [x] Continuation validates the server-generated `session_id` and ownership.
- [x] Administrator override remains limited to eligible MediaGallery administrators.
- [x] Internal continuation does **not** require Geeklog 2.1.1's referer-bound one-time token.

### Remaining live security tests

- [ ] MIME mismatch rejection and generic-file compatibility.
- [ ] Stale-temp cleanup with recent vs stale trees.
- [x] Batch start rejects invalid CSRF.
- [x] Batch continuation rejects GET, missing/invalid session ID and wrong owner.
- [x] Batch continuation/cancellation succeeds for the owner and eligible administrator.
- [x] Full moderation upload/edit/approve/reject flow including forged album bindings.

## 5. Image processing

- [x] Image upload confirmed on Geeklog 2.1.1 / PHP 5.6 with GD.
- [x] Generated derivatives stored in persistent media storage.
- [x] GD, ImageMagick and NetPBM capability detection centralized.
- [x] Resize/conversion/rotation/watermark calls guarded.
- [x] Clear error returned when configured backend is unavailable.
- [ ] Validate the missing-backend error live once with the configured backend intentionally unavailable.

## 6. Playback

- [x] Active Flash, ActiveX and QuickTime plugin execution removed from maintained output.
- [x] MPEG/MOV/MP4 routed through HTML5 rendering where supported.
- [x] Supported audio uses HTML5 where meaningful.
- [x] FLV/SWF use safe download/fallback behavior.
- [x] Generated `mms:` links retired.
- [x] Obsolete XSPF/Flash play-all paths replaced.
- [x] Old `fslideshow.php` routes redirect to the maintained slideshow.
- [x] Live-test representative MP3/WMA/MOV/MP4/MPEG/FLV/SWF records on both Geeklog targets without PHP warnings.

## 7. Moderation and email

- [x] Bundled PHPMailer moderator path replaced by Geeklog `COM_mail()`.
- [x] HTML and plaintext templates provided.
- [x] Notification permissions/throttling retained.
- [x] Queue relations and moderation promotion/removal repaired.
- [x] Complete a live moderator-email test through the configured Geeklog backend.
- [x] Complete approval/rejection tests with files and database rows inspected before/after.

## 8. Templates, accessibility, image quality and SEO

- [x] Responsive slideshow/lightbox viewer.
- [x] Semantic headings and navigation landmarks.
- [x] Modern album/media/search/file-list/podcast skins.
- [x] Improved escaping and form labels.
- [x] Canonical media URLs and canonical-safe album pagination.
- [x] Paginated title suffixes and editorial meta descriptions.
- [x] Conservative media JSON-LD.
- [x] Album-card thumbnail sharpness improvements.
- [x] Permanent scale transforms that amplified blur removed.
- [ ] Complete final visual regression across bundled skins with portrait and landscape media.

## 9. Interoperability

### Shared capability contract

- [x] `plugin_getcapabilities_mediagallery()` advertises the provider roles and shared capabilities defined by the Geeklog memorandum.
- [x] Declare `content.read`, `content.collection`, `content.search`, `content.url.resolve` and `content.lifecycle`.
- [x] Declare `media.album.list`, `media.album.read`, `media.item.read` and `media.item.collection`.
- [x] Expose `dashboard.summary` through the bounded `dashboard_summary` service for Eclipse and other administration consumers.
- [x] Expose permission-filtered `album_read` and `media_read` services so Agent, Hub and future consumers do not need MediaGallery SQL knowledge.
- [x] Keep capability discovery consumer-neutral: MediaGallery has no dependency on Agent, Eclipse or Hub.
- [x] Align `plugin.json` with the maintained 1.8.0 baseline: Geeklog 2.1.1+ and PHP 5.6+.
- [x] Correct Media Item Info description/excerpt mapping for normalized consumers.
- [x] Live-test capability discovery and all new read services on Geeklog 2.1.1 and 2.2.2.
- [x] Validate Eclipse 1.2 rendering of albums/media/pending/storage summary from the exact release archive.
- [x] Validate Agent/Hub reads with anonymous, member and administrator permission contexts.


### Album discovery

- [x] `album_list` implemented through `PLG_invokeService()`.
- [x] MediaGallery permissions and album-tree rules reused.
- [x] `member_album_root = 0` remains valid.
- [ ] Live-test `album_list` as owner, non-owner, anonymous user and administrator.

### Lifecycle events

- [x] Existing media save/delete lifecycle events retained.
- [x] Albums use `album:<id>` identifiers compatible with Geeklog 2.1.1.
- [x] Album create/update/delete events emitted.
- [x] Affected album pages notified on media add/edit/delete/reorder/move.
- [x] Old/new parents notified on album movement.
- [x] `plugin_getiteminfo_mediagallery()` resolves namespaced albums.
- [x] Anonymous URLs returned only for anonymously readable, non-hidden albums.
- [x] `plugin_idToURL_mediagallery()` resolves deterministic album URLs.
- [x] Repeated album notifications deduplicated per request.
- [x] MediaGallery remains consumer-agnostic and does not call IndexNow directly.
- [ ] Live-test MediaGallery → IndexNow 1.3.0 save/delete flow on Geeklog 2.1.1 and 2.2.2.

See `docs/SERVICES.md` for the service/lifecycle contract.

## 10. Code structure

- [x] Prefer Geeklog APIs over duplicate internal mechanisms where practical.
- [x] Centralize 1.8 runtime/storage/security/interoperability helpers.
- [x] Remove dead Flash/ActiveX code already superseded.
- [x] Complete static PHP 8.x warning/deprecation cleanup in owned hot paths.
- [ ] Complete live PHP 8.2/8.3 validation.
- [ ] Decide final `functions_legacy.inc` structure.

**RC recommendation:** keep `functions_legacy.inc` as a transitional implementation layer for 1.8.0. Folding it back into a large bootstrap immediately before RC adds regression risk without user-facing benefit. Revisit structural consolidation after 1.8.0.

## 11. Documentation

- [x] `README.md` current for 1.8.0.
- [x] `UPGRADE` current for persistent-storage preflight and 1.7.x upgrade rules.
- [x] `ROADMAP.md` current.
- [x] `TESTING-1.8.md` is the live regression checklist.
- [x] `IMPLEMENTATION_NOTES.md` retained for design details.
- [x] `docs/CHANGELOG.md` replaces the old excerpted plain-text changelog.
- [x] `docs/SERVICES.md` documents service/lifecycle interoperability.
- [x] `docs/ADMIN_GUIDE.html` is a private, post-installation administrator manual.
- [x] `admin/help.php` protects and renders the administrator guide inside the plugin administration UI.
- [x] Obsolete/Japanese/duplicated 1.6/1.7 documentation removed.
- [x] Public static usage/install documentation removed from the installable web tree.

Documentation cleanup is no longer an RC blocker except for corrections discovered during live testing.

## 12. Distribution

- [x] Single installable archive: `dist/mediagallery_1.8.0_2.1.1.zip`.
- [x] One top-level `mediagallery/` directory.
- [x] Build-only content excluded.
- [x] Archive filenames validated against Geeklog 2.2.2 rules.
- [x] Required migration/storage helpers validated in the archive.
- [x] Test archive automatically rebuilt after validated branch changes.
- [x] Obsolete public documentation removed from source tree.
- [ ] Confirm the next generated archive contains `docs/ADMIN_GUIDE.html` and `admin/help.php` but no obsolete public docs.
- [x] Rebuild and validate the final release archive after the live test matrix closes.

## 13. Release validation record

### Phase A — Geeklog 2.1.1 first

This is the highest-risk compatibility target and should be validated before 2.2.2.

- [ ] Fresh install 1.8.0.
- [ ] Open Configuration and all MediaGallery admin menu sections.
- [ ] Open protected Help and confirm a non-admin cannot access it.
- [ ] Create/edit/move/delete album and sub-album.
- [ ] Browser image upload with JPEG/PNG/GIF/BMP.
- [ ] DNC on/off and discard-original variants.
- [ ] Edit/move/delete/reorder media and set/reset album cover.
- [ ] Rebuild thumbnails and resize display images.
- [ ] Batch start + continuation/cancellation ownership matrix.
- [ ] Member Album enrollment, quota and PHP block.
- [ ] Categories and EXIF/IPTC administration.
- [ ] RSS rebuild/search/comments/What's New/Random Image Block.
- [ ] Slideshow and portrait/landscape visual regression.
- [ ] Moderated upload/edit/approve/reject.
- [ ] Moderator email.
- [ ] `album_list` permissions.
- [ ] Media/album lifecycle notifications with IndexNow 1.3.0.
- [ ] Representative legacy media playback/fallback.
- [ ] Confirm no unexpected PHP warnings/notices in Geeklog `error.log`.

### Phase B — Upgrade validation

- [ ] MediaGallery 1.7.3 disposable copy: pre-migrate media, upgrade ZIP, verify content/configuration.
- [ ] Re-run migration and confirm idempotence.
- [ ] Verify conflict refusal without overwrite.
- [ ] Repeat essential upgrade checks from 1.7.0.

### Phase C — Geeklog 2.2.2 / PHP 8.3 regression

- [ ] Fresh install.
- [ ] Repeat core album/media/admin/batch/moderation flows.
- [ ] Run PHP 8.3 warning/deprecation audit.
- [ ] Validate RSS/podcast and old media records without warnings.
- [ ] Repeat interoperability/IndexNow checks.
- [ ] Repeat visual regression.

### Phase D — Multisite

- [ ] Shared plugin code with separate DB/table prefix or databases.
- [ ] Separate `path_images`, `images_url` and `path_data`.
- [ ] Confirm Site A cannot write into or serve Site B storage.
- [ ] Confirm temporary/upload directories remain isolated.

## 14. Release freeze

Phases A–D are green; the release freeze now keeps the validated compatibility and packaging decisions stable.

- [ ] Record the tested Geeklog/PHP combinations in `TESTING-1.8.md` or release notes.
- [ ] Keep `functions_legacy.inc` for 1.8.0 unless a test demonstrates a concrete problem.
- [ ] Keep harmless obsolete configuration rows unless removal has been proven safe in both upgrade paths.
- [ ] Regenerate `dist/mediagallery_1.8.0_2.1.1.zip` from the final source.
- [ ] Inspect archive contents and install the exact RC ZIP once on Geeklog 2.1.1 and once on 2.2.2.
- [ ] Tag/package the release candidate only after those archive installs pass.

## Release principle

MediaGallery 1.8.0 should be safer to upgrade than 1.7.x, preserve user media outside replaceable plugin code, work naturally in single-site and shared-code multisite installations, provide modern accessible public output, use Geeklog-native APIs wherever practical, expose content changes to the wider Geeklog ecosystem, and fail explicitly when required runtime capabilities are unavailable.
