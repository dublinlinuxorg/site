import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

def md_files_to_pages(pages):
    for page in pages:
        print(page.get('md_file', None))
        if page.get('pages', False):
            md_files_to_pages(page['pages'])

@dataclass
class Page:
    id: str
    title: str
    relative_url: str
    menu_order: float
    template: str
    md_file: Path

@dataclass
class SiteConfig:
    title: str
    theme: str
    big_logo: str
    small_logo: str

@dataclass
class Site:
    site_config: SiteConfig
    pages: List[Page]

if __name__ == '__main__':
    with open('site.json', 'r') as site_file:
        site = json.load(site_file)
        # print(site)
    md_files_to_pages(site['pages'])