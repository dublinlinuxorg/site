# website

- all links to images, js and css need to be absolute in the html and tempates, but relative to the site root in the config:
    - in a template: `<img src="/{site_config.assets_folder}/{site_config.small_logo}">`
    - in markdown: `![dlc full logo](/assets/dl_logo.png?resize=200,200)`
    - in config.py: `'asset_folder': 'assets'`
- menus can be put together from a dict that is created from markdown files frontmatter (`menu_item`). Nested items are to be separated with a `/`:
    `menu_item: Learn about Linux/Links`
- parent menu items (`Learn about Linux` in the above example) don't have to have a page, in which case they won't be selectable (but they will still show up as a parent menu item)
- live folder must be called public, for gitlab cicd