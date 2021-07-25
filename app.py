# collect files in md_files/
# create a file using the templates in themes/THEME/templates folder
import shutil
import os
import markdown
import frontmatter
from pathlib import Path
from config import config, site_config
from jinja2 import Environment, FileSystemLoader
from copy import deepcopy


def get_frontmatter(f):
    """
    in: filename (str, Path)
    out: parsed frontmatter from the file	
    """
    with open(f, 'r') as fi:
        metadata, content  = frontmatter.parse(fi.read())
        return metadata, content


def render_markdown(mkd_file):
    """
    for the given markdown file, returns a dict with
    content as html and frontmatter as nested dict
    """
    frontmatter, mkd_text = get_frontmatter(mkd_file)
    html_string = markdown.markdown(mkd_text)
    return {'content': html_string, **frontmatter}


def app_run(root_dir):
    """
    removes everything from build and output dirs 
    gets every markdown file rendered, and using the renders and the layouts
    creates the final html files
    """
    # make sure you are in the correct place, as
    # this fn can get called from anywhere
    os.chdir(root_dir)
    # load the configuration
    theme_folder = Path(config['theme_folder'])
    template_folder = Path(config['template_folder'])
    live_folder = Path(config['live_folder'])
    output_folder = Path(config['output_folder'])
    markdown_folder = Path(config['md_folder'])
    asset_folder = Path(site_config['asset_folder'])
    site_config['menu'] = {}

    # delete the build dirs, remake them and the .gitkeeps in them
    for d in [output_folder, live_folder]:
        shutil.rmtree(d)
        d.mkdir()
        with open(Path(d, '.gitkeep'), 'w') as gk:
            gk.write('keep me')

    # load Jinja 2
    file_loader = FileSystemLoader(template_folder)
    env = Environment(loader=file_loader)

    # create a structure for the site config and 
    # the list of all the pages to display
    site = {}
    site['pages'] = []
    site['site_config'] = site_config

    # iterate over the page markdown files
    for md_file in markdown_folder.glob('**/*.md'):
        # parse the markdown into metadata dict and html
        page = render_markdown(mkd_file=md_file)
        menu_item = page['menu_item']

        # create a file path for each file
        # if it's the site index, write it into the top output folder
        if md_file == Path(markdown_folder, 'index.md'):
            index_file_path = Path(output_folder, 'index.html')
        else:
            # everything else gets written into it's own folder as
            # index html, to allow nicer urls
            index_file_path = Path(output_folder, md_file.parent.relative_to(markdown_folder), page['slug'], 'index.html')
        
        # add the index file path to the page config
        page['index_file_path'] = index_file_path
        
        page_menu_path = menu_item.split('/')

        def add_menu(site_menu, pm_path, parents, depth):
            if site_menu.get(pm_path[depth], None) is None:
                site_menu[pm_path[depth]] = {}
            depth += 1
            if depth == len(pm_path):
                return
            add_menu(site_menu, pm_path, depth)
        add_menu(site_config['menu'], page_menu_path, 0)
        print(site_config['menu'])
        # create the directory for the page
        index_file_path.parent.mkdir(parents=True, exist_ok=True)

        # create a page item and add it to the page list 
        # all the info about pages needs to be collected before any  
        # page is rendered, this ensures that menus are complete
        site['pages'].append(page)

    for page in site['pages']:
        # create the pages
        template = env.get_template(f'{page["template"]}.html')
        rendered_page = template.render(page=page,  
            site_config=site_config)
        with open(page['index_file_path'], 'w') as index_file:
            index_file.write(rendered_page)
    
    # copy the assests into the public folder
    for dd in [asset_folder, Path(theme_folder, 'css'), Path(theme_folder, 'js')]:
        src = Path(dd)
        dst = Path(live_folder, src.name)
        try:
            destination = shutil.copytree(src, dst)  
        except FileNotFoundError:
            pass

    # copy the output folder items into the public folder
    for f in output_folder.glob("**/*.html"):
        # recreate the parent folders in the live dir if needed
        live_parent_path = Path(live_folder, f.parent.relative_to(output_folder))
        live_parent_path.mkdir(parents=True, exist_ok=True)
        # copy the file
        try:
            shutil.copy((f), Path(live_parent_path, f.name))
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    app_run(os.getcwd())