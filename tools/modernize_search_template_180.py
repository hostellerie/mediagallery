from pathlib import Path

p = Path('templates/search_page.thtml')
text = p.read_text(encoding='utf-8')
start = text.find('<table cellspacing="0" cellpadding="5"')
form_end = text.find('</form>', start)
if start == -1 or form_end == -1:
    raise SystemExit('Search header/form markers not found')
form_end += len('</form>')
new = '''<header class="mg_search_page_header">
  <h1 class="mg_search_page_title">{lang_search_title}</h1>
  {!if select_adminbox}<div class="mg_adminbox">{select_adminbox}</div>{!endif}
</header>

{msg}

<form name="mgsearch" action="{s_form_action}" method="post" class="uk-form mg_search_form" role="search">
  <fieldset>
    <legend class="mg-visually-hidden">{lang_search_title}</legend>
    <div class="mg_search_form_grid">
      <div class="mg_form_group mg_form_group_wide">
        <label for="mg-search-keywords">{lang_search_for}:</label>
        <div class="mg_search_query_controls">
          <input type="search" id="mg-search-keywords" name="keywords" value="{search_keywords}"{xhtml}>
          <label for="mg-search-keytype">{lang_options}:</label>
          {keytype_select}
        </div>
      </div>

      <div class="mg_form_group">
        <label for="mg-search-swhere">{lang_search_in}:</label>
        {swhere_select}
      </div>

      <div class="mg_form_group">
        <label for="mg-search-category">{lang_category}:</label>
        {cat_select}
      </div>

      <div class="mg_form_group">
        <label for="mg-search-user">{lang_user}:</label>
        {user_select}
      </div>

      <div class="mg_form_group">
        <label for="mg-search-numresults">{lang_results}:</label>
        <div>{nresults_select} <span>{lang_per_page}</span></div>
      </div>
    </div>

    <div class="mg_form_actions">
      <input type="submit" name="mode" value="{lang_search}"{xhtml}>
      <input type="submit" name="mode" value="{lang_cancel}"{xhtml}>
      <input type="hidden" name="mode" value="search"{xhtml}>
    </div>
  </fieldset>
</form>'''
text = text[:start] + new + text[form_end:]
text = text.replace('<div class="mg_navbar">', '<div class="mg_navbar" role="navigation" aria-label="Search results navigation">')
text = text.replace('<div style="text-align:center;font-size:small;text-indent:0;padding-top:2px;">\n   {album_description}\n</div>', '<div class="mg_album_description mg_search_description">\n  {album_description}\n</div>')
text = text.replace('<span class="mg_separator" style="">|</span>', '<span class="mg_separator">|</span>')
p.write_text(text, encoding='utf-8')

p = Path('public_html/style.css')
css = p.read_text(encoding='utf-8')
marker = '/* MediaGallery 1.8 search form responsive layer */'
if marker in css:
    raise SystemExit('Search responsive layer already present')
css += r'''

/* MediaGallery 1.8 search form responsive layer */
.mg_search_page_header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.mg_search_page_title {
  margin: 0;
  font-size: clamp(1.4rem, 2vw + 0.75rem, 2rem);
  line-height: 1.25;
}

.mg_search_form fieldset {
  margin: 0;
  padding: 0;
  border: 0;
}

.mg_search_form_grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem 1.25rem;
}

.mg_form_group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 0;
}

.mg_form_group_wide {
  grid-column: 1 / -1;
}

.mg_form_group label {
  font-weight: 600;
}

.mg_form_group input[type="search"],
.mg_form_group input[type="text"],
.mg_form_group select {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.mg_search_query_controls {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(8rem, auto);
  gap: 0.5rem;
  align-items: center;
}

.mg_form_actions {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 1.25rem;
}

.mg_search_description {
  text-align: left;
}

@media (max-width: 48rem) {
  .mg_search_form_grid {
    grid-template-columns: 1fr;
  }

  .mg_form_group_wide {
    grid-column: auto;
  }

  .mg_search_query_controls {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 34rem) {
  .mg_search_page_header,
  .mg_form_actions {
    align-items: stretch;
  }

  .mg_search_page_header .mg_adminbox,
  .mg_form_actions input[type="submit"] {
    width: 100%;
  }
}
'''
p.write_text(css, encoding='utf-8')

p = Path('ROADMAP.md')
roadmap = p.read_text(encoding='utf-8')
marker = '- [x] Modernize bundled file-list, podcast, jQuery gallery and SimpleViewer skins for responsive layouts and semantic album headings.\n'
addition = marker + '- [x] Replace the public advanced-search presentation tables with a semantic responsive search form.\n'
if roadmap.count(marker) != 1:
    raise SystemExit('Roadmap bundled skin marker mismatch')
p.write_text(roadmap.replace(marker, addition, 1), encoding='utf-8')
