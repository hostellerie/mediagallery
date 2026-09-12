from pathlib import Path

path = Path('include/config_180.php')
text = path.read_text()

anchor = """function MG_applyRuntimeConfiguration180()
{
"""
helper = """function MG_prepareMediaStorage180($root)
{
    if (!MG_prepareDirectory180($root)) {
        return false;
    }

    if (!MG_prepareDirectory180($root . 'covers/')) {
        return false;
    }

    $buckets = str_split('0123456789abcdef');
    foreach (array('orig', 'disp', 'tn') as $type) {
        $typePath = $root . $type . '/';
        if (!MG_prepareDirectory180($typePath)) {
            return false;
        }

        foreach ($buckets as $bucket) {
            if (!MG_prepareDirectory180($typePath . $bucket . '/')) {
                return false;
            }
        }
    }

    return true;
}

function MG_applyRuntimeConfiguration180()
{
"""

assert text.count(anchor) == 1, 'runtime configuration anchor not found exactly once'
assert 'function MG_prepareMediaStorage180(' not in text, 'storage helper already exists'
text = text.replace(anchor, helper, 1)

old = "        MG_prepareDirectory180($_MG_CONF['path_mediaobjects']);"
new = "        MG_prepareMediaStorage180($_MG_CONF['path_mediaobjects']);"
assert text.count(old) == 1, 'expected exactly one multisite root preparation call'
text = text.replace(old, new, 1)

path.write_text(text)
