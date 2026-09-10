# MediaGallery 1.8.0 Roadmap

MediaGallery 1.8.0 is a modernization release focused on configuration cleanup, multisite-safe media storage, current Geeklog compatibility, template modernization, SEO/accessibility improvements, and better interoperability with other Geeklog plugins.

The branch `modernize-1.8.0` is the working branch for this release. Implementation should preserve existing installations by default and avoid automatic media moves during upgrade.

## 1. Compatibility goals

- Keep upgrade compatibility with existing MediaGallery 1.7.x installations.
- Target Geeklog 2.1.1 through 2.2.2 where practical.
- Keep current Geeklog 2.2.2 behavior and PHP 8.1 support already present in 1.7.3.
- Audit for PHP 8.2/8.3 warnings and deprecated behavior before release.
- Do not reintroduce the removed legacy `config.php` file.
- Preserve existing database data and media locations unless an administrator explicitly changes the site storage configuration.

## 2. Multisite-aware media storage

### Goal

Allow one shared MediaGallery codebase to serve multiple Geeklog sites without sharing physical media storage.

### Site configuration

Geeklog already provides `$_CONF['path_images']`. MediaGallery 1.8.0 will optionally recognize a matching public URL supplied by the site configuration:

```php
$_CONF['images_url'] = $_CONF['site_url'] . '/images/SITE';
```

When both values are available:

```php
$_CONF['path_images']
$_CONF['images_url']
```

MediaGallery should derive:

```php
$_MG_CONF['path_mediaobjects'] = rtrim($_CONF['path_images'], '/\\') . '/mediagallery/';
$_MG_CONF['mediaobjects_url']  = rtrim($_CONF['images_url'], '/') . '/mediagallery';
```

When `images_url` is not defined, the historical MediaGallery location remains the default:

```text
public_html/mediagallery/mediaobjects/
```

and:

```text
{site_url}/mediagallery/mediaobjects
```

### Upgrade rules

- Never move existing media automatically during plugin upgrade.
- Never require `images_url` on standard Geeklog installations.
- Existing single-site installations must continue to work unchanged.
- Multisite installations can opt into site-specific storage only through their Geeklog site configuration.
- Remove hostname-specific logic from MediaGallery itself.
- Audit `tmp_path` and upload staging so shared multisite installations cannot unintentionally share temporary upload data.

## 3. Configuration API cleanup

The old MediaGallery `config.php` no longer exists in current code. Remaining administrator preferences hard-coded in `functions.inc` should be reviewed and moved to the Geeklog Configuration API where appropriate.

### Move to online configuration where still relevant

Candidates include:

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
- legacy `menulabel`, if still required by current navigation behavior
- advanced image-processing options from older releases when still used by current code

### Keep derived/internal values out of online configuration

Do not store the following as administrator-editable settings when they can be reliably derived:

- `path_html`
- `site_url`
- `admin_url`
- `path_admin`
- `path_mediaobjects`
- `mediaobjects_url`
- `template_path`
- plugin version metadata
- table mappings
- media format constants
- internal MIME/type maps

### Remove or replace obsolete options

Audit and remove options that only support obsolete technologies, including where no current code path still depends on them:

- Flash playback
- QuickTime-specific playback
- Windows Media Player-specific playback
- MooTools selection/loading
- SimpleViewer configuration
- old standalone version-check behavior

Do not migrate an old setting merely because it existed in `config.php`; first determine whether the current code still consumes it or whether a newer setting already replaces it.

### Upgrade migration

Add a 1.8.0 configuration migration routine that:

- adds only missing Configuration API entries;
- never resets existing administrator values;
- distinguishes an absent setting from valid false/zero values;
- maps legacy settings to current equivalents where appropriate;
- avoids duplicate semantic settings;
- leaves media paths derived at runtime rather than stored in the plugin configuration.

## 4. Template modernization

Audit all `.thtml` templates and template selection logic.

Goals:

- remove obsolete markup and table-based layout where it is only present for presentation;
- keep semantic tables where the content is genuinely tabular;
- use current HTML5 markup;
- improve responsive behavior;
- remove dependencies on obsolete JavaScript libraries and plugins;
- reduce inline styles and inline JavaScript where practical;
- use Geeklog theme/template facilities consistently;
- preserve compatibility with current Geeklog themes, including UIKit-based themes where supported;
- review all forms for labels, fieldsets, keyboard accessibility, CSRF handling and useful validation messages;
- ensure media controls and navigation are usable on mobile devices;
- keep template overrides possible without editing plugin core files.

Template modernization must not silently break existing album skins. Where a legacy skin cannot be retained safely, document its replacement or migration path.

## 5. SEO and discoverability

MediaGallery contains indexable album and media pages and should produce search-engine-friendly output without introducing duplicate-content problems.

Review and improve where needed:

- meaningful page titles for albums and individual media;
- one clear page heading hierarchy;
- descriptive image `alt` output based on available media title/description rather than filename-only fallbacks;
- canonical URLs for album/media pages where multiple navigation URLs can expose the same content;
- pagination handling and crawlable previous/next navigation;
- metadata/description output using Geeklog-supported page metadata mechanisms;
- XML Sitemap integration already supported by current releases;
- stable URLs and redirects when legacy URL forms are detected;
- avoid indexing administrative, upload, batch and transient views;
- structured data only where it accurately represents the content and does not duplicate or conflict with Geeklog core structured data;
- Open Graph/social metadata only through a consistent Geeklog-compatible mechanism if not already provided by the theme/core.

SEO changes must not invent metadata that the media record does not contain.

## 6. Accessibility

Treat accessibility as part of template modernization:

- valid form labels;
- keyboard-accessible navigation;
- visible focus states inherited from the active theme;
- useful alternative text;
- avoid JavaScript-only essential navigation;
- accessible previous/next controls;
- sensible heading hierarchy;
- accessible album/media action menus.

## 7. Interoperability and public API

Address the open proposal for a public member album tree service so other plugins do not need to query MediaGallery tables directly.

Target service concept:

```php
PLG_invokeService(
    'mediagallery',
    'album_list',
    array(
        'uid'       => $uid,
        'root'      => 'member',
        'recursive' => true,
        'visible'   => true
    ),
    $output,
    $svc_msg
);
```

The implementation should reuse MediaGallery permission and album-tree logic rather than exposing raw tables.

Potential consumers include Documents and future Geeklog connector/plugin integrations.

## 8. Email modernization

Address the open request to use Geeklog email templates for messages sent by MediaGallery.

Goals:

- use Geeklog-supported email template mechanisms;
- provide plaintext and HTML variants where supported;
- avoid hard-coded presentation inside PHP;
- preserve existing notification behavior and permissions;
- keep site name, site URL and sender configuration controlled by Geeklog.

## 9. Existing bug fixes to retain

The 1.8.0 branch must retain all fixes already present in 1.7.3, including recent upload, PHP 7/8.1, permissions and filename/thumbnail fixes inherited from the current branch history.

Before release, review all currently open MediaGallery issues and either:

- implement the issue;
- explicitly defer it in this roadmap;
- or close it only when the current code clearly already addresses it.

## 10. Code modernization

- Remove dead compatibility branches after confirming they are no longer needed by the supported Geeklog/PHP matrix.
- Replace obsolete PHP idioms that trigger PHP 8.x warnings/deprecations.
- Validate array keys and request values before access.
- Centralize storage path/URL resolution.
- Avoid direct reliance on `$_SERVER['HTTP_HOST']` for site identity.
- Prefer Geeklog APIs over direct duplication of core behavior.
- Keep permission checks close to every action that reads or mutates protected media.

## 11. Testing plan

Test at minimum:

### Standard installation

- Geeklog standard single-site layout.
- No `$_CONF['images_url']` defined.
- Existing `mediagallery/mediaobjects/` media remain accessible.
- Upload, edit, delete, thumbnail generation, RSS, search and comments.

### Multisite installation

- shared plugin code;
- separate database table prefixes or databases;
- separate `path_images` values;
- separate `images_url` values;
- verify media from Site A cannot be written into or served from Site B storage;
- verify temporary/upload directories are isolated where necessary.

### Upgrade

- upgrade from 1.7.0 and 1.7.3;
- configuration values preserved;
- no automatic media move;
- no duplicate configuration entries;
- existing URLs remain valid unless the administrator explicitly opted into a different site image URL.

### Runtime

- Geeklog 2.1.1 compatibility where retained;
- Geeklog 2.2.2;
- PHP versions in the final supported matrix, with PHP 8.3 included in the audit.

## 12. Proposed implementation order

1. Document 1.8.0 behavior and compatibility policy.
2. Refactor configuration loading and derived paths.
3. Implement multisite-aware media and temporary storage resolution.
4. Add Configuration API migration for remaining live options.
5. Remove confirmed obsolete configuration/code paths.
6. Modernize templates and JavaScript dependencies.
7. Improve SEO/accessibility output.
8. Implement public album service API.
9. Modernize email templates.
10. Complete PHP/Geeklog compatibility audit and regression tests.
11. Update installation/upgrade documentation and changelog.
12. Prepare 1.8.0 release candidate.

## Release principle

MediaGallery 1.8.0 should be easier to install, safer to upgrade, naturally usable in a Geeklog multisite environment, and configurable from Geeklog without restoring a manually edited plugin `config.php`.
