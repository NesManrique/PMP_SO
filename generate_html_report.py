#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
import os
import json
import pmp_so_utils

parser = ArgumentParser(description="Reads a list of server resource values in json and generates a report in html")
parser.add_argument('servers', nargs='+', help='List of dictionaries with server values', type=json.loads)
args = parser.parse_args()

# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def print_html_doc():
# Create the jinja2 environment.
# Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR+'/templates'),
                            trim_blocks=True,lstrip_blocks=True)
    print(j2_env.get_template('report.html').render(
        servidores = args.servers
    ))

if __name__ == '__main__':
    print_html_doc()
