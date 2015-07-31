#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
import os
import json
import pmp_so_utils

# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def print_html_report():
# Create the jinja2 environment.
# Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR+'/templates'),
                            trim_blocks=True,lstrip_blocks=True)
    print(j2_env.get_template('report.html').render(
        servidores = args.servers
    ))

def print_html_historic_report():
# Create the jinja2 environment.
# Notice the use of trim_blocks, which greatly helps control whitespace.
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR+'/templates'),
                            trim_blocks=True,lstrip_blocks=True)
    print(j2_env.get_template('hist_report.html').render(
        servidores = args.servers
    ))


if __name__ == '__main__':

    parser = ArgumentParser(description="Reads a list of server resource values in json and generates a report in html")
    parser.add_argument('servers', nargs='+', help='List of dictionaries with server values', type=json.loads)
    #parser.add_argument('-f','--from', nargs='?', help='Beginning date for report',default="today")
    #parser.add_argument('-t','--to', nargs='?', help='End date for report', default="today")
    args = parser.parse_args()

    print_html_report()
    #print_html_historic_report()

