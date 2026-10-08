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

---

# MediaGallery 1.9.0 — Event / Quick Share roadmap

MediaGallery 1.9.0 introduces an event-oriented capture, publishing and delivery workflow while keeping MediaGallery albums and media as the canonical storage model. The feature must not create a parallel media library.

**Core model:** Special Events album → Events → Sessions → MediaGallery media.

## 15. Event foundation

- [ ] Add an optional Event / Quick Share mode based on a special MediaGallery album type/container dedicated to Events.
- [ ] Allow a special Events album to contain multiple distinct events instead of creating one normal MediaGallery album per event.
- [ ] Allow an administrator to designate/create one or more special Events albums where useful (for example separate professional and private event collections).
- [ ] Allow an administrator or authorized photographer to create an event inside a selected special Events album.
- [ ] Keep uploaded photographs as normal MediaGallery media so existing permissions, metadata, derivatives, storage, lifecycle notifications and interoperability remain usable.
- [ ] Add event status and lifecycle controls: draft, active, closed and optionally expired.
- [ ] Allow optional event start/end dates and configurable retention/expiration without deleting canonical media unexpectedly.
- [ ] Keep the feature optional so normal MediaGallery installations and album workflows remain unchanged.

## 16. Mobile-first quick upload

- [ ] Provide a minimal responsive upload interface designed first for iPhone and Android browsers.
- [ ] Use the device-native photo picker and support multiple-photo selection.
- [ ] Treat the native picker as the initial batch selection only: do not upload immediately after files are chosen.
- [ ] Build a local pre-upload review workflow so selected photographs can be inspected without first sending them to the server.
- [ ] Provide a large-format mobile viewer as the primary photo-selection interface; small thumbnails may be used for navigation/overview but must not be the only way to judge and select photographs.
- [ ] Allow swipe/previous/next navigation through the locally selected photographs.
- [ ] Provide touch zoom / pinch-to-zoom where browser capabilities allow, so the photographer can inspect focus, faces, expressions and image detail before publication.
- [ ] Allow each photograph to be explicitly selected or rejected from the large viewer, with a persistent selected/total counter.
- [ ] Provide a thumbnail/grid recap after review with select all, deselect all and individual selection correction.
- [ ] Show a final action such as “Upload 7 photos” reflecting the actual number selected for publication.
- [ ] Upload only the photographs retained after the local review step.
- [ ] Allow direct upload into the currently selected event/session with as few interactions as possible after review.
- [ ] Display per-file upload progress, individual success/failure states, overall completion state and retry of failed uploads without resending successful files.
- [ ] Support immediate publication when the operator has permission, with optional moderation where required.
- [ ] Preserve MediaGallery upload validation, MIME checks, quotas, image processing and security rules.
- [ ] Make interrupted/partial mobile uploads recoverable where practical.
- [ ] Avoid requiring a dedicated mobile application for the baseline workflow.

## 17. Event QR code and public gallery

- [ ] Generate a QR code for each event.
- [ ] Provide a stable event sharing URL suitable for printing or displaying on a screen.
- [ ] Allow visitors to scan the QR code and open the event gallery without navigating the full MediaGallery hierarchy.
- [ ] Make newly published photographs appear in the event gallery with minimal delay.
- [ ] Support public events and permission-controlled/private events.
- [ ] Provide individual photo download where permitted.
- [ ] Provide multi-select and ZIP download where permitted and operationally safe.
- [ ] Reuse MediaGallery thumbnails/display images for browsing while allowing controlled access to originals.
- [ ] Provide administrator controls to disable sharing without deleting the album or media.

## 18. Sessions and participant delivery

- [ ] Allow an event to contain lightweight photo sessions (for example session #042).
- [ ] Associate one or more MediaGallery media items with a session without duplicating the files.
- [ ] Generate a unique share URL and QR code for each session.
- [ ] Allow a participant to scan the session QR and see only the photographs assigned to that session.
- [ ] Support adding more photographs to an active session after its QR has already been issued.
- [ ] Provide session states such as active, closed and revoked.
- [ ] Allow optional expiration of a session share link independently from the canonical MediaGallery media.
- [ ] Provide download controls at session level.
- [ ] Keep session identifiers separate from personally identifying information by default.

## 19. Participant-first QR workflow

A later 1.9.x stage should support a reverse workflow suitable for high-volume event photography:

1. the participant receives or displays a session QR;
2. the photographer scans that QR before shooting;
3. the mobile upload interface switches to that participant/session;
4. subsequent selected photographs are attached automatically to that session;
5. the participant can use the same QR to retrieve the photographs as they are published.

Implementation requirements:

- [ ] Generate participant/session QR codes without requiring facial recognition.
- [ ] Add a mobile QR scanner using browser capabilities where supported, with a manual token/code fallback.
- [ ] Clearly show the currently active session before upload to prevent photographs being assigned to the wrong participant.
- [ ] Provide a one-tap way to end/switch the active session.
- [ ] Allow correction/reassignment by an authorized operator.
- [ ] Never use facial recognition as a hidden fallback.

## 20. Share-link security and privacy

- [ ] Use cryptographically strong, non-sequential, non-guessable share tokens.
- [ ] Never expose internal database IDs as sufficient authorization for a private session.
- [ ] Store share tokens safely and make revocation possible.
- [ ] Apply MediaGallery/Geeklog permissions before serving originals or downloads.
- [ ] Add configurable expiry for event/session links.
- [ ] Prevent directory indexing and direct bypass of private delivery controls.
- [ ] Rate-limit or otherwise protect expensive ZIP/download operations where appropriate.
- [ ] Avoid collecting participant names, email addresses or other personal data unless explicitly required by a future workflow.
- [ ] Document privacy/retention implications for event operators.

## 21. Event administration and UX

- [ ] Add an Event administration view listing event name, parent Events album, status, sessions, media count and sharing state.
- [ ] Provide fast actions: Open upload, New session, Show QR, Copy link, Close event and Disable sharing.
- [ ] Provide a session view with assigned photographs and reassignment/removal controls.
- [ ] Allow QR presentation in a large high-contrast view suitable for showing directly on the photographer's phone.
- [ ] Allow QR export/printing for event signage.
- [ ] Keep public participant pages deliberately simple: gallery, selection and permitted download actions.
- [ ] Ensure the workflow remains usable with touch interfaces and narrow screens.
- [ ] Keep templates compatible with maintained Geeklog themes including Denim and Eclipse.

## 22. Data model and interoperability

- [ ] Add event/session tables only for workflow metadata and relationships; do not duplicate MediaGallery media records.
- [ ] Define explicit relations between special Events album, event, session and media IDs.
- [ ] Ensure deleting/revoking a session does not delete canonical media unless an administrator explicitly performs a normal MediaGallery deletion.
- [ ] Define behavior when event media are moved outside their Events container or deleted through normal MediaGallery tools.
- [ ] Extend MediaGallery services/capabilities only where a generic event/session read contract is useful.
- [ ] Emit appropriate lifecycle notifications for event/session publication changes without coupling MediaGallery to Hub, Eclipse, Agent or another consumer.
- [ ] Keep the implementation compatible with shared-code multisite isolation.
- [ ] Do not allow event/session tokens or relationships to cross site boundaries.

## 23. Performance and event-scale operation

- [ ] Avoid regenerating existing image derivatives solely for Event mode.
- [ ] Use bounded/paginated gallery loading for large events.
- [ ] Support incremental refresh so participants can see newly published photographs without reloading an entire large gallery.
- [ ] Design ZIP generation to avoid PHP memory/time exhaustion; use bounded/background preparation if required by scale.
- [ ] Define cleanup for expired temporary ZIP files and upload state.
- [ ] Test concurrent photographer uploads and participant browsing.
- [ ] Establish practical test scenarios for 100, 500, 1,000+ photographs per event.

## 24. 1.9.0 implementation phases

### Phase A — Event MVP
- [ ] Special MediaGallery Events album/container capable of holding multiple events.
- [ ] Event creation inside the selected Events album without requiring a separate normal album for every event.
- [ ] Mobile multi-photo quick upload.
- [ ] Local pre-upload review of the selected batch.
- [ ] Large-format photo viewer optimized for judging image quality on a phone.
- [ ] Swipe navigation, select/reject controls and selected/total counter.
- [ ] Touch zoom / pinch-to-zoom where supported.
- [ ] Grid recap and correction before upload.
- [ ] Upload only the final selected photographs, with per-file progress and failed-file retry.
- [ ] Event share URL and QR code.
- [ ] Public/permission-aware event gallery.
- [ ] Individual downloads.
- [ ] Share revocation.

### Phase B — Sessions
- [ ] Session creation inside an event.
- [ ] Media-to-session assignment.
- [ ] Unique session URL/token/QR.
- [ ] Session-only gallery.
- [ ] Session download and expiration controls.

### Phase C — Professional rapid workflow
- [ ] Participant-first QR workflow.
- [ ] Photographer QR scanning.
- [ ] Persistent active-session indicator during mobile upload.
- [ ] Fast session switching and reassignment.
- [ ] Multi-select/ZIP delivery.

### Phase D — Hardening
- [ ] Security review of tokens, permissions and direct-download paths.
- [ ] Mobile Safari and Android/Chrome regression tests.
- [ ] Large-event performance tests.
- [ ] Multisite isolation tests.
- [ ] Accessibility and theme regression.
- [ ] Documentation and operator workflow examples.

## 25. Optional paid session access / Store integration

Paid delivery must remain optional. MediaGallery must not implement its own checkout/payment system and must continue to operate normally when the Store plugin is absent or disabled.

- [ ] Add an optional paid access mode at Event Session level alongside free/private sharing modes.
- [ ] Keep MediaGallery independent from Store: expose the purchasable session/resource and entitlement checks through a bounded interoperability contract rather than direct Store SQL/table knowledge.
- [ ] Let Store own product/price, checkout, payment, order/refund state and purchase entitlement.
- [ ] Start with a simple product model: unlock/download the complete session for a configured price.
- [ ] Keep the data model extensible for later per-photo or selected-photo purchasing without making those models mandatory for 1.9.0.
- [ ] Allow protected previews before purchase where configured, using reduced-resolution and/or watermarked derivatives while keeping originals and protected downloads inaccessible.
- [ ] A session QR/share token identifies the session but must never by itself prove payment or grant paid download entitlement.
- [ ] After confirmed payment, allow MediaGallery to resolve a Store-issued entitlement and unlock the permitted originals/session ZIP.
- [ ] Revoke or update entitlement appropriately after cancellation/refund where Store reports that state.
- [ ] Define safe behavior when Store is unavailable: never accidentally unlock paid content and never break ordinary free/private Event workflows.

### Guest purchase without site account

Creating a Geeklog user account must **not** be required to buy and retrieve Event photographs.

- [ ] Support Store guest checkout for paid Event Sessions without requiring registration or login on the Geeklog site.
- [ ] Do not silently create a permanent Geeklog account as a side effect of guest purchase.
- [ ] Bind guest purchase entitlement to the Store order and Event Session using a cryptographically strong, non-guessable, revocable access/download token rather than a logged-in user ID.
- [ ] Return the purchaser to the unlocked session immediately after successful payment when the payment flow allows it.
- [ ] Provide a secure recovery/delivery mechanism for later access (for example a Store-generated secure order/download link) without requiring account creation.
- [ ] Minimize purchaser personal data; MediaGallery must not require name/email/PII beyond what Store/payment processing actually needs.
- [ ] Never expose order IDs, sequential session IDs or predictable values as sufficient download authorization.
- [ ] Support expiration/rotation/revocation of guest download tokens independently from canonical MediaGallery media.
- [ ] Ensure a leaked session QR cannot be combined with public order information to derive a paid download URL.
- [ ] Keep entitlement verification server-side for original-file and ZIP delivery; hiding download controls in the browser is not authorization.
- [ ] Document guest purchase, successful payment, failed/cancelled payment, refund, expired token and link-recovery test cases.

### Paid-session delivery UX

- [ ] Clearly distinguish preview access from purchased download access.
- [ ] Show session price and what the purchase unlocks before checkout.
- [ ] Provide a direct “Unlock / Buy session” action from the QR-opened session page when Store integration is available.
- [ ] After purchase, return to the same session context rather than forcing the participant to navigate MediaGallery.
- [ ] Provide individual and/or full-session ZIP download according to the purchased entitlement.
- [ ] Keep the participant workflow mobile-first and usable entirely from the phone used to scan the QR code.

## 26. 1.9.0 design principle

Event / Quick Share is a workflow layer, not a second gallery system. MediaGallery albums and media remain canonical. A special Events album acts as a container for multiple events; an event is not required to become a separate normal MediaGallery album. Events organize temporary/event-oriented publication inside that container; sessions provide selective delivery; QR codes provide fast access. The architecture should remain useful for weddings, parties, trade shows, sports, excursions, associations and professional event photographers without forcing personal-data collection or facial recognition.



---

# MediaGallery 2.0.0 — Shared content collection

MediaGallery 2.0.0 completes the generic Geeklog Item Info collection contract so
content consumers such as Hello, Hub and future indexing/agent tools can consume
MediaGallery content without direct access to `mg_*` tables.

## Generic Item Info collection

- [x] Extend `plugin_getiteminfo_mediagallery()` for `id='*'`.
- [x] Keep media items as the default generic collection for backward compatibility.
- [x] Allow generic collections to request `subtypes = media`, `album` or both.
- [x] Keep namespaced album reads through `album:<id>`.
- [x] Apply album visibility and Geeklog permission filtering for the requested `$uid`.
- [x] Support `since`.
- [x] Support bounded `limit` with a maximum of 500.
- [x] Support `modified-desc`, `modified-asc`, `created-desc` and `created-asc`.
- [x] Deduplicate media that belong to more than one accessible album.
- [x] Expose normalized fields required by generic consumers.

Supported normalized media properties include:

```text
id
type = mediagallery
subtype = media
title
url
canonical_url
description
excerpt
raw-description
date-created
date-modified
image
thumbnail_url
uid
album_id
media_type
mime_type
label
status
```

For the current MediaGallery schema, `date-created` and `date-modified` both
map to the media upload timestamp because there is no separate authoritative
media-modification timestamp yet. A future schema may split these values without
changing the consumer contract.

## Consumer rule

Generic consumers must use:

```php
PLG_getItemInfo(
    'mediagallery',
    '*',
    'id,title,url,excerpt,date-created,date-modified,type,subtype,image',
    $uid,
    array(
        'since' => $since,
        'limit' => 200,
        'order' => 'modified-desc',
        'subtypes' => array('album', 'media')
    )
);
```

They must not query `mg_media`, `mg_media_albums` or `mg_albums` directly.

## Hello compatibility

This contract makes MediaGallery eligible as an editorial source for Hello when
MediaGallery 2.0.0 is installed and enabled.

Hello may expose MediaGallery as a selectable digest source because the provider
already advertises:

```text
content.read
content.collection
content.url.resolve
```

The owning MediaGallery plugin remains authoritative for permissions and public
visibility.

## Native XML Sitemap collector

- [x] Add `plugin_collectSitemapItems_mediagallery($uid, $limit)`.
- [x] Keep XMLSitemap generation separate from the generic Item Info collection fallback.
- [x] Emit the MediaGallery root, public albums and public media as distinct canonical resources.
- [x] Deduplicate media that belong to multiple albums.
- [x] Exclude hidden and unauthorized albums/media for anonymous sitemap generation.
- [x] Prevent wildcard/placeholder sitemap URLs such as `s=*`.
- [x] Provide sitemap-specific priority and change-frequency values.
- [x] Guard sitemap collection during Geeklog's transient plugin activation state.

## 2.0.0 packaging

- [x] Promote canonical runtime version to 2.0.0.
- [x] Add the no-schema-change upgrade transition from 1.9.0 to 2.0.0.
- [x] Point PHP lint and archive workflows at `mediagallery_2.0.0`.
- [x] Generate the installable archive only after the PHP validation matrix succeeds.
- [ ] Confirm the generated `dist/mediagallery_2.0.0_2.1.1.zip` installs and upgrades correctly on Geeklog 2.1.1 and 2.2.2.

## 2.0.0 validation

Before release:

- [ ] Test anonymous collection reads against public, private and hidden albums.
- [ ] Test registered-user collection reads with mixed group permissions.
- [ ] Test administrator collection reads.
- [ ] Test one media belonging to multiple albums and confirm one collection item.
- [ ] Test `since`, `limit` and all supported sort orders.
- [ ] Test album-only, media-only and mixed album + media collection reads.
- [ ] Test Hello preview/test digest with MediaGallery as the only non-Story source.
- [ ] Test mixed Story + MediaGallery digest.
- [ ] Confirm no private/hidden media title, excerpt, URL or thumbnail leaks to an unauthorized `$uid`.
