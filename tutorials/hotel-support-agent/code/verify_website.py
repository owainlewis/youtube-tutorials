"""Credential-free checks for the saved website's local dependencies."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent / 'website'


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        self.urls.extend(attrs[key] for key in ('src', 'href') if attrs.get(key))


def main():
    page = References()
    page.feed((ROOT / 'index.html').read_text())
    urls = page.urls + re.findall(r"['\"](assets/[^'\"]+)['\"]", (ROOT / 'app.js').read_text())
    failures = []
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.path and not (ROOT / parsed.path).is_file():
            failures.append(f'Missing local asset: {parsed.path}')
        if not parsed.path and parsed.fragment and parsed.fragment not in page.ids:
            failures.append(f'Missing section: {parsed.fragment}')
    if failures:
        raise SystemExit('\n'.join(sorted(set(failures))))
    print('Website asset and section checks passed.')


if __name__ == '__main__':
    main()
