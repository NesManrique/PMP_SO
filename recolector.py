#!/usr/bin/env python

import sys
import socket
from optparse import OptionParser
import paramiko
import pmp_so_utils
import os

parser = OptionParser(usage = "Usage: %prog <server IP> <server Hostname> <username>")

(options, args) = parser.parse_args()

if len(args) != 3:
    parser.error("Incorrect number of arguments\n")

server_ip = args[0]
server_hostname = args[1]
ssh_username = args[2]

try:
    socket.inet_aton(server_ip)
except socket.error as err:
	print "\tServer IP is not valid"
	exit(1)

if not pmp_so_utils.is_valid_hostname(server_hostname):
	print "Hostname is not valid"
	exit(1)

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
sshkey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
ssh.connect(server_ip, username = ssh_username,  pkey = sshkey)

stdin, stdout, stderr = ssh.exec_command("ls")

for line in stdout:
    print '... ' + line.strip('\n')

ssh.close()

