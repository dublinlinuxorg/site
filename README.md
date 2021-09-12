# website

__everything works, but user experience is a bit barebones__

## A few basics

- To edit a page, edit to corresponding markdown file in /md_files and rebuild

- To add a new page, add a new markdown file to /md_files and add a corresponding section to sites.json and rebuild.

- Images, JavaScript and CSS for any page goes into the /assets folder

- The built page files and assets are in the /public folder

- Pushing to GitLab deploys the page (to https://test.dublinlinux.org/)

## Static site generator application

### Installing

- Python should be installed on your distro already. You will also need Pip and Virtualenv

- make sure you are using Python 3 (On Arch-based and Fedora-based distros use "python" and "pip", but on Ubuntu you might have to use "python3" and "pip3". This doc uses "python" and "pip").

- create a virtual environment:
    `python -m venv venv`

- activate it:
    `source venv/bin/activate`

- install the needed packages:
    `pip install -r requirements.txt`

### Running
- By default everything should be in working order when downloaded from the Main branch on GitLab. Re-generate the site:
    `python app.py`

- To see the site locally, open another terminal, navigate to the `public` folder and do
    `python -m http.server`

- The command output will give you a url to visit (most likely http://0.0.0.0:8000/). (So far running the SSG doesn't auto open the website in your browser, neither does the browser window auto refreshes on code change)

### The website content

- Edit the files in the md_files/ folder. Markdown, HTML or plain text 

- Any images, JavaScript, css and so on need to be in the /assets folder, or the application won't copy them into the public folder (copying them manually is not reliable, the folder gets cleaned on each build). That means that links to assets from any page need to start with /assets/

### Deploying

- Add, commit and push to GitLab. After a while (~ 3 minutes), if the GitLab CICD pipelines passed, the website will be deployed at https://test.dublinlinux.org/

### Customizing
#### Application Code
- The application is simple. It loads the site configuration from site.json and the app configuration from app_config.json and it crates data classes from these. It creates 2 menus ( a simple, html ready for use in the templates, and a more comprehensive pythonic dict, that needs to be parsed by a logic in the template), it renders the markdown as html using Jinja2 templates and it moves everything to the `public` folder (this is mandated by GitLab pages as the folder for www content.)

- The code needs more comments.

#### Site and application config

- the file site.json contains the configuration and description of the site

- the file app_config.json contains the configuration of the application (so far only folder locations)

- **if any configuration options are added to/removed from the config files, the corresponding code in app.py must be adjusted. dataclasses __init__s will fail if the parameters don't match expected members**

- Site-wide config is on the top of the site.json file.

- the `pages` section has nested pages. 

    - the menu_order must be either unique or negative. pages with a negative menu order won't be included in the menus.

    - the menu_order should reflect the nesting, e.g. if you have a page with order 3 that contains 2 other pages, the 2 inner pages should have the menu order 3.0 and 3.1

- the partials section is for parts of the site for which it makes sense to be declared separately from pages. For example the footer, that has to be under every page, should be declared here. for the partial to work, it has to have the existing md file and jinja template (html file). Its id is important, as that is what other templates are going to call it by - for example, to place the footer on the page, use the following in the template of that page:
    `{{ partials.footer }}`

#### Theming

- the theme for the site is set in site config in site.json 

- all themes need to be in /themes/theme_name

- all theme-wide assets (images, JS, CSS, ...) need to be in /themes/theme_name/theme_assets . The theme_assets folder is moved to the public folder on build

- /themes/theme_name/templates contains Jinja2 templates. Each page has one template file (set in site.json), multiple pages can share one template file and template files can include one another. For example, the redirect (subreddit, chat) pages use "blank" that just displays the pages contents. Other pages use the "basic" template that adds some menus and includes the boilerplate from the "base" template.
