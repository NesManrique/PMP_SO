#!/usr/bin/env python
import sys
import ConfigParser
import ast
import socket
import re
import pmp_so_utils

config = ConfigParser.RawConfigParser()
config.read('./pmp_so.cfg')
servidores = {}
check = re.compile("/{1,2}[-_A-Za-z0-9]*(/[-_A-Za-z0-9]*)*")

count=1
while 1 == 1:
    try:
        countstr = str(count)
        aux_dict = ast.literal_eval(config.get('servidores', 'servidor'+countstr))
        for k, v in aux_dict.iteritems():
            if k=='ip':
                try:
                    socket.inet_aton(v)
                except socket.error as err:
                    print "La ip del servidor"+countstr+" no es valida."
                    print "Verifique el archivo de configuracion."
                    exit(1)
            elif k=='hostname':
                if not pmp_so_utils.is_valid_hostname(v):
                    print "El hostname del servidor"+countstr+" no es valido."
                    print "Verifique el archivo de configuracion."
                    exit(1)
            elif k=='red': 
                if (type(v) is not int or ( 0 > v or v > 100 )):
                    print "El valor del umbral de red para el servidor"+countstr+" no es valido." 
                    print "Verifique el archivo de configuracion."
                    exit(1)
            elif k in ['cpu_usr', 'cpu_sys', 'mem_ram', 'mem_swap', 'filesys'] or check.match(k): 

                if type(v) is not list:
                    print "Error de sintaxis en los umbrales de " + k + " en el servidor" + countstr + "."
                    print "Verifique el archivo de configuracion."
                    exit(1)

                if type(v[0]) is not int or type(v[1]) is not int or v[0] > v[1] or v[0] < 0 or v[1] > 100:
                    print "Los umbrales de " + k + " para el servidor"+countstr+" no son validos."
                    print "Verifique el archivo de configuracion."
                    exit(1)
            else:
                print "Opcion " + k + " no valida en la definicion del servidor"+countstr+"."
                print "Verifique el archivo de configuracion."
                exit(1)

        print aux_dict
        servidores[aux_dict['ip']]=d1
        count+=1
    except ConfigParser.NoOptionError as inst:
        print inst
        print servidores
        break
    except SyntaxError as inst:
        print "Error de sintaxis en la definicion del servidor" + countstr + "."
        print "Verifique el archivo de configuracion."
        exit(1)

print "saliendo"
