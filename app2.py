import json
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict

def empty_list():
    return []

def empty_dict():
    return {}

def page_from_template(page, menu, site_config):
    # load Jinja 2
    template = env.get_template(f'{page.template}.html')
    rendered_page = template.render(page=page, menu=menu, site_config=site_config)
    with open(page['index_file_path'], 'w') as index_file:
        index_file.write(rendered_page)

# def md_files_to_pages(pages, page_list):

@dataclass
class Page:
    id: str
    title: str
    slug: str
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
class MenuItem:
    page_id: str
    order: int = field(init=False)
    label: str = field(init=False)
    link: str = field(init=False)

@dataclass
class Site:
    site_config: SiteConfig
    pages: List[Page] = field(default_factory=empty_list, init=False)
    menu: List[MenuItem] = field(default_factory=empty_list, init=False)

    def make_page_list(self, pages, page_list):
        for page in pages:
            page_list.append(Page(**page))
            if page.get('pages', False):
                self.make_page_list(page['pages'], page_list)
        self.pages = page_list

    def make_menu(self):
        for page in self.pages:
            menu_item = MenuItem(page.id)
            menu_item.label = page.title
            menu_item.link = page.slug
            menu_item.order = page.menu_order
            self.menu.append(menu_item)

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

    template_folder = Path(app_config.theme_folder, site.site_config.theme, 'templates')
    file_loader = FileSystemLoader(template_folder)
    env = Environment(loader=file_loader)
    site.make_page_list(site_json['pages'], site.pages)
    site.make_menu()
    
    print(site)