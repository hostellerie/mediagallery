from pathlib import Path

p = Path('include/lib-media.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')

# Fix the generic renderer first: Media::getThumbInfo() returns media_size_orig.
generic_start = text.find('function MG_displayGeneric(')
generic_end = text.find('function MG_displayTGA(', generic_start)
if generic_start == -1 or generic_end == -1:
    raise SystemExit('unable to isolate MG_displayGeneric')
generic = text[generic_start:generic_end]
count = generic.count('$media_size_disp')
if count != 4:
    raise SystemExit('MG_displayGeneric expected 4 media_size_disp references, found %d' % count)
generic = generic.replace('$media_size_disp', '$media_size_orig')
text = text[:generic_start] + generic + text[generic_end:]

# SWF/FLV are no longer executable playback formats in 1.8. Keep the public
# format compatibility but render them as generic downloadable media.
def replace_function(source, start_name, end_name):
    start = source.find('function ' + start_name + '(')
    end = source.find('function ' + end_name + '(', start)
    if start == -1 or end == -1 or end <= start:
        raise SystemExit('unable to isolate ' + start_name)
    replacement = "function %s($I, $opt=array())\n{\n    return MG_displayGeneric($I, $opt);\n}\n\n" % start_name
    return source[:start] + replacement + source[end:]

text = replace_function(text, 'MG_displaySWF', 'MG_displayFLV')
text = replace_function(text, 'MG_displayFLV', 'MG_displayMP3')

if 'use_flowplayer' in text:
    raise SystemExit('use_flowplayer remains in lib-media.php after cleanup')
if 'split("=", $var)' in text:
    raise SystemExit('legacy split() remains in lib-media.php after cleanup')

p.write_text(text, encoding='utf-8', errors='surrogateescape')
