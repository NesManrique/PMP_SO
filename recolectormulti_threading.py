#!/usr/bin/env python

import signal, sys, threading
import paramiko
import pmp_so_utils
import os
import pwd
import argparse
try:
    from itertools import izip as zip
except ImportError: # will be 3.x series
    izip = zip

def signal_cleanup(_signum, _frame):
    sys.exit(0)

def workon(server):

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    sshkey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_username = pwd.getpwuid(os.getuid()).pw_name

    ssh.connect(server, username = ssh_username,  pkey = sshkey)

    if pmp_so_utils.is_valid_ip(server):
        server_values = {'date': pmp_so_utils.timestamp(), 'ip' : server}
        stdin, stdout, stderr = ssh.exec_command("hostname")
        hostname = stdout.read().rstrip().decode("utf-8")
        server_values['hostname'] = hostname
    elif pmp_so_utils.is_valid_hostname(server):
        server_values = {'date': pmp_so_utils.timestamp(), 'hostname' : server}
        stdin, stdout, stderr = ssh.exec_command("grep "+server+" /etc/hosts|cut -f1 -d' '")
        ip = stdout.read().rstrip().decode("utf-8")
        server_values['ip'] = ip

    stdin, stdout, stderr = ssh.exec_command("uname")

    plataforma = stdout.read().rstrip().decode("utf-8")

    if plataforma == "AIX":
        print("AIX servers not yet supported")
        exit(0)
    elif plataforma == "HP-UX":
        print("HP-UX servers not yet supported")
        exit(0)
    elif plataforma == "SunOS":
        print("SunOS servers not yet supported")
        exit(0)
    elif plataforma == "Linux":

        #CPU DATA
        stdin, stdout, stderr = ssh.exec_command("sar -u 1 2|grep Avera|awk '{print $3\":\"$5\":\"$6}'")
        cpu = stdout.read().rstrip().decode("utf-8").split(":")
        server_values['cpu_usr'] = "{0:.2f}%".format(float(cpu[0]) + 0.5)
        server_values['cpu_sys'] = "{0:.2f}%".format(float(cpu[1]) + 0.5)
        server_values['cpu_wio'] = "{0:.2f}%".format(float(cpu[2]) + 0.5)

        #Filesystem DATA
        stdin, stdout, stderr = ssh.exec_command("df -H| awk 'match($0,/[0-9]+% /) { print substr($0,RSTART,RLENGTH) $NF  } '|awk '{print $1\"_\"$2 \"_\"$3}' | paste -sd \"\" -")
        fs = stdout.read().rstrip().decode("utf-8").split("_")[:-1]
        fs = iter(fs)
        fs = zip(fs,fs)
        for x,y in fs:
            server_values[y] = x

        #RAM DATA
        stdin, stdout, stderr = ssh.exec_command("free |grep Mem:|awk '{print $2}'")
        total_ram = stdout.read().rstrip().decode("utf-8")

        stdin, stdout, stderr = ssh.exec_command("free |grep cache:|awk '{print $3}'")
        used_ram = stdout.read().rstrip().decode("utf-8")

        server_values['ram'] = "{0:.2f}%".format(100 * float(used_ram)/float(total_ram))

        #SWAP DATA
        stdin, stdout, stderr = ssh.exec_command("free|grep Swap:|awk '{print $2\":\"$3}'|sed \"s/%//g\"")
        swap = stdout.read().rstrip().decode("utf-8").split(":") 
        total_swap = swap[0]
        used_swap = swap[1]

        server_values['swap'] = "{0:.2f}%".format(100 * float(used_swap)/float(total_swap))
        print(server_values)
    else:
        print("Platform "+ plataforma +" not supported.")
        ssh.close()
        exit(0)

def main():

    parser = argparse.ArgumentParser(description="Recolects resource data from a list of servers and returns a dict with the values.")
    parser.add_argument('servers', nargs='+', help='List of servers IPs or Hostnames')

    args = parser.parse_args()

    for server in args.servers:
        if not pmp_so_utils.is_valid_hostname(server) and not pmp_so_utils.is_valid_ip(server):
            print("\tServer IP or Hostname '"+ server + "' is not valid")
            exit(1)

    # exit after a few seconds (see WARNINGs)
    signal.signal(signal.SIGALRM, signal_cleanup)
    signal.alarm(5)

    threads = [
        threading.Thread(
            target=workon, 
            args=(host,),
            name='host #{}'.format(num+1)
            )
        for num,host in enumerate(args.servers)
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
            t.join(timeout=0.4)
    
if __name__=='__main__':
    main()

