# MediaGallery 1.9.0 development notes

MediaGallery 1.9.0 extends the SEO/interoperability work introduced in 1.8.0 while keeping OGP optional.

## SEO and structured data

- Album pages now publish Schema.org `CollectionPage` JSON-LD with an `ItemList` for the items displayed on the current page.
- Media pages keep their content-aware `ImageObject`, `VideoObject` and `AudioObject` JSON-LD.
- Local media `contentUrl` and video `thumbnailUrl` values are normalized to absolute public URLs.
- Album and media pages now provide content-specific meta-description fallbacks instead of relying on the site's generic description when no dedicated description exists.

## Optional OGP integration

- When an active OGP plugin exposes `OGP_registerSocialMetadata()`, MediaGallery delegates Open Graph and Twitter/X metadata to OGP.
- Albums delegate title, description, canonical URL and a representative image when one is available.
- Media pages delegate title, description, canonical URL, media image and subtype metadata; video pages use `video.other`.
- When OGP is absent or an older OGP release is installed, MediaGallery renders equivalent Open Graph and Twitter/X metadata itself.
- MediaGallery remains authoritative for canonical URLs, descriptions and Schema.org structured data.

# MediaGallery 1.8.0 release notes

MediaGallery 1.8.0 is a major modernization and hardening release for Geeklog. It preserves the mature gallery feature set while updating storage, security, playback, administration, interoperability and compatibility for current Geeklog installations.

## Compatibility

- Geeklog 2.1.1 or newer, including Geeklog 2.2.2.
- PHP 5.6-compatible syntax for the Geeklog 2.1.1 transition line.
- Validation targets also include PHP 7.4, 8.1 and 8.3.
- Existing MediaGallery 1.7.x installations require the documented persistent-media pre-migration before the plugin ZIP upgrade.

## Highlights

- Persistent media storage outside the replaceable plugin public directory.
- Safer 1.7.x upgrades and shared-code multisite isolation.
- Upload, remote-media, FTP, ZIP, CLI, batch and moderation hardening.
- Responsive public/admin interfaces and improved accessibility.
- HTML5-first audio/video playback with obsolete Flash/ActiveX execution removed.
- Canonical URLs, descriptions and conservative media structured data.
- Geeklog-native moderator email through `COM_mail()`.
- Improved album thumbnails and portrait rendering.
- Reusable MediaGallery media picker and permission-filtered album/media discovery.

## Upstream issues addressed

MediaGallery 1.8.0 incorporates or supersedes the fixes tracked in the official Geeklog-Plugins/mediagallery issue tracker:

- [#4](https://github.com/Geeklog-Plugins/mediagallery/issues/4) — Add Media navigation works with Denim Three / UIkit-style navigation.
- [#5](https://github.com/Geeklog-Plugins/mediagallery/issues/5) — Remote Media no longer raises a `count()` warning when no categories exist.
- [#6](https://github.com/Geeklog-Plugins/mediagallery/issues/6) — MediaGallery mail now uses Geeklog's configured mail backend with HTML/plaintext templates for moderation and approval notifications.
- [#7](https://github.com/Geeklog-Plugins/mediagallery/issues/7) — comment enablement respects album and user read permissions.
- [#8](https://github.com/Geeklog-Plugins/mediagallery/issues/8) — upload `post_max_size` conversion uses the complete numeric value.
- [#9](https://github.com/Geeklog-Plugins/mediagallery/issues/9) — thumbnail paths remain correct for filenames containing multiple periods.
- [#10](https://github.com/Geeklog-Plugins/mediagallery/issues/10) — member album discovery is exposed through the public `album_list` service, with additional album/media read and collection services for interoperable consumers.
- [#11](https://github.com/Geeklog-Plugins/mediagallery/issues/11) — PHP 8.x compatibility work covers configuration bootstrap defaults, initialized media-view variables, administration paths including member-album purge, and broader PHP 8.1/8.3 runtime hardening.

Issue #11 also contains a defense-in-depth suggestion for web-server-level script execution protection in media storage. MediaGallery 1.8.0 instead enforces portable application-level executable-extension rejection and MIME/extension validation so deployments are not coupled to Apache-specific `.htaccess` directives.

## Geeklog interoperability

MediaGallery 1.8.0 exposes a shared, consumer-neutral capability contract for Agent, Eclipse, Hub and future integrations.

Current declared capabilities include:

```text
content.read
content.collection
content.search
content.url.resolve
content.lifecycle
dashboard.summary
media.album.list
media.album.read
media.item.read
media.item.collection
```

The plugin provides bounded read-only services for album lists, album reads, media collections, media reads and administration dashboard summaries. Consumers no longer need to know MediaGallery table names or storage paths.

Album lifecycle identifiers use the portable `album:<id>` namespace, while historical media IDs remain unchanged. Save/delete events continue through Geeklog's native lifecycle API so IndexNow, XML Sitemap, Hub and future consumers can react without MediaGallery depending on them.

## Eclipse dashboard support

The `dashboard_summary` service can expose, subject to MediaGallery administration rights:

- album count;
- media count;
- pending moderation count;
- storage-writability alerts;
- pending-moderation alerts;
- the MediaGallery administration link.

This follows the shared Geeklog memorandum dashboard contract rather than an Eclipse-specific API.

## Agent and Hub support

Permission-filtered `album_read` and `media_read` services expose normalized identities, subtypes, canonical URLs, descriptions, dates, ownership and relevant media metadata. The existing Item Info/search/lifecycle APIs remain part of the same interoperability surface.

## Important upgrade note

Before replacing a MediaGallery 1.7.x installation with the 1.8.0 ZIP, migrate legacy media out of:

```text
public_html/mediagallery/mediaobjects/
```

using the supplied migration tool and confirm that the copy/verification succeeds. See `UPGRADE` for the complete procedure.

## Validation

The 1.8.0 release has been validated across the supported transition matrix, including Geeklog 2.1.1 and Geeklog 2.2.2, upgrades from MediaGallery 1.7.3 and 1.7.0, persistent-storage migration, batch security, moderation, Geeklog-native mail, representative playback/fallback paths, and the Agent/Eclipse/Hub interoperability services.

The release archive is generated from the validated `modernize-1.8.0` source and checked for PHP syntax compatibility on PHP 5.6, 7.4, 8.1 and 8.3.
