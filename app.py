# collect files in md_files/
# create a file using the index.html template
import shutil
import os
import markdown
import frontmatter
import logging
from pathlib import Path
from config import config
from jinja2 import Environment, FileSystemLoader
from jinja2.nodes import Output


def get_frontmatter(f):
    """
    in: filename (str, Path)
    out: parsed frontmatter from the file	
    """
    with open(f, 'r') as fi:
        metadata, content  = frontmatter.parse(fi.read())
        return metadata, content


def render_markdown(temp_folder, mkd_file, environ):
    """
    in: 
    template_folder: the folder where the templates are in (Path, str)
    md_file: markdown file with page content (Path)

    """
    frontmatter, mkd_text = get_frontmatter(mkd_file)
    html_string = markdown.markdown(mkd_text)
    if 'template' in frontmatter.keys() \
        and Path(temp_folder, f'{frontmatter["template"]}.html').exists():
        template = environ.get_template(f'{frontmatter["template"]}.html')
    elif Path(temp_folder, f'{mkd_file.name}.html').exists():
        template = environ.get_template(f'{mkd_file.name}.html')
    else:
        template = environ.get_template('index.html')
    rendered_html = template.render(page={'content': html_string, **frontmatter})
    return {'content': rendered_html, **frontmatter}

def app_run(root_dir):
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    logging.info("regenerating")
    # make sure you are in the correct place, as
    # this fn can get called from anywhere
    os.chdir(root_dir)
    # load the configuration
    template_folder = Path(config['template_folder'])
    live_folder = Path(config['live_folder'])
    output_folder = Path(config['output_folder'])
    markdown_folder = Path(config['md_folder'])

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
    for md_file in markdown_folder.glob('*.md'):
        # parse the markdown into metadata dict and html
        page = render_markdown(temp_folder=template_folder,
            mkd_file=md_file,
            environ=env)
        # add this to the list 
        pages.append(page)

    # create the big page
    template = env.get_template('index.html')
    whole_site = template.render(pages=pages)

    # write the page into the index file
    with open(Path(output_folder, 'index.html'), 'w') as index_file:
        index_file.write(whole_site)
    
    # copy the assests into the public folder
    for dd in ['assets', 'images']:
        src = Path(dd)
        dst = Path(live_folder, dd)
        destination = shutil.copytree(src, dst)  
    shutil.copy(Path(output_folder, 'index.html'), Path(live_folder, 'index.html'))

if __name__ == '__main__':
    app_run(os.getcwd())