# MediaGallery 1.8.0 Implementation Notes

This file tracks implementation decisions made while modernizing the plugin.

## Configuration loading

- Keep only internal/runtime constants hard-coded in `functions.inc`.
- Load administrator preferences from the Geeklog Configuration API.
- Compute derived paths after configuration is loaded.
- Do not restore the historical `config.php` file.

## Media storage

- Standard installations keep `public_html/mediagallery/mediaobjects/`.
- If both `$_CONF['path_images']` and `$_CONF['images_url']` are defined, use the site-specific image root and append `/mediagallery/`.
- Never derive site identity from `HTTP_HOST` inside MediaGallery.
- Never move existing media automatically during upgrade.

## Temporary storage

The legacy `tmp_path` can be shared in a shared-code multisite installation. 1.8.0 must isolate temporary work when a site-specific image root is active, while preserving the old location for standard installations.

## Upgrade policy

New Configuration API entries must be added only when missing. Existing administrator values must never be reset by the 1.8.0 upgrade.
