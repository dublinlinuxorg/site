import json
import markdown
import shutil as sh
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple
from operator import attrgetter
from copy import deepcopy

def empty_list():
    return []

def empty_dict():
    return {}

def string_to_path(s):
    return Path(s)

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
    favicon: str
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
            # negative menu_order means don't include in the menu
            if int(page.menu_order) < 0:
                continue
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
            # negative menu_order means don't include in the menu
            if int(page.menu_order) < 0:
                continue
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
        """
        given the page, it will use its .template to render
        it as html 
        """
        parent_folder = Path(app_config.live_folder, page.slug)
        parent_folder.mkdir(parents=True, exist_ok=True)
        if page.template:
            with open(Path(app_config.md_folder, page.md_file), 'r') as md_file:
                md_string = md_file.read()
            html_string = markdown.markdown(md_string)
            template = self.env.get_template(f'{page.template}.html')
            rendered_page = template.render(
                page = page,
                html_string = html_string,
                menu = self.simple_menu,
                site_config = self.site_config
            )
            file_path =  Path(parent_folder, 'index.html')
            with open(file_path, 'w') as index_file:
                index_file.write(rendered_page)

    def clear_live_dir(self):
        live_folder = Path(app_config.live_folder)
        # remove everything except the .gitkeep file from the public
        # directory, so that we can fill it with shiny new things
        for item in live_folder.glob('[!.]*'):
            try:
                sh.rmtree(item)
            # rmtree only removes directories, unlink only removes files...
            except NotADirectoryError:
                item.unlink()

    def copy_assets(self):
        """
        copy the asset dir into the public dir
        """
        sh.copytree(
            app_config.asset_folder,
            Path(app_config.live_folder, app_config.asset_folder.name)
        )

    def make_pages(self, page_list):
        """
        iterates over Site.pages and creates a html file for each
        page that has a tempate 
        """
        for page in page_list:
            self.page_from_template(page)
            if page.pages != []:
                self.make_pages(page.pages)
    
    def build(self, site_json):
        """
        goes through the steps from loading the site json to 
        generating and copying the files 
        """
        self.make_page_list(site_json['pages'], [])
        self.make_simple_menu(self.pages)
        self.make_menu(self.pages, [])
        self.clear_live_dir()
        self.make_pages(self.pages)
        self.copy_assets()
        
@dataclass
class AppConfig:
    md_folder: Path = field(default_factory=string_to_path)
    theme_folder: Path = field(default_factory=string_to_path)
    live_folder: Path = field(default_factory=string_to_path)
    output_folder: Path = field(default_factory=string_to_path)
    asset_folder: Path = field(default_factory=string_to_path)

    def __post_init__(self):
        self.md_folder = Path(self.md_folder)
        self.theme_folder = Path(self.theme_folder)
        self.live_folder = Path(self.live_folder)
        self.output_folder = Path(self.output_folder)
        self.asset_folder = Path(self.asset_folder)


if __name__ == '__main__':
    # load the application config, like where are different folders
    with open('app_config.json') as ap_file:
        ap_json = json.load(ap_file)
        app_config = AppConfig(**ap_json)

    # load the site config (includes pages definitions)
    with open('site.json', 'r') as site_file:
        site_json = json.load(site_file)
        site = Site(SiteConfig(**site_json['site_config']))
    
    # build the site
    site.build(site_json)

    # site.make_page_list(site_json['pages'], [])
    # s = list(map(print, [f'{p}\n' for p in site.pages]))
    # print(site.pages)
    # site.make_simple_menu(site.pages)
    # print(site.simple_menu)
    # site.make_menu(site.pages, [])
    # s = list(map(print, [f'{p}\n' for p in site.pages]))
    # site.clear_live_dir()
    # site.make_pages(site.pages)
    # print(site.menu)
    # print(site)
    # print(app_config)
    # site.copy_assets()