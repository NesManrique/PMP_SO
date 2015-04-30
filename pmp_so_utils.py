#!/usr/bin/env python
import sys
import re
from datetime import datetime, date, time, timedelta
from time import localtime

timestring="%Y-%b-%d:%H:%M:%S"

def timestamp():
    return datetime.strftime(timestring,localtime())

def timestampdiff(timestamp1, timestamp2):
    if datetime.strptime(timestamp2,timestring) > datetime.strptime(timestamp1,timestring):
        delta = datetime.strptime(timestamp2,timestring) - datetime.strptime(timestamp1,timestring)
        return delta.seconds/60
    delta = datetime.strptime(timestamp1,timestring) - datetime.strptime(timestamp2,timestring)
    return delta.seconds/60

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, timestring)
    except ValueError:
        raise ValueError("Formato de fecha incorrecto, deberia ser " + timestring)

def mensajeAlerta(hostname,ip,recurso,valor):
    if recurso == "DISP":
        return "Alerta! El servidor " + hostname + " no esta disponible."
    elif recurso == "RED":
        return "Alertar! El servidor " + hostname + " perdio " + valor + " de los paquetes ping."
    else:
        return "Alerta! El porcentaje de uso de " + recurso + " en " + ip + " " + hostname + " esta en " + valor + " revise y corrija el problema."

#def alertaRecEnRango():

#def

def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))
