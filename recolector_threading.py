#!/usr/bin/env python

import signal, sys, threading
import socket
import paramiko
import pmp_so_utils
import os
from optparse import OptionParser
from itertools import izip

def signal_cleanup(_signum, _frame):
    print '\nCLEANUP\n'
    sys.exit(0)

def workon(server_hostname,server_ip,ssh_username):

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    sshkey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_ip, username = ssh_username,  pkey = sshkey)

    stdin, stdout, stderr = ssh.exec_command("uname")

    plataforma = stdout.read().rstrip()

    server_values = {'date': pmp_so_utils.timestamp(), 'ip' : server_ip , 'hostname' : server_hostname}

    if plataforma == "AIX":
        print "AIX servers not yet supported"
        exit(0)
    elif plataforma == "HP-UX":
        print "HP-UX servers not yet supported"
        exit(0)
    elif plataforma == "SunOS":
        print "SunOS servers not yet supported"
        exit(0)
    elif plataforma == "Linux":

        #Datos CPU
        stdin, stdout, stderr = ssh.exec_command("sar -u 1 2|grep Avera|awk '{print $3\":\"$5\":\"$6}'")
        cpu = stdout.read().rstrip().split(":")
        server_values['cpu_usr'] = "{0:.2f}%".format(float(cpu[0]) + 0.5)
        server_values['cpu_sys'] = "{0:.2f}%".format(float(cpu[1]) + 0.5)
        server_values['cpu_wio'] = "{0:.2f}%".format(float(cpu[2]) + 0.5)

        #Datos Filesystems
        stdin, stdout, stderr = ssh.exec_command("df -H| awk 'match($0,/[0-9]+% /) { print substr($0,RSTART,RLENGTH) $NF  } '|awk '{print $1\"_\"$2 \"_\"$3}' | paste -sd \"\" -")
        fs = stdout.read().rstrip().split("_")[:-1]
        fs = iter(fs)
        fs = izip(fs,fs)
        for x,y in fs:
            server_values[y] = x

        #Datos Memoria RAM
        stdin, stdout, stderr = ssh.exec_command("free |grep Mem:|awk '{print $2}'")
        total_ram = stdout.read().rstrip()

        stdin, stdout, stderr = ssh.exec_command("free |grep cache:|awk '{print $3}'")
        used_ram = stdout.read().rstrip()

        server_values['ram'] = "{0:.2f}%".format(100 * float(used_ram)/float(total_ram))

        #Datos Memoria SWAP
        stdin, stdout, stderr = ssh.exec_command("free|grep Swap:|awk '{print $2\":\"$3}'|sed \"s/%//g\"")
        swap = stdout.read().rstrip().split(":") 
        total_swap = swap[0]
        used_swap = swap[1]

        server_values['swap'] = "{0:.2f}%".format(100 * float(used_swap)/float(total_swap))
    else:
        print "Platform "+ plataforma +" not supported."
        ssh.close()
        exit(0)

def main():

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
    
    # exit after a few seconds (see WARNINGs)
    signal.signal(signal.SIGALRM, signal_cleanup)
    signal.alarm(3)

    threads = [
        threading.Thread(
            target=workon, 
            args=(server_hostname,server_ip,ssh_username),
            name=server_hostname
            )
    ]

    for t in threads:
        # WARNING: daemon=True allows program to exit when main proc
        # does; otherwise we'll wait until all threads complete.
        t.daemon = True    
        t.start()

    for t in threads:
        # WARNING: t.join() is uninterruptible; this while loop allows
        # signals
        # see: http://snakesthatbite.blogspot.com/2010/09/cpython-threading-interrupting.html
        while t.is_alive():
            t.join(timeout=0.1)
    
if __name__=='__main__':
    main()

