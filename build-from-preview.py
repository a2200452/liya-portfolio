"""Rebuild the GitHub Pages copy from the claude.ai preview pages in ../網站.

Run from the liya-portfolio folder:  python3 build-from-preview.py
- claude.ai artifact links become relative links marked data-int (the language toggle keeps #en on them)
- target="_top" is dropped (only needed inside the claude.ai viewer)
- pages without a doctype get one
- each page's assets folder is mirrored (files removed from the preview are removed here too)
"""
import os, re, shutil, filecmp

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, '..', '網站')
PAGES = {  # artifact id -> (preview folder, published folder)
    'RDM8zHWKejft2eJjoAnC34': ('首頁', ''),
    'YMBuXjm4BFC5bF7TRoiBZ1': ('關於', 'about'),
    'CooyKos7JJctyfYd3vUgo4': ('Subway-上篇-研究與設計', 'subway-research'),
    'Ma96j9n5oDrHQk8Tqr3qaY': ('Subway-下篇-易用性測試', 'subway-usability'),
}

def rel(from_dir, to_dir):
    up = '../' if from_dir else ''
    return (up + to_dir + '/') if to_dir else (up or './')

def convert(html, here):
    def link(m):
        aid, frag = m.group(1), m.group(2) or ''
        return 'href="%s%s" data-int' % (rel(here, PAGES[aid][1]), frag)
    html = re.sub(r'href="https://claude\.ai/artifact/([A-Za-z0-9]+)(#[^"]*)?"', link, html)
    html = html.replace(' target="_top"', '')
    html = html.replace('a[href^="https://claude.ai/artifact/"]', 'a[data-int]')
    if not html.lstrip().lower().startswith('<!doctype'):
        html = '<!doctype html>\n<html lang="zh-Hant">\n<head>\n' + html
    return html

def mirror(src, dst):
    os.makedirs(dst, exist_ok=True)
    keep = set(os.listdir(src))
    for f in os.listdir(dst):
        if f not in keep and os.path.isfile(os.path.join(dst, f)):
            os.remove(os.path.join(dst, f)); print('  removed', f)
    for f in keep:
        s, d = os.path.join(src, f), os.path.join(dst, f)
        if os.path.isfile(s) and not (os.path.exists(d) and filecmp.cmp(s, d, shallow=False)):
            shutil.copy2(s, d); print('  copied', f)

for aid, (src_dir, out_dir) in PAGES.items():
    html = open(os.path.join(SRC, src_dir, 'index.html'), encoding='utf-8').read()
    out = convert(html, out_dir)
    assert 'claude.ai/artifact' not in out, src_dir
    dst = os.path.join(ROOT, out_dir)
    open(os.path.join(dst, 'index.html'), 'w', encoding='utf-8').write(out)
    print(out_dir or '(home)', 'page written,', out.count('data-int'), 'internal links')
    mirror(os.path.join(SRC, src_dir, 'assets'), os.path.join(dst, 'assets'))
