#!/usr/bin/env python3
"""Tells the site its own web address.

Link previews (the picture and title shown when the site is shared in a message), the sitemap for search
engines and the "page not found" page all need the site's full web address. This script works the address out
and writes it into the files that need it. It is safe to run again and again: if nothing needs changing, it
changes nothing.

How the address is found, in this order:
  1. an address given on the command line:   python pipeline/site_address.py https://example.com/
  2. a custom domain, if a file called CNAME is in the repository
  3. GitHub's own address for the repository:  https://OWNER.github.io/REPOSITORY/
     (the weekly workflow runs the script this way, so normally you never need to run it yourself)

Files it writes, all in the top folder: index.html (a few lines in the head), 404.html (one line),
sitemap.xml and robots.txt. It never touches the scripts inside index.html, so the page's security policy
(which lists the exact scripts allowed to run) stays valid.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = '<!-- site-address:start (pipeline/site_address.py fills this in once the site has a web address) -->'
END = '<!-- site-address:end -->'
URL_OK = re.compile(r'^https://[a-z0-9]([a-z0-9.-]*[a-z0-9])?(/[A-Za-z0-9._~-]+)*/$')


def find_address(argv, env, root):
    """Returns the site's address, always ending in a slash, or None if it cannot be worked out."""
    if len(argv) > 1 and argv[1].strip():
        url = argv[1].strip()
        if not url.endswith('/'): url += '/'
        return url
    cname = os.path.join(root, 'CNAME')
    if os.path.exists(cname):
        host = open(cname, encoding='utf-8').read().strip().lower()
        if host: return 'https://' + host + '/'
    repo = (env.get('GITHUB_REPOSITORY') or '').strip()
    if '/' in repo:
        owner, name = repo.split('/', 1)
        owner = owner.lower()
        if name.lower() == owner + '.github.io': return 'https://' + owner + '.github.io/'
        return 'https://' + owner + '.github.io/' + name + '/'
    return None


def write_if_changed(path, text):
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
    if old == text: return False
    with open(path, 'w', encoding='utf-8', newline='\n') as f: f.write(text)
    return True


def apply(url, root):
    """Writes the address into the files. Returns the list of files that changed."""
    if not URL_OK.match(url): raise ValueError('That does not look like a web address this script can use: ' + url)
    changed = []
    path = '/' + url.split('/', 3)[3]                     # '/plateful/' or '/'

    idx = os.path.join(root, 'index.html')
    html = open(idx, encoding='utf-8').read()
    a, b = html.find(START), html.find(END)
    if a < 0 or b < a: raise ValueError('index.html has no site-address block (it may be an older copy).')
    block = (START + '\n'
             f'<link rel="canonical" href="{url}">\n'
             f'<meta property="og:url" content="{url}">\n'
             f'<meta property="og:image" content="{url}og-image.png">\n'
             f'<meta name="twitter:image" content="{url}og-image.png">\n')
    if write_if_changed(idx, html[:a] + block + html[b:]): changed.append('index.html')

    nf = os.path.join(root, '404.html')
    if os.path.exists(nf):
        h = open(nf, encoding='utf-8').read()
        h2, n = re.subn(r'<meta name="plateful-root" content="[^"]*">', f'<meta name="plateful-root" content="{path}">', h, count=1)
        if n and write_if_changed(nf, h2): changed.append('404.html')

    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               f'  <url><loc>{url}</loc></url>\n'
               '</urlset>\n')
    if write_if_changed(os.path.join(root, 'sitemap.xml'), sitemap): changed.append('sitemap.xml')

    robots = 'User-agent: *\nAllow: /\n\nSitemap: ' + url + 'sitemap.xml\n'
    if write_if_changed(os.path.join(root, 'robots.txt'), robots): changed.append('robots.txt')
    return changed


def main():
    url = find_address(sys.argv, os.environ, ROOT)
    if not url:
        print('Could not work out the site address. Give it on the command line, for example:\n'
              '  python pipeline/site_address.py https://yourname.github.io/plateful/')
        return 0                                          # never fail the weekly job over this
    try:
        changed = apply(url, ROOT)
    except ValueError as e:
        print('Site address not set:', e)
        return 0
    print('Site address:', url)
    print('Updated: ' + ', '.join(changed) if changed else 'Everything already had this address, nothing to change.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
