# collect files in md_files/
# create a file using the index.html template
import shutil
import os
import markdown
import frontmatter
from pathlib import Path
from config import config, site_config
from jinja2 import Environment, FileSystemLoader


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

    # delete the build dirs, remake them and the .gitkeeps in them
    for d in [output_folder, live_folder]:
        shutil.rmtree(d)
        d.mkdir()
        with open(Path(d, '.gitkeep'), 'w') as gk:
            gk.write('keep me')

    # load Jinja 2
    file_loader = FileSystemLoader(template_folder)
    env = Environment(loader=file_loader)

    # the list of all the pages to display
    pages = []
    # iterate over the page markdown files
    for md_file in markdown_folder.glob('**/*.md'):
        # parse the markdown into metadata dict and html
        page = render_markdown(mkd_file=md_file)
        menu_item = page['menu_item']
        # add this to the list 
    #     pages.append(page)

    # # create the pages
    # for page in pages:
        template = env.get_template(f'{page["template"]}.html')
        rendered_page = template.render(page=page,  
            site_config=site_config)

        # write each page into the index file
        # if it's the site index, write it into the top output folder
        if md_file == Path(markdown_folder, 'index.md'):
            index_file_path = Path(output_folder, 'index.html')
        else:
            # everything else gets written into it's own folder as
            # index html, to allow nicer urls
            index_file_path = Path(output_folder, md_file.parent.relative_to(markdown_folder), page['slug'], 'index.html')
        index_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_file_path, 'w') as index_file:
            index_file.write(rendered_page)
    
    # copy the assests into the public folder
    for dd in [asset_folder, Path(theme_folder, 'css'), Path(theme_folder, 'js')]:
        src = Path(dd)
        dst = Path(live_folder, src.name)
        try:
            destination = shutil.copytree(src, dst)  
        except FileNotFoundError:
            pass
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