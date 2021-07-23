from pathlib import Path

site_config = {
    'theme': 'dublin_linux_classic',
    'small_logo': 'small_logo.png',
    'asset_folder': 'assets',
}

config = {
	'md_folder': 'md_files',
	'theme_folder': Path('themes', f'{site_config["theme"]}'),
	'template_folder': Path('themes', f'{site_config["theme"]}', 'templates'),
	'live_folder': 'public', # this has to be called public because of GitLab pages
	'output_folder': 'output',
    'dev_url': '127.0.0.1',
    'dev_port': 5555
}