#!/usr/bin/env python

import sys
import socket
from optparse import OptionParser

parser = OptionParser(usage = "Usage: %prog <server IP> <server Hostname> <username>")

(options, args) = parser.parse_args()

if len(args) != 3:
    parser.error("Incorrect number of arguments\n")

try:
    args[0]. 
