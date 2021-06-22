# collect files in md_files/
# create a file using the index.html template
from jinja2 import Environment, FileSystemLoader
import markdown
import frontmatter
from pathlib import Path
from config import config


def get_frontmatter(f):
	"""
	in: filename (str, Path)
	out: parsed frontmatter from the file	
	"""
	with open(f, 'r') as fi:
		metadata, content  = frontmatter.parse(fi.read())
		return metadata, content


def render_markdown(temp_folder, mkd_file):
	"""
	in: 
	template_folder: the folder where the templates are in (Path, str)
	md_file: markdown file with page content (Path)

	"""
	frontmatter, mkd_text = get_frontmatter(mkd_file)
	html_string = markdown.markdown(mkd_text)
	if 'template' in frontmatter.keys() \
		and Path(temp_folder, f'{frontmatter["template"]}.html').exists():
		template = env.get_template(f'{frontmatter["template"]}.html')
	elif Path(temp_folder, f'{mkd_file.name}.html').exists():
		template = env.get_template(f'{mkd_file.name}.html')
	else:
		template = env.get_template('index.html')
	rendered_html = template.render(page={'content': html_string, **frontmatter})
	return {'content': rendered_html, **frontmatter}


if __name__ == '__main__':
	# load the configuration
	template_folder = Path(config['template_folder'])
	output_folder = Path(config['live_folder'])
	markdown_folder = Path(config['md_folder'])

	# load Jinja 2
	file_loader = FileSystemLoader(template_folder)
	env = Environment(loader=file_loader)

	# the list of all the pages to display
	pages = []
	# iterate over the page markdown files
	for md_file in markdown_folder.glob('*.md'):
		# parse the markdown into metadata dict and html
		page = render_markdown(temp_folder=template_folder,
			mkd_file=md_file )
		# add this to the list 
		pages.append(page)

	# create the big page
	template = env.get_template('index.html')
	whole_site = template.render(pages=pages)

	# write the page into the index file
	with open(Path(output_folder, 'index.html'), 'w') as index_file:
		index_file.write(whole_site)
	
	
