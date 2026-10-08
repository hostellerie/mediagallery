# MediaGallery 2.0.0 for Geeklog

MediaGallery is a full-featured media gallery plugin for Geeklog. The `mediagallery_2.0.0` branch is the release line for MediaGallery 2.0.0 and builds on the modernization completed in 1.8.0 and the compatibility/interoperability work completed in 1.9.0.

> **Release status:** MediaGallery 2.0.0 is in active release validation for Geeklog 2.1.1 through 2.2.2. Keep complete database and media backups before upgrading an existing production site.

## Compatibility target

- Geeklog **2.1.1 or newer**, including Geeklog 2.2.2
- PHP **5.6 or newer**; syntax validation covers PHP 5.6, 7.4, 8.1 and 8.3

MediaGallery 2.0.0 preserves the transition compatibility policy introduced in 1.8.0 so existing Geeklog 2.1.1 sites can upgrade before or alongside a Geeklog core migration.

## What 2.0.0 includes

MediaGallery 2.0.0 carries forward the 1.8.0 modernization and 1.9.0 compatibility work, with the current interoperability, sitemap and SEO improvements. The maintained feature set includes:

- persistent media storage outside the replaceable plugin public directory;
- safer upgrades from existing 1.7.x installations;
- shared-code multisite isolation using Geeklog's configured paths and URLs;
- upload, FTP, ZIP, CLI and remote-media security hardening;
- modern HTML5 audio/video behavior and removal of active Flash/ActiveX playback;
- responsive album, media, search and administrative interfaces;
- accessibility, canonical URL, meta-description and structured-data improvements;
- Geeklog-native `COM_mail()` moderator notifications;
- a read-only album discovery service through `PLG_invokeService()`;
- generic album/media lifecycle events for IndexNow, XML Sitemap, Hub and other Geeklog consumers;
- improved album thumbnail sharpness and portrait-image rendering;
- Geeklog 2.1.1-compatible PHP-block and batch-session fixes.
- 13 maintained UTF-8 translations synchronized with the current English language contract: Spanish, Italian, Japanese, Russian, Chinese (Simplified), Chinese (Traditional), Hebrew, Persian, French Canada, French France, German, German Formal and Spanish Argentina.

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for 2.0.0 changes and [ROADMAP.md](ROADMAP.md) for the broader implementation record.

## Persistent media storage

MediaGallery 1.8.0 stores public media below Geeklog's image root instead of inside `public_html/mediagallery/`.

The runtime path is derived from:

```php
$_CONF['path_images'] . 'mediagallery/'
```

and the public URL uses Geeklog's configured image URL root (`images_url` when explicitly configured).

A typical single-site installation therefore uses:

```text
/path/to/geeklog/public_html/images/mediagallery/
https://example.com/images/mediagallery/
```

A shared-code multisite installation can give each site its own image root, for example:

```php
$_CONF['path_images'] = $_CONF['path'] . 'public_html/images/site-a/';
$_CONF['images_url']  = $_CONF['site_url'] . '/images/site-a';
```

MediaGallery then stores that site's media below:

```text
public_html/images/site-a/mediagallery/
```

Private temporary/upload working data is likewise derived from each site's Geeklog `path_data`.

## Important: upgrading a 1.7.x site

Older MediaGallery installations may still store user media in:

```text
public_html/mediagallery/mediaobjects/
```

Geeklog's plugin ZIP updater replaces the plugin's public directory before MediaGallery's upgrade code can run. Therefore **do not upload a 1.8.0-or-newer ZIP over a 1.7.x installation until legacy media have been pre-migrated**.

Extract the target MediaGallery package on the server and run:

```bash
php tools/migrate-media-storage.php /path/to/geeklog
```

The tool copies the existing media into the persistent Geeklog image location, verifies the copied files and deliberately leaves the legacy source untouched.

Only proceed with the plugin ZIP upgrade after the tool reports a successful migration.

## Image-processing requirement

Image uploads require a working image-processing backend because MediaGallery creates thumbnails and display images.

MediaGallery uses Geeklog's configured `$_CONF['image_lib']` backend:

- `gdlib` — PHP GD must be installed and enabled;
- `imagemagick` — the configured ImageMagick tools must be executable;
- `netpbm` — the configured NetPBM tools must be executable.

MediaGallery checks backend availability before resize, conversion, rotation and watermark operations and returns a clear error when the configured backend is unavailable.

Non-image media such as PDF/ZIP files may not require image conversion.

## Security foundation introduced in 1.8.0

The modernization branch hardens the main mutation and import paths, including:

- Geeklog CSRF protection on normal browser mutation entry points;
- server-side album/media ownership and membership revalidation;
- safe filename and MIME/extension checks;
- FTP path confinement;
- ZIP traversal/symlink/payload protections;
- recursive CLI symlink rejection;
- bounded public HTTP(S) remote media retrieval;
- stale temporary-file cleanup;
- moderation queue approval/rejection validation.

### Batch processing on Geeklog 2.1.1

Geeklog 2.1.1 security tokens are one-time and referer-bound. MediaGallery therefore keeps the normal token on the operation that starts a batch, but internal `batch.php` continuation is protected by:

- POST-only requests;
- a server-generated batch `session_id`;
- an existing batch session record;
- ownership validation against the logged-in user (with the existing administrator override).

This avoids false “security token expired” failures during multi-step batch processing without making the batch session publicly callable.

## Modern public output

The maintained MediaGallery templates include:

- responsive CSS Grid/Flexbox album and media layouts;
- semantic headings and navigation landmarks;
- accessible form labels and controls;
- modern lightbox/slideshow interaction;
- HTML5 audio/video rendering and safe download fallbacks;
- canonical URLs for media and paginated albums;
- editorial meta descriptions where source descriptions exist;
- conservative `ImageObject`, `AudioObject` and eligible `VideoObject` JSON-LD;
- sharper album thumbnails by preferring original local images as the visual source when available.

## Geeklog interoperability

### Shared capability discovery

MediaGallery declares provider-neutral capabilities for Agent, Eclipse, Hub and future Geeklog consumers. It exposes bounded read-only album/media services and an administration `dashboard_summary` service, while keeping MediaGallery permissions authoritative and avoiding direct consumer access to `mg_*` tables.

### Generic media collection for content consumers

On the `mediagallery_2.0.0` development branch, the existing
`plugin_getiteminfo_mediagallery()` callback also supports a permission-aware
`id='*'` media collection with `since`, `limit` and `order`.

This allows generic consumers such as Hello to discover MediaGallery media
without direct SQL. The normalized result can expose IDs, titles, URLs,
excerpts, timestamps, type/subtype and thumbnail images. Albums remain
addressable separately with the existing `album:<id>` namespace.


### Album discovery

Other Geeklog plugins can request permitted album trees through the native service API instead of querying `mg_*` tables directly:

```php
$output = array();
$svc_msg = array();

$status = PLG_invokeService(
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

See [docs/SERVICES.md](docs/SERVICES.md) for the service contract.

### Album and media lifecycle events

MediaGallery reports content changes through Geeklog's standard plugin lifecycle APIs rather than calling IndexNow or another consumer directly.

Existing media IDs remain unchanged. Album IDs use a namespaced form:

```text
album:52
```

MediaGallery emits save/delete events for albums and media, and also reports affected album pages when media are added, edited, deleted, reordered or moved.

This allows IndexNow 1.3.0, XML Sitemap, Hub and future connectors to react through Geeklog's plugin API without depending on MediaGallery's database schema.

## Configuration

MediaGallery does not restore the old manually edited MediaGallery `config.php` model.

Administrator preferences stay in Geeklog's Configuration API where appropriate. Runtime-derived values such as plugin URLs, template paths and storage paths are calculated from the active Geeklog site configuration.

Obsolete Flash/FlowPlayer controls are no longer created on fresh installations. Legacy rows may remain harmlessly in upgraded databases until deletion has been validated across the supported upgrade matrix.

## Distribution

The release branch produces one installable archive:

```text
dist/mediagallery_1.9.0_2.1.1.zip
```

The archive contains one top-level `mediagallery/` directory and excludes repository/build-only content. Automated validation checks PHP syntax, required MediaGallery helpers, public item-display contracts and Geeklog-compatible archive filenames.

The archive is rebuilt automatically from validated source changes and is the package intended for the 1.9.0 release.

## Documentation

Current 1.8 documentation:

- [ROADMAP.md](ROADMAP.md) — implementation and validation status;
- [TESTING-1.8.md](TESTING-1.8.md) — live regression checklist;
- [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) — design/implementation notes;
- [docs/SERVICES.md](docs/SERVICES.md) — public Geeklog service/lifecycle integration;
- [docs/README.md](docs/README.md) — documentation inventory and legacy-document status.

Some historical MediaGallery documents are still present for reference but describe much older releases. They must not be used as 1.8 install/upgrade instructions unless explicitly marked current.

## License

MediaGallery is distributed under the GNU General Public License v2 (GPLv2). Historical copyright notices remain in the source files inherited from the original MediaGallery/glFusion codebase.


### Generic album candidates

MediaGallery 2.0.0 can expose both albums and individual media items through its
generic content collection. Existing consumers remain media-only unless they
request the `album` subtype explicitly. Albums use stable `album:<id>`
identifiers and MediaGallery remains responsible for visibility and permission
filtering.
