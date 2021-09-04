import json
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple
from operator import attrgetter
from copy import deepcopy

from jinja2.filters import do_filesizeformat

def empty_list():
    return []

def empty_dict():
    return {}

@dataclass
class Page:
    """
    Slightly differs from the JSON, includes all fields
    Where the JSON doesn't have a field, the Page class
    uses None as the field's value 
    """
    id: str
    title: str
    slug: str
    menu_order: str
    md_file: Path = field(default=None)
    template: str = field(default=None)
    no_link: str = field(default=None)
    pages: List[any] = field(default_factory=empty_list)

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
    pages: List[any] = field(default_factory=empty_list)

@dataclass
class Site:
    site_config: SiteConfig
    simple_menu: str = field(default="")
    menu: List = field(default_factory=empty_list)
    env: Environment = field(init=False)
    file_loader: FileSystemLoader = field(init=False)
    pages: List[Page] = field(default_factory=empty_list)

    def __post_init__(self):
        self.file_loader = FileSystemLoader(self.site_config.template_folder)
        self.env = Environment(loader=self.file_loader)
    
    def make_simple_menu(self, pages, indent_counter = 0):
        """
        creates a simplified nested menu as a html
        string from the Site class's pages member
        the menu items are ordered by each page's .menu_order
        """
        indent_string = '  ' * indent_counter
        self.simple_menu += f'{indent_string}<ul>\n'
        for page in sorted(pages, key=attrgetter('menu_order'), reverse=False):
        # for page in pages:
            self.simple_menu += f'{indent_string}  <li>\n'
            self.simple_menu += f'{indent_string}    <a href="/{page.slug}">{page.title}</a>\n'
            if page.pages != []:
                self.make_simple_menu(page.pages, indent_counter+1)
        self.simple_menu += f'{indent_string}  </li>\n'
        self.simple_menu += f'{indent_string}</ul>\n'

    def make_page_list(self, json_pages, page_list):
        """
        recursively traverses the possibly nested JSON's pages array
        creates a corresponding and if appropriate, nested list of Page classes 
        """
        for json_page in json_pages:
            page = Page(
                id = json_page['id'],
                title = json_page['title'],
                slug = json_page['slug'],
                menu_order = json_page['menu_order'],
                md_file = json_page.get('md_file', None),
                template = json_page.get('template', None),
                no_link = json_page.get('no_link', None),
                pages = []
            )
            page_list.append(page)
            if json_page.get('pages', False):
                # page_list = page_list[page_list.index(page)].pages
                self.make_page_list(json_page['pages'], page_list[page_list.index(page)].pages)
        self.pages = page_list

    def make_menu(self, pages, menu_list):
        """
        creates a list of menu items and sets the site's
        menu member to it.
        this offers more use than the simple menu, but is more
        difficult to use in the template.
        """
        for page in sorted(pages, key=attrgetter('menu_order'), reverse=True):
            menu_item = MenuItem(
                page_id = page.id,
                label = page.title,
                link = page.slug,
                # an assignment without deepcopy would cause the
                # list to be altered in the recursion
                pages = deepcopy(page.pages)
            )
            menu_list.append(menu_item)
            if menu_item.pages != []:
                self.make_menu(menu_item.pages, menu_list[menu_list.index(menu_item)].pages)
        self.menu = menu_list

    def page_from_template(self, page):
        # load Jinja 2
        parent_folder = Path(app_config.live_folder, page.slug)
        parent_folder.mkdir(parents=True, exist_ok=True)
        if page.template:
            template = self.env.get_template(f'{page.template}.html')
            rendered_page = template.render(page=page, menu=self.simple_menu, site_config=self.site_config)
            file_path =  Path(parent_folder, 'index.html')
            with open(file_path, 'w') as index_file:
                index_file.write(rendered_page)

    def make_pages(self, page_list):
        """
        iterates over Site.pages and creates a html file for each
        page that has a tempate 
        """
        for page in page_list:
            # print(page, end='\n')
            self.page_from_template(page)
            if page.pages != []:
                self.make_pages(page.pages)


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

    site.make_page_list(site_json['pages'], [])
    # s = list(map(print, [f'{p}\n' for p in site.pages]))
    
    # print(site.pages)

    site.make_simple_menu(site.pages)
    # print(site.simple_menu)

    site.make_menu(site.pages, [])
    # s = list(map(print, [f'{p}\n' for p in site.pages]))
    site.make_pages(site.pages)
    print(site.menu)
    # print(site)