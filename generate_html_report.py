#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
import os

# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def print_html_doc():
# Create the jinja2 environment.
# Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR+'/templates'),
                            trim_blocks=True,lstrip_blocks=True)
    print(j2_env.get_template('report.html').render(
        title='Hellow Gist from GitHub'
    ))

if __name__ == '__main__':
    print_html_doc()
