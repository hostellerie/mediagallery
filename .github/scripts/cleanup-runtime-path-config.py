from pathlib import Path

path = Path('install_defaults.php')
text = path.read_text(encoding='utf-8')

patterns = {
    "    'tmp_path'                   => $_CONF['path'] . 'plugins/mediagallery/tmp/',\n": 1,
    "    'ftp_path'                   => $_CONF['path'] . 'plugins/mediagallery/uploads/',\n": 1,
    "        $c->add('tmp_path',              $_MG_DEFAULT['tmp_path'],                 'text',     0,  0, 0,    $o++, true, $n, 4);\n": 2,
    "        $c->add('ftp_path',              $_MG_DEFAULT['ftp_path'],                 'text',     0,  0, 0,    $o++, true, $n, 4);\n": 2,
}

for pattern, expected in patterns.items():
    count = text.count(pattern)
    if count != expected:
        raise SystemExit(
            'Expected %d match(es), found %d for: %s'
            % (expected, count, pattern.strip())
        )
    text = text.replace(pattern, '')

path.write_text(text, encoding='utf-8')
