from jinja2 import Environment, PackageLoader, select_autoescape
from collections import defaultdict
import csv
import json
import os

if __name__ == '__main__':
    os.chdir('resource_maker')
    # prepare Jinja
    env = Environment(
        loader=PackageLoader("resource_maker"),
        autoescape=select_autoescape()
    )

    # grab the template
    template = env.get_template("resources.html")

    resource_fields = ["Category", "Subcategory", "Name", "Web", "Wikipedia", "Note"]
    template_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
    category_notes = {}
    with open('assets/DL site resources.csv', 'r') as resource_file:
        reader = csv.DictReader(resource_file) #, fieldnames=resource_fields)
        for line in reader:
            category = line['Category']
            category_note = line['CategoryNote'] if line['CategoryNote'] != '' else None
            subcategory = line['Subcategory']
            name = line['Name']
            web = line['Web']
            wikipedia = line['Wikipedia'] if line['Wikipedia'] != '' else None
            note = line['Note'] if line['Note'] != '' else None
            template_data[category][subcategory][name]['web'] = web
            if category_note is not None:
                category_notes[category] = category_note
            if wikipedia is not None:
                template_data[category][subcategory][name]['wikipedia'] = wikipedia
            if note is not None:
                template_data[category][subcategory][name]['note'] = note



    # write into the file
    with open('../public/resources.html', 'w') as html_file:
        html_file.write(template.render(template_data=template_data, category_notes=category_notes))
