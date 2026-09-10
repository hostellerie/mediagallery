# MediaGallery 1.8.0 Implementation Notes

This file tracks implementation decisions made while modernizing the plugin.

## Implemented in the first 1.8.0 batch

- Created a transitional 1.8.0 bootstrap in `functions.inc`.
- Preserved the complete 1.7.3 implementation as `functions_legacy.inc` while modernization is introduced incrementally.
- Added `include/config_180.php` for 1.8.0 runtime configuration and Configuration API migration.
- Added explicit upgrade support from known 1.7.x identifiers, including 1.7.0 and 1.7.3.
- Bumped the development plugin version to 1.8.0 through the runtime/bootstrap and autoinstall metadata.
- Added optional multisite storage based on `$_CONF['path_images']` + `$_CONF['images_url']`.
- Preserved the historical `mediagallery/mediaobjects/` location when `images_url` is absent.
- Isolated multisite temporary and FTP/upload staging paths under site-specific `$_CONF['path_data']` when available.
- Added idempotent Configuration API migration for live settings that were previously hard-coded.
- Added English fallback labels for the new configuration entries until translation files are updated.
- Modernized the main album template with a semantic H1, nav elements and a more accessible search control.

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

This prevents sites sharing one plugin code tree from sharing temporary upload data.

The plugin still needs a dedicated directory check/creation step before release so an administrator gets a clear error instead of an upload failure when these directories do not exist or are not writable.

## Configuration API migration

The first batch adds these previously hard-coded settings when missing:

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

## Template / SEO work started

`templates/album_page.thtml` now uses a semantic album `<h1>` and navigation landmarks. The next template/SEO batch should:

- pass the album title to `MG_createHTMLDocument()` as the page title;
- review individual media page headings and titles;
- review alt text generation in media and album thumbnails;
- move remaining inline presentation CSS into plugin stylesheets where safe;
- audit obsolete audio-player/SWF/legacy JavaScript includes before removal;
- review canonical URL and pagination behavior through Geeklog-supported header metadata.

## Required tests before merging

- Upgrade an actual 1.7.0 installation.
- Upgrade a 1.7.3 installation.
- New 1.8.0 installation.
- Geeklog 2.1.1 and 2.2.2 Configuration API behavior.
- Multisite with separate table prefixes/databases and separate `path_images` / `images_url` / `path_data`.
- Standard site with no `images_url` to confirm legacy media paths remain unchanged.
- Verify `tmp` and `uploads` directory existence/writability handling.
- Verify all added configuration controls display and save correctly.
- PHP 8.1 and PHP 8.3 warning/deprecation pass.
