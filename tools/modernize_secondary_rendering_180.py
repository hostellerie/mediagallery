from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit('Expected one %s marker in %s, found %d' % (label, path, count))
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


# Autotag wrappers: semantic figure/figcaption, responsive limits, no fixed caption width.
Path('templates/autotag.thtml').write_text('''<figure class="MG_autotag MG_autotag_{align}" style="max-width:{framewidth}px;">\n  <div class="MG_autotag_media">{autotag}</div>\n  {!if caption}<figcaption class="MG_autotag_caption">{caption}</figcaption>{!endif}\n</figure>\n''', encoding='utf-8')

Path('templates/autotag_nb.thtml').write_text('''<figure class="MG_autotag MG_autotag_nb MG_autotag_nb_{align}" style="max-width:{width}px;">\n  <div class="MG_autotag_media">{autotag}</div>\n  {!if caption}<figcaption class="MG_autotag_caption">{caption}</figcaption>{!endif}\n</figure>\n''', encoding='utf-8')

Path('templates/autotag_ss.thtml').write_text('''<figure class="MG_autotag MG_autotag_slideshow MG_autotag_{align}" style="max-width:{framewidth}px;">\n  <div id="slideshowContainer{ss_count}" class="slideshowContainer MG_autotag_slideshow_stage" style="max-width:{maxwidth}px;height:{maxheight}px;">\n    {pics}\n  </div>\n  {!if caption}<figcaption class="MG_autotag_caption">{caption}</figcaption>{!endif}\n</figure>\n''', encoding='utf-8')

# The generic autotag container can express alignment through classes instead of inline style.
p = Path('include/autotags.php')
text = p.read_text(encoding='utf-8')
old = """function MG_helper_getContainer($media, $align, $container)\n{\n    $style = '';\n    if ($align == 'center') {\n        $style = 'text-align:center;';\n    } else if ($align != '') {\n        $style = 'float:' . $align . ';';\n    }\n    $retval = '<' . $container . ' class=\"MG_autotag_media\" style=\"' . $style . '\">' . $media . '</' . $container . '>';\n\n    return $retval;\n}\n"""
new = """function MG_helper_getContainer($media, $align, $container)\n{\n    $allowedAlign = array('left', 'right', 'center');\n    $class = 'MG_autotag_media';\n    if (in_array($align, $allowedAlign)) {\n        $class .= ' MG_autotag_media_' . $align;\n    }\n\n    return '<' . $container . ' class=\"' . $class . '\">' . $media . '</' . $container . '>';\n}\n"""
if text.count(old) != 1:
    raise SystemExit('MG_helper_getContainer marker mismatch')
p.write_text(text.replace(old, new, 1), encoding='utf-8')

# Random block: move presentation into reusable CSS classes.
Path('templates/random_block.thtml').write_text('''<div class="mg_random_block">\n  {media_thumbnail}\n{!if media_title}\n  <div class="pluginSmallText mg_random_block_title">{media_title}</div>\n{!endif}\n  <div class="mg_random_block_browse">\n    <a href="{url_album}">{lang_browse_album}</a>\n  </div>\n</div>\n''', encoding='utf-8')

# Legacy fullscreen autotag/slideshow entry points stay compatible but get modern structure.
Path('templates/fsat.thtml').write_text('''<div class="mg-fslideshow-legacy" id="{id}" style="max-width:{width}px;">\n  <a class="mg-fslideshow-link" id="{id2}" href="{site_url}/index.php">Open slideshow</a>\n</div>\n<script type="text/javascript">\n(function () {\n    var source = '{movie}';\n    var match = source.match(/[?&]aid=([^%&]+)/);\n    var link = document.getElementById('{id2}');\n    if (match && link) {\n        link.href = '{site_url}/slideshow.php?aid=' + encodeURIComponent(match[1]);\n    }\n}());\n</script>\n''', encoding='utf-8')

Path('templates/fslideshow.thtml').write_text('''<header class="mg_album_header mg-fslideshow-header">\n  <h1 class="mg_album_title">{album_title}</h1>\n  {!if pagination}<nav class="mg_pagination" aria-label="Slideshow pagination">{pagination}</nav>{!endif}\n</header>\n<!-- BEGIN noItems -->\n<div class="mg-empty-album">\n  {no_images}\n</div>\n<!-- END noItems -->\n<!-- BEGIN slideItems -->\n<div class="mg-legacy-slideshow">\n  <p><a class="mg-fslideshow-link" href="{site_url}/slideshow.php?aid={aid}">Open slideshow</a></p>\n</div>\n<!-- END slideItems -->\n''', encoding='utf-8')

# HTML5 player snippets: preserve legacy filenames, remove hard-coded inline widths.
Path('templates/view_mp3_flv.thtml').write_text('''<div class="mg-media-player mg-media-player-audio mg-media-player-compact">\n  {u_pic}\n  <audio controls preload="metadata">\n    <source src="{movie}" type="audio/mpeg">\n    <a href="{movie}">{title}</a>\n  </audio>\n</div>\n''', encoding='utf-8')

Path('templates/view_mp3_qt.thtml').write_text('''<div class="mg-media-player mg-media-player-audio mg-media-player-standard">\n  {u_pic}\n  <audio controls preload="metadata">\n    <source src="{movie}">\n    <a href="{movie}">Download audio</a>\n  </audio>\n</div>\n''', encoding='utf-8')

Path('templates/view_mp3_wmp.thtml').write_text('''<div class="mg-media-player mg-media-player-audio" style="max-width:{width}px;">\n  {u_pic}\n  <audio controls preload="metadata">\n    <source src="{movie}">\n    <a href="{movie}">Download audio</a>\n  </audio>\n</div>\n''', encoding='utf-8')

Path('templates/mp3_qt.thtml').write_text('''<!doctype html>\n<html>\n<head>\n<meta charset="{charset}">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n{themeCSS}\n<title>{title}</title>\n</head>\n<body class="mg-player-popup-body">\n<div class="mg-media-player mg-media-player-audio mg-media-player-popup" style="max-width:{width}px;">\n  {u_pic}\n  <audio controls preload="metadata">\n    <source src="{movie}">\n    <a href="{movie}">{title}</a>\n  </audio>\n</div>\n</body>\n</html>\n''', encoding='utf-8')

# Add responsive CSS as a final override layer.
p = Path('public_html/style.css')
text = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 secondary public rendering layer */'
if marker in text:
    raise SystemExit('Secondary public rendering layer already present')
css = r'''

/* MediaGallery 1.8 secondary public rendering layer */
.MG_autotag {
  box-sizing: border-box;
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: 0.75rem;
  text-align: center;
}

.MG_autotag_left,
.MG_autotag_nb_left {
  float: left;
  margin-right: 1rem;
}

.MG_autotag_right,
.MG_autotag_nb_right {
  float: right;
  margin-left: 1rem;
}

.MG_autotag_center,
.MG_autotag_nb_center {
  margin-left: auto;
  margin-right: auto;
}

.MG_autotag_media,
.MG_autotag_media img,
.MG_autotag_media video,
.MG_autotag_media audio,
.MG_autotag_media iframe {
  max-width: 100%;
}

.MG_autotag_media_center {
  text-align: center;
}

.MG_autotag_media_left { float: left; }
.MG_autotag_media_right { float: right; }

.MG_autotag_caption {
  display: block;
  width: auto;
  max-width: 100%;
  margin-top: 0.35rem;
  line-height: 1.4;
  text-align: center;
  font-size: 0.875rem;
  text-indent: 0;
}

.MG_autotag_slideshow_stage {
  width: 100%;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  text-align: center;
}

.MG_autotag_slideshow_stage img {
  max-width: 100%;
  height: auto;
}

.mg_random_block_title,
.mg_random_block_browse {
  margin-top: 0.35rem;
}

.mg_random_block img {
  max-width: 100%;
  height: auto;
}

.mg-fslideshow-legacy {
  box-sizing: border-box;
  width: 100%;
  min-height: 2.5rem;
  margin: 0 auto;
  text-align: center;
}

.mg-fslideshow-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.5rem;
}

.mg-fslideshow-header .mg_pagination {
  margin-left: auto;
}

.mg-media-player {
  box-sizing: border-box;
  width: 100%;
  margin: 0 auto;
}

.mg-media-player audio,
.mg-media-player video {
  display: block;
  width: 100%;
  max-width: 100%;
}

.mg-media-player video {
  height: auto;
}

.mg-media-player-compact { max-width: 16.25rem; }
.mg-media-player-standard { max-width: 18.75rem; }

.mg-player-popup-body {
  margin: 0;
  padding: 1rem;
}

@media (max-width: 30rem) {
  .MG_autotag_left,
  .MG_autotag_right,
  .MG_autotag_nb_left,
  .MG_autotag_nb_right {
    float: none;
    margin-left: auto;
    margin-right: auto;
  }

  .MG_autotag_slideshow_stage {
    max-height: 70vh;
  }
}
'''
p.write_text(text + css, encoding='utf-8')

# Document the completed public-secondary template pass without claiming all inline styles are gone.
p = Path('ROADMAP.md')
text = p.read_text(encoding='utf-8')
needle = '- [x] Replace the public advanced-search presentation tables with a semantic responsive search form.\n'
addition = needle + '- [x] Modernize secondary public autotag, random-block, fullscreen-slideshow and maintained HTML5 audio rendering for responsive output.\n'
if text.count(needle) != 1:
    raise SystemExit('ROADMAP template marker mismatch')
p.write_text(text.replace(needle, addition, 1), encoding='utf-8')
