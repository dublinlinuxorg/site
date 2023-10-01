# Welcome to Dublin Linux!

We’re a community of like-minded individuals in Dublin with a passion for Linux and all things free (as in free speech) and open source software. Whether you’re a seasoned Linux user or someone who would simply like to learn more please feel free to come along to one of our regular meetups or follow us through one of our social accounts. If chatting is more your thing you can find us on Telegram. We are a pretty active group!

---

This repository is designated for the [Dublin Linux website](https://dublinlinux.org).

Feel free to contribute to the site, submit any issues you may find, or anything else.

If you want to get more involved in the development of the site, please consider joining our [Matrix channel](https://matrix.to/#/!lfSGseSPnQWsUaYZda:matrix.org?via=matrix.org&via=matrix.dublinlinux.org)

## Notes:
- The www root is in the `public` folder
- The resource.html file is created by the resource_maker script, please don't edit it manually.
	- Any changes to its design should be made to the `resource_maker/templates/resources.html` file instead. It's a Jinja2 template.
	- Any chnages to it's data should be made to the `resource_maker/assets/DL site resources.csv` file.
- GitLab's CICD runs the resource_maker script during deployment.
- CICD is configured by the `.gitlab-ci.yml` file
 
