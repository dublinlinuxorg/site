import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

def empty_list():
    return []

def md_files_to_pages(pages, page_list):
    for page in pages:
        page_list.append(Page(**page))
        if page.get('pages', False):
            md_files_to_pages(page['pages'], page_list)

@dataclass
class Page:
    id: str
    title: str
    relative_url: str
    menu_order: float
    md_file: Path = field(default=None)
    template: str = field(default="")
    sub_pages: List[any] = field(default_factory=empty_list)

@dataclass
class SiteConfig:
    title: str
    theme: str
    big_logo: str
    small_logo: str

@dataclass
class Site:
    site_config: SiteConfig
    pages: List[any] = field(default_factory=empty_list, init=False)

if __name__ == '__main__':
    with open('site.json', 'r') as site_file:
        site_json = json.load(site_file)
        site = Site(SiteConfig(**site_json['site_config']))
            # SiteConfig(site_json['site_config']),
            # md_files_to_pages(site_json['pages']) 
        # )

        # print(site)
    md_files_to_pages(site_json['pages'], site.pages)
    
    print(site)