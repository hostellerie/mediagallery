# MediaGallery changelog

This changelog tracks the maintained MediaGallery development line. MediaGallery 1.9.0 is the current release line; the 1.8.0 section below records the modernization foundation carried forward into 1.9.0.

## 1.9.0 — release candidate

### SEO and interoperability

- Add album `CollectionPage` / `ItemList` structured data and retain content-aware media schema.
- Normalize local media URLs used in structured data.
- Add content-specific description fallbacks.
- Add optional OGP integration while preserving standalone Open Graph/Twitter metadata fallbacks.

### Language updates

- Add or refresh the maintained UTF-8 translations for Spanish, Italian, Japanese, Russian, Chinese Simplified, Chinese Traditional, Hebrew, Persian, French Canada, French France, German, German Formal and Spanish Argentina.
- Synchronize the maintained language files with the current English language contract and include them in the 1.9.0 distribution archive.

### PHP 8 compatibility and release hardening

- Normalize optional media renderer metadata to prevent undefined-array-key warnings on PHP 8.x for legacy/imported records.
- Complete the remaining compatibility work tracked by upstream issue #11.
- Preserve the MediaGallery 1.8 compatibility baseline: Geeklog 2.1.1 or newer, including 2.2.2.
- Run PHP syntax validation on the actual `mediagallery_1.9.0` branch.
- Build `dist/mediagallery_1.9.0_2.1.1.zip` from the validated branch.

## 1.8.0 — modernization foundation

### Compatibility and platform

- Set Geeklog 2.1.1 as the minimum supported Geeklog version.
- Preserve compatibility with Geeklog 2.2.2.
- Keep PHP 5.6-compatible syntax for legacy Geeklog 2.1.1 deployments while linting and validating newer PHP branches through PHP 8.x.
- Remove the need for Geeklog core modifications.
- Repair legacy PHP-block bootstrap behavior so MediaGallery blocks load the helpers they require on Geeklog 2.1.1.

### Persistent media storage and upgrades

- Move runtime media storage out of the replaceable `public_html/mediagallery/` plugin directory.
- Store MediaGallery user media below Geeklog's configured image root, normally `images/mediagallery/`.
- Support shared-code multisite installations through site-specific `path_images`, `images_url` and `path_data` values.
- Add centralized storage/path resolution and storage directory creation.
- Add safe copy-and-verify migration support for legacy `public_html/mediagallery/mediaobjects/` trees.
- Add `tools/migrate-media-storage.php` for required 1.7.x pre-migration before using Geeklog's ZIP plugin updater.
- Never remove the legacy media source automatically during migration.
- Refuse conflicting destination files instead of silently overwriting them.
- Propagate migration failures to the installer/upgrader.

### Configuration cleanup

- Add the 1.8 runtime/configuration compatibility layer.
- Preserve valid existing Configuration API values during upgrades, including `0` and `false` values.
- Keep runtime-derived paths and URLs outside administrator-editable configuration.
- Remove obsolete fresh-install Flash/FlowPlayer configuration controls.
- Remove maintained-interface controls that no longer affect HTML5 playback.

### Upload and import security

- Add or strengthen Geeklog CSRF protection on browser upload, Remote Media, FTP import and sensitive administration actions.
- Validate media/album ownership and membership before edit, move, delete, rotate, watermark and batch operations.
- Reject unsafe executable/server-side filenames and strengthen validation inside the file-import path.
- Improve content-derived MIME detection and MIME/extension consistency checks for explicitly supported formats.
- Restrict Remote Media fetching to bounded public HTTP(S) targets and reject localhost, private/reserved addresses and redirects.
- Constrain FTP imports with `realpath()` and reject escaping paths/symlinks.
- Harden ZIP extraction against path traversal, unsafe temporary paths, symbolic links, excessive entry counts and oversized declared payloads.
- Harden recursive CLI imports and preserve nested directory-to-subalbum mappings.
- Prevent uploads to the synthetic Root Album (`album_id=0`).
- Add deterministic temporary-file cleanup and conservative stale-temp cleanup for interrupted operations.
- Remove the orphaned legacy asynchronous upload endpoint.
- Remove the obsolete batch-caption mutation path.

### Batch processing and Geeklog 2.1.1

- Keep batch-start mutations protected by Geeklog CSRF validation.
- Make internal batch continuation/cancellation POST-only.
- Validate the server-generated batch `session_id` and owning user for each continuation.
- Avoid Geeklog 2.1.1's referer-bound one-time token during internal batch continuation, fixing false “security token expired” failures.

### Moderation

- Repair Geeklog-native moderated upload handling.
- Revalidate administrator permissions and queued album/media membership.
- Correctly promote approved queue rows into active MediaGallery tables.
- Fully remove rejected queue rows and their temporary files.
- Allow moderation edit/save without incorrectly requiring configuration access.

### Image processing

- Centralize runtime detection for GD, ImageMagick and NetPBM.
- Guard resize, conversion, rotation and watermark operations before backend-specific calls.
- Return a clear MediaGallery error when the configured image-processing backend is unavailable.
- Confirm image upload and derivative generation on Geeklog 2.1.1 / PHP 5.6 with GD available.

### Playback modernization

- Remove active Flash playback from maintained default rendering.
- Replace QuickTime/Windows Media ActiveX playback paths with HTML5 audio/video or safe download fallbacks.
- Route supported MPEG/MOV/MP4 media through maintained HTML5 rendering.
- Use HTML5 audio where applicable.
- Replace FLV/SWF execution with download fallback behavior.
- Retire generated `mms:` links.
- Replace obsolete XSPF/Flash play-all behavior with maintained album/playlist behavior.
- Redirect legacy `fslideshow.php` entry points to the maintained slideshow.
- Remove unused SWF binaries, SWFObject helpers and obsolete duplicate playback assets.

### Public interface, accessibility and SEO

- Modernize default album, media, search, file-list, podcast and bundled gallery skins with responsive HTML/CSS.
- Add semantic album/media heading structure and improved landmark/form labeling.
- Replace maintained presentation tables with semantic responsive forms/layouts where practical.
- Improve escaping of attributes, persisted values, action links and translated confirmation messages.
- Add canonical URLs on media pages.
- Add self-canonical album pagination while excluding sort variants.
- Add page-number suffixes to paginated album titles.
- Add canonical-safe meta descriptions based on existing album/media descriptions.
- Add conservative JSON-LD for MediaGallery-owned `ImageObject`, `AudioObject` and eligible `VideoObject` data.
- Avoid competing album-level generic page schema when page-schema ownership may belong to Geeklog or the active theme.
- Replace the legacy slideshow chrome with a responsive native lightbox-style viewer supporting keyboard navigation, swipe, autoplay and reduced motion.
- Improve album-card thumbnail sharpness by using the original local image as the visual source when available.
- Remove persistent scale transforms that amplified blur and made portrait media appear artificially square.

### Email

- Replace the bundled PHPMailer moderator-notification path with Geeklog `COM_mail()`.
- Provide HTML and plain-text notification templates.
- Preserve existing permission and throttling behavior.

### Interoperability

- Add a shared provider capability declaration for Agent, Eclipse, Hub and future consumers.
- Add the bounded `dashboard_summary` service with album, media and moderation metrics plus storage/moderation alerts.
- Add permission-filtered `album_read` and `media_read` services with normalized identity, subtype, URL, description, ownership and media metadata.
- Declare content, lifecycle, URL-resolution and MediaGallery album/media capabilities using the memorandum's provider-neutral names.
- Correct the media Item Info description/excerpt mapping used by normalized content consumers.
- Align `plugin.json` with the 1.8.0 compatibility policy (Geeklog 2.1.1+, PHP 5.6+).

- Add a read-only `album_list` service through Geeklog `PLG_invokeService()`.
- Reuse MediaGallery permission and album-tree rules rather than exposing raw `mg_*` tables to consumers.
- Preserve valid `member_album_root = 0` behavior.
- Keep existing media `PLG_itemSaved()` and `PLG_itemDeleted()` lifecycle events.
- Add album lifecycle events using portable namespaced IDs such as `album:52`.
- Notify affected album pages when media are added, edited, deleted, reordered or moved.
- Notify old and new parent album listings when an album moves.
- Extend `plugin_getiteminfo_mediagallery()` to resolve album objects and expose public album URLs only when anonymously readable.
- Extend `plugin_idToURL_mediagallery()` to resolve deterministic album URLs for consumers handling deletions.
- Deduplicate repeated album lifecycle notifications during a single request.
- Keep this integration generic so IndexNow, XML Sitemap, Hub and future connectors can consume the same Geeklog lifecycle contract without MediaGallery depending on any one plugin.

### Distribution and documentation

- Add automated PHP linting and installable archive validation.
- Build one development archive, `dist/mediagallery_1.8.0_2.1.1.zip`, with one top-level `mediagallery/` directory.
- Exclude repository/build-only files from the installable archive.
- Replace the root legacy `README` with a maintained Markdown `README.md`.
- Rewrite the 1.8 upgrade instructions around persistent media storage and the required 1.7.x pre-migration step.
- Remove obsolete Japanese documentation pending future community-maintained translation.
- Remove obsolete 1.6/1.7 installation/configuration guides and duplicated historical documentation.
- Replace the old 1.6-era public usage guide with a current MediaGallery 1.8.0 `public_html/docs/usage.html` guide.
- Document the public service/lifecycle interoperability contract in `docs/SERVICES.md`.

### Historical 1.8.0 validation checklist

- Complete the full live regression matrix on Geeklog 2.1.1 and 2.2.2.
- Complete live PHP 8.2/8.3 warning/deprecation validation.
- Validate disposable upgrades from MediaGallery 1.7.0 and 1.7.3.
- Complete remaining moderation, mail, MIME mismatch, stale-temp, service-permission and IndexNow integration tests.
- Decide whether `functions_legacy.inc` remains as the transitional implementation layer for the 1.8.0 RC.
- Build and validate the final release-candidate archive.

## 1.7.3

- Fixed remote media upload behavior.
- Added fixes for PHP 7 and PHP 8.1 compatibility.
- Fixed comment permission handling for MediaGallery items.

## Earlier releases

The repository history contains the complete legacy development record. The former changelog bundled with this repository was itself only an excerpt from the historical glFusion changelog and contained detailed entries primarily for the 1.6.x line.

Notable functionality introduced during the earlier MediaGallery line included:

- Geeklog `PLG_itemSaved()` integration;
- command-line batch imports;
- user/media ownership controls;
- member albums and profile integration;
- RSS/podcast support;
- album permissions and static sorting;
- random-media block enhancements;
- importer support for older gallery systems;
- historical Flash/QuickTime/Windows Media playback features that have now been retired from maintained 1.8 rendering.

For exact historical changes prior to 1.7.3, use the Git history and tagged releases rather than treating the previous excerpted changelog as a complete release record.
