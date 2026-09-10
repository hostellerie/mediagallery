# Distribution archives

Installable MediaGallery test archives generated from `modernize-1.8.0` are committed directly in this directory by the GitHub Actions workflow **Build MediaGallery installable archive**.

To request a new archive, update `.github/dist-trigger` (or run the workflow manually with `workflow_dispatch`). The workflow builds the current `modernize-1.8.0` HEAD and creates:

```text
dist/mediagallery-1.8.0-test-<short-sha>.zip
dist/mediagallery-1.8.0-test-<short-sha>.zip.sha256
```

The ZIP contains a single top-level `mediagallery/` directory suitable for plugin installation/testing. The build verifies required plugin files, generic MediaGallery assets and the SHA-256 checksum before committing the archive.

Only the current generated test ZIP and checksum are kept alongside this README.
