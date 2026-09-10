from pathlib import Path

p = Path('install_defaults.php')
text = p.read_text(encoding='utf-8', errors='surrogateescape')

single_lines = [
    "    'use_flowplayer'             => '0',\n",
    "        $c->add('use_flowplayer',       $_MG_DEFAULT['use_flowplayer'],           'select',   0,  0, 13,   $o++, true, $n, 1);\n",
]
for old in single_lines:
    if text.count(old) != 1:
        raise SystemExit('expected line not found exactly once: ' + old.strip())
    text = text.replace(old, '', 1)

swf_defaults = """    // Flash Media Player
    'swf_play'                   => '1',
    'swf_menu'                   => '0',
    'swf_scale'                  => 'showall',
    'swf_wmode'                  => 'transparent',
    'swf_allowscriptaccess'      => 'sameDomain',
    'swf_quality'                => 'high',
    'swf_loop'                   => '0',
    'swf_bgcolor'                => '#FFFFFF',
    'swf_width'                  => '640',
    'swf_height'                 => '480',
    'swf_flashvars'              => '',
    'swf_version'                => '6',

"""
if text.count(swf_defaults) != 1:
    raise SystemExit('SWF defaults block not found exactly once')
text = text.replace(swf_defaults, '', 1)

swf_add = """        // ----------------------------------
        $c->add('tab_flashmedia',        NULL,                                     'tab',      2,  0, NULL, 0,    true, $n, 13);
        $c->add('fs_flashmedia',         NULL,                                     'fieldset', 2,  0, NULL, 0,    true, $n, 13);

        $c->add('swf_play',              $_MG_DEFAULT['swf_play'],                 'select',   2,  0, 0,    $o++, true, $n, 13);
        $c->add('swf_menu',              $_MG_DEFAULT['swf_menu'],                 'select',   2,  0, 0,    $o++, true, $n, 13);
        $c->add('swf_scale',             $_MG_DEFAULT['swf_scale'],                'select',   2,  0, 26,   $o++, true, $n, 13);
        $c->add('swf_wmode',             $_MG_DEFAULT['swf_wmode'],                'select',   2,  0, 27,   $o++, true, $n, 13);
        $c->add('swf_allowscriptaccess', $_MG_DEFAULT['swf_allowscriptaccess'],    'select',   2,  0, 28,   $o++, true, $n, 13);
        $c->add('swf_quality',           $_MG_DEFAULT['swf_quality'],              'select',   2,  0, 29,   $o++, true, $n, 13);
        $c->add('swf_loop',              $_MG_DEFAULT['swf_loop'],                 'select',   2,  0, 0,    $o++, true, $n, 13);
        $c->add('swf_bgcolor',           $_MG_DEFAULT['swf_bgcolor'],              'text',     2,  0, 0,    $o++, true, $n, 13);
        $c->add('swf_width',             $_MG_DEFAULT['swf_width'],                'text',     2,  0, 0,    $o++, true, $n, 13);
        $c->add('swf_height',            $_MG_DEFAULT['swf_height'],               'text',     2,  0, 0,    $o++, true, $n, 13);
        $c->add('swf_flashvars',         $_MG_DEFAULT['swf_flashvars'],            'text',     2,  0, 0,    $o++, true, $n, 13);
        $c->add('swf_version',           $_MG_DEFAULT['swf_version'],              'text',     2,  0, 0,    $o++, true, $n, 13);

"""
if text.count(swf_add) != 1:
    raise SystemExit('SWF config block not found exactly once')
text = text.replace(swf_add, '', 1)

p.write_text(text, encoding='utf-8', errors='surrogateescape')
