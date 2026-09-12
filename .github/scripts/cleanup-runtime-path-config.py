from pathlib import Path

path = Path('install_defaults.php')
text = path.read_text(encoding='utf-8')

patterns = [
    "    'tmp_path'                   => $_CONF['path'] . 'plugins/mediagallery/tmp/',\n",
    "    'ftp_path'                   => $_CONF['path'] . 'plugins/mediagallery/uploads/',\n",
    "        $c->add('tmp_path',              $_MG_DEFAULT['tmp_path'],                 'text',     0,  0, 0,    $o++, true, $n, 4);\n",
    "        $c->add('ftp_path',              $_MG_DEFAULT['ftp_path'],                 'text',     0,  0, 0,    $o++, true, $n, 4);\n",
]

for pattern in patterns:
    count = text.count(pattern)
    if count != 1:
        raise SystemExit('Expected exactly one match, found %d for: %s' % (count, pattern.strip()))
    text = text.replace(pattern, '')

path.write_text(text, encoding='utf-8')
