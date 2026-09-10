# Distribution archive

The installable MediaGallery test archive generated from `modernize-1.8.0` is committed directly in this directory by the GitHub Actions workflow **Build MediaGallery installable archive**.

To request a new archive, update `.github/dist-trigger` or run the workflow manually with `workflow_dispatch`.

The workflow always replaces the previous generated package with exactly one installable archive:

```text
dist/mediagallery_1.8.0_2.0.0.zip
```

The ZIP contains a single top-level `mediagallery/` directory suitable for Geeklog plugin installation/testing.

The build verifies archive integrity, required plugin files and required generic MediaGallery assets before committing the ZIP. A SHA-256 digest is calculated and logged during the workflow, but no separate checksum file is kept in `dist/`.
