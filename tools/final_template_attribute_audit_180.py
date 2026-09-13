from pathlib import Path
import re

roots = [Path('templates'), Path('public_html/frames')]
attrs = ('href','src','action','style','onclick','title','alt','value')
pat = re.compile(r'\b('+'|'.join(attrs)+r')\s*=\s*(["\'])(.*?)\2', re.I|re.S)
var = re.compile(r'\{([A-Za-z0-9_]+)\}')
for root in roots:
    for p in sorted(root.rglob('*.thtml')):
        text = p.read_text(encoding='utf-8', errors='replace')
        for m in pat.finditer(text):
            vs = var.findall(m.group(3))
            if vs:
                line = text.count('\n',0,m.start())+1
                print('%s:%d\t%s\t%s\tvars=%s' % (p,line,m.group(1).lower(),m.group(3).replace('\n',' '),','.join(sorted(set(vs)))))
