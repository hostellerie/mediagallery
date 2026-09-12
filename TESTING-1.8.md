# MediaGallery 1.8.0 online test checklist

Use the installable archive in `dist/mediagallery_1.8.0_2.1.1.zip` only after the distribution workflow has rebuilt it from the current `modernize-1.8.0` branch.

## Fresh installation

Test on Geeklog 2.1.1 and 2.2.2 where available.

- Install MediaGallery 1.8.0 through the standard plugin installer.
- Open the MediaGallery Configuration page.
- Confirm there is no FlowPlayer option and no Flash Media configuration tab.
- Confirm the remaining MP3/MOV/ASF controls load without PHP warnings.
- Confirm MediaGallery public pages load before any media is uploaded.

## Image upload and DNC

Use small PNG, GIF, BMP and JPEG samples.

### DNC disabled

With `discard_original = 0` and **Do not convert original to JPG** unchecked:

- upload PNG/GIF/BMP;
- confirm upload completes without warning;
- confirm the retained original is a real JPEG file;
- confirm its stored extension is `.jpg` and MediaGallery records JPEG MIME data;
- confirm thumbnail and display images render normally.

### DNC enabled

With **Do not convert original to JPG** checked:

- upload PNG/GIF/BMP;
- confirm the original retains its source format and extension;
- confirm thumbnail and display images render normally.

### Discard original

With `discard_original = 1`, repeat one PNG/JPEG upload and confirm no orphan original or incorrect MIME record is created.

## Legacy media playback

- Open an existing MP3/WMA media item and verify HTML5 audio playback/fallback.
- Exercise MP3 popup, download and MMS/legacy modes and confirm no undefined thumbnail-size warning appears.
- Open MOV/MP4/MPEG media inline and verify HTML5 video rendering.
- Exercise MOV/ASF popup and download modes and confirm no `media_size_disp` warning appears.
- Open existing SWF and FLV items and verify they are offered through the generic download fallback without Flash/FlowPlayer execution or PHP warnings.
- Test an old `fslideshow.php` URL and an existing `fslideshow` autotag.

## Upload security

- Browser upload with a valid CSRF token succeeds.
- Missing/invalid CSRF submission is rejected.
- Four simultaneous upload slots preserve their own title, description, keywords, category, attached-thumbnail and DNC values.
- Executable/double-extension test names are rejected.
- FTP import accepts a file inside configured `ftp_path` and rejects a forged outside path or escaping symlink.
- Remote Media accepts a normal public HTTP(S) thumbnail and rejects localhost/private/reserved targets.

## Persistent media storage

On a standard single-site installation:

- confirm `path_mediaobjects` resolves below `public_html/images/mediagallery/`;
- upload an image and confirm `orig`, `disp` and `tn` files are created there;
- re-upload the same MediaGallery 1.8.0 plugin ZIP and confirm the existing image remains intact;
- confirm placeholder/type assets such as `missing.png` and `generic.png` are present in persistent storage.

On a shared-code installation with site-specific `path_images`, `images_url` and `path_data`:

- confirm each site resolves its own `mediagallery` media path and URL;
- confirm `tmp` and FTP/upload staging directories are site-specific;
- confirm uploads on one site do not appear in another site's storage.

## Upgrade from 1.7.x

On disposable copies only:

- back up the database and `public_html/mediagallery/mediaobjects/`;
- extract the 1.8.0 package without installing it;
- run `php tools/migrate-media-storage.php /path/to/geeklog`;
- confirm the tool reports all source files verified in the persistent destination and leaves the source untouched;
- only then upload the 1.8.0 ZIP through Geeklog;
- test both MediaGallery 1.7.0 and 1.7.3 sources;
- confirm existing albums/media remain accessible from the new images storage;
- confirm existing administrator settings are preserved;
- confirm re-running the migration is idempotent;
- create a conflicting destination file with a different size and confirm migration fails without overwriting it;
- confirm a site containing only remote-media records does not falsely require local media files;
- confirm obsolete Flash/FlowPlayer configuration rows, if still present in the database, do not affect the 1.8 runtime.

Record PHP warnings/notices together with the Geeklog version, PHP version, action performed and relevant MediaGallery settings.
