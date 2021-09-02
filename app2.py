import json
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple

from jinja2.filters import do_filesizeformat

def empty_list():
    return []

def empty_dict():
    return {}

@dataclass
class Page:
    id: str
    title: str
    slug: str
    menu_order: str
    md_file: Path = field(default=None)
    template: str = field(default=None)
    no_link: str = field(default=None)
    sub_pages: List[any] = field(default_factory=empty_list)

@dataclass
class SiteConfig:
    title: str
    theme: str
    big_logo: str
    small_logo: str
    template_folder: Path = field(init=False)
    def __post_init__(self):
        self.template_folder = Path(app_config.theme_folder, self.theme, 'templates')

@dataclass
class MenuItem:
    page_id: str
    label: str 
    link: str

@dataclass
class Site:
    site_config: SiteConfig
    menu_html: str = field(default="")
    env: Environment = field(init=False)
    file_loader: FileSystemLoader = field(init=False)
    pages: Dict[str, Page] = field(default_factory=empty_dict, init=False)

    def __post_init__(self):
        self.file_loader = FileSystemLoader(self.site_config.template_folder)
        self.env = Environment(loader=self.file_loader)
    
    def make_page_list(self, pages, page_dict):
        self.menu_html += '<ul>\n'
        for page in pages:
            self.menu_html += '<li>\n'
            page_dict[str(page['menu_order'])] = Page(**page)
            self.menu_html += f'<a href="/{page["slug"]}">{page["title"]}</a>\n'
            if page.get('sub_pages', False):
                self.make_page_list(page['sub_pages'], page_dict)
        self.menu_html += '</li>\n'
        self.menu_html += '</ul>\n'
        self.pages = page_dict

    def page_from_template(self, page):
        # load Jinja 2
        parent_folder = Path(app_config.live_folder, page.slug)
        parent_folder.mkdir(parents=True, exist_ok=True)
        if page.template is not None:
            template = self.env.get_template(f'{page.template}.html')
            rendered_page = template.render(page=page, menu=self.menu_html, site_config=self.site_config)
            file_path =  Path(parent_folder, 'index.html')
            with open(file_path, 'w') as index_file:
                index_file.write(rendered_page)

    def make_pages(self):
        for order, page in self.pages.items():
            # print(page, end='\n')
            self.page_from_template(page)

@dataclass
class AppConfig:
    md_folder: str
    theme_folder: str
    live_folder: str
    output_folder: str

if __name__ == '__main__':
    # load the application config, like where are different folders
    with open('app_config.json') as ap_file:
        ap_json = json.load(ap_file)
        app_config = AppConfig(**ap_json)

    # load the site config (includes pages definitions)
    with open('site.json', 'r') as site_file:
        site_json = json.load(site_file)
        site = Site(SiteConfig(**site_json['site_config']))

    site.make_page_list(site_json['pages'], site.pages)
    # print(site.menu)
    
    site.make_pages()
    # print(site)