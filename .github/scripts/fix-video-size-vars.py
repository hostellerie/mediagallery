from pathlib import Path

p = Path('include/lib-media.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')

def patch_function(source, start_name, end_name):
    start_marker = 'function ' + start_name + '('
    end_marker = 'function ' + end_name + '('
    start = source.find(start_marker)
    end = source.find(end_marker, start + len(start_marker))
    if start == -1 or end == -1 or end <= start:
        raise SystemExit('unable to isolate ' + start_name)

    block = source[start:end]
    count = block.count('$media_size_disp')
    if count != 4:
        raise SystemExit('%s expected 4 media_size_disp references, found %d' % (start_name, count))
    block = block.replace('$media_size_disp', '$media_size_orig')
    return source[:start] + block + source[end:]

text = patch_function(text, 'MG_displayASF', 'MG_displayMOV')
text = patch_function(text, 'MG_displayMOV', 'MG_displaySWF')

p.write_text(text, encoding='utf-8', errors='surrogateescape')
