#!/usr/bin/env python
import json
import pmp_so_utils
from openpyxl import Workbook
from argparse import ArgumentParser

wbook = Workbook()
wsheet = wbook.active
wsheet.title = "Recursos"
wsheet['A1'] = "Hostname"
wsheet['B1'] = "Version s.o."
wsheet['C1'] = "Direccion IP"
wsheet['D1'] = "Uso filesystems"
wsheet['E1'] = "Responsable"
wsheet['F1'] = "Errores errpt"
wsheet['G1'] = "Porcentaje uso CPU"
wsheet['H1'] = "Estado de la Memoria"
wsheet['I1'] = "Observaciones"

parser = ArgumentParser(description="Reads a list of server resource values in json and generates a report in excel")
parser.add_argument('servers', nargs='+', help='List of dictionaries with server values', type=json.loads)
args = parser.parse_args()

#letters = [ chr(x) for x in range(ord('A'),ord('Z'))]

for host,row in zip(args.servers,range(1,len(args.servers)+1)):
    print(host['hostname'])
    wsheet['A'+str(row)] = host['hostname']
    wsheet['B'+str(row)] = host['verso']
    wsheet['C'+str(row)] = host['ip']
    #wsheet['D'+str(row)] = host['Filesystems']
    #wsheet['E'+str(row)] = host['cpu_usr']
    #wsheet['F'+str(row)] = host['hostname']
    wsheet['G'+str(row)] = "%usu="+host['cpu_usr']+"  %sys="+host['cpu_sys']+"  %wio="+host['cpu_wio']+"%idle= "+host['cpu_idle']
    wsheet['H'+str(row)] = "Usada= "+host['ram_used']+"   Libre= "+host['ram_free']+"  Swap usada=  "+host['swap']
    #wsheet['I'+str(row)] = host['']
