# MediaGallery service API

MediaGallery 1.8.0 exposes read-only interoperability through Geeklog's native `PLG_invokeService()` mechanism.

## `album_list`

The `album_list` service returns albums already filtered through MediaGallery access rules. Consumers should use this service instead of querying `mg_albums`, `mg_media`, or `mg_media_albums` directly.

### Member album tree

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

if ($status === PLG_RET_OK) {
    // $output contains the visible member album tree.
}
```

`uid` defaults to the current Geeklog user. A normal user can request only their own member album tree. A user with `mediagallery.admin` may request another user's tree.

`member_album_root = 0` is valid and is supported.

### Numeric root

A caller can request the visible children of a specific album:

```php
$status = PLG_invokeService(
    'mediagallery',
    'album_list',
    array(
        'root'      => 123,
        'recursive' => true,
        'visible'   => true,
    ),
    $output,
    $svc_msg
);
```

The numeric root itself is used as the traversal root; the result contains its children and, when `recursive` is true, their descendants.

### Arguments

| Argument | Default | Meaning |
| --- | --- | --- |
| `uid` | current user | User whose member tree is requested when `root=member` |
| `root` | `member` | `member` or a numeric album ID |
| `recursive` | `true` | Include descendants |
| `visible` | `true` | Apply MediaGallery visibility filtering |

### Result

Each result row uses a stable associative structure:

```php
array(
    'id'       => 1064,
    'title'    => 'Thailand',
    'parent'   => 1060,
    'owner_id' => 42,
    'hidden'   => false,
    'access'   => 2,
    'depth'    => 2,
    'url'      => 'https://example.com/mediagallery/album.php?aid=1064',
);
```

Consumers should persist only the MediaGallery album ID when associating their own records with a gallery. Rendering should remain delegated to MediaGallery, for example through its existing gallery autotags, so the consuming plugin does not depend on MediaGallery's storage schema.

## Compatibility

The API is additive in MediaGallery 1.8.0. Existing pages, autotags, albums and database tables are not changed by enabling the service.
