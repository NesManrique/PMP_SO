######################################################################################
#!/bin/bash
#
# recolector.sh
#
# Script Recolector de Información de los Recursos de un servidor
#
# Recolecta información en % de uso de CPU, SWAP, RAM y Filesystems de un servidor. 
# Asi como la hora y el nombre del servidor. Y las devuelve en un string de la forma.
# FECHA:IP:HOSTNAME:CPU_USR:CPU_SYS:CPU_WIO:RAM:FREE:SWAP:VALORFS1%_NOMBREFS1_VALORFS2%_NOMBREFS2_...
#
# Autor: Nestor Manrique
#
# Version: 1.0
# Ultima Modificación: 20/01/2015, por Nestor Manrique
#
######################################################################################
#
# Uso: ./recolector.sh <IP> <Hostname> <Usuario>
#
# Parametros:
#		IP: Direccion IP del servidor a chequear
#		Hostname: hostname del servidor a chequear
#		usuario: Usuario con relación de confianza para conectarse al servidor
#
######################################################################################

# Nota: si alguien quiere usar estos regex los puse por separado

usage () {
	echo "./recolector.sh"
	echo ""
	echo "Recolecta información en % de uso de CPU, SWAP, RAM y Filesystems de un servidor."
	echo "Asi como la hora y el nombre del servidor y las devuelve en un string de la forma"
	echo "FECHA:IP:HOSTNAME:CPU_USR:CPU_SYS:CPU_WIO:RAM:FREE:SWAP:VALORFS1%_NOMBREFS1_VALORFS2%_NOMBREFS2_..."
	echo ""
	echo "Uso: ./recolector.sh <IP> <Hostname> <Usuario>"
}

if [ $# -ne 3 ] then
fi

VALIDIPADDREGEX="^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";

VALIDHOSTNREGEX="^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$";

IPYHOSTREGEX="^((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]):(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9]))$"

timestamp
FECHA=$RETURN
IP=$1
HOSTNAME=$2
SERVER=`echo "$1:$2"`
USUARIO=$3

if [[ ! $SERVER =~ $IPYHOSTREGEX ]]; then
	exit 1
fi

# Importo Script con Funciones
source pmp_so_utils.sh

# Recoge datos de los recursos segun el sistema operativo y los devuelve
# en porcentajes en un string.
#
# $1: IP:HOSTNAME del servidor a revisar
# $2: FECHA generada antes de correr la funcion
#
# Retorna:
#
# FECHA:IP:HOSTNAME:CPU_USR:CPU_SYS:CPU_WIO:RAM:FREE:SWAP:VALORFS1%_NOMBREFS1_VALORFS2%_NOMBREFS2_...
#

valoresRecursosPorc () {
    local SERVER=$1
        local FECHA=$2
        local SO=`uname`
        if [ $SO = "AIX" ]
           then
           verso=`uname -vs`
           maquina=`uuname -l`
           syslog="No aplica"
           errpt=`errpt|wc -l`
           if [ $errpt -lt 1 ]
                  then
                  errpt="OK"
           fi
           cpu=`sar -u 1 2|grep Avera|awk '{print "%usu="$2"  %sys="$3"  %wio="$4"  %idle="$5}'`
           um=`svmon -G | head -2|tail -1| awk {'print $3'}`
           um=`expr $um / 256`
           tm=`lsattr -El sys0 -a realmem | awk {'print $2'}`
           tm=`expr $tm / 1000`
           fm=`expr $tm - $um`
           memoria=`echo "Total="$tm"  Usada="$um"  Libre="$fm`
           swap=`lsps -s|tail -1|awk '{print $2}'|sed "s/%//g"`
           df|grep -v Filesystem|grep -v proc|awk '{print $4":"$7":"$2}'>/home/provseti/salida
        else
           if [ $SO = "HP-UX" ]
                  then
                  syslog="OK"
                  errpt="No aplica"
                  verso=`uname -sr`
                  cpu=`sar -u 1 2|grep Avera|awk '{print "%usu="$2"  %sys="$3"  %wio="$4"  %idle="$5}'`
                  memoria=`/etc/swapinfo -tam|grep memory|awk '{print "Total="$2"  Usada="$3"  Libre="$4}'`
                  tm=`/etc/swapinfo -tam|grep memory|awk '{print $2}'`
                  um=`/etc/swapinfo -tam|grep memory|awk '{print $3}'`
                  fm=`/etc/swapinfo -tam|grep memory|awk '{print $4}'`
        swap=`/etc/swapinfo -tam|grep total|awk '{print $5}'|sed "s/%//g"`
                  bdf | awk 'match($0,/[0-9]+% /) { print substr($0,RSTART,RLENGTH) $NF  } '|awk '{print $1":"$2":"$3}' >/home/provseti/salida
        else
           if [ $SO = "SunOS" ]
                  then
                  syslog="OK"
                  errpt="No aplica"
                  verso=`uname -sr`
                  cpu=`sar -u 1 2|grep Avera|awk '{print "%usu="$2"  %sys="$3"  %wio="$4"  %idle="$5}'`
                  tm=`/etc/swapinfo -tam|grep memory|awk '{print $2}'`
                  um=`/etc/swapinfo -tam|grep memory|awk '{print $3}'`
                  fm=`/etc/swapinfo -tam|grep memory|awk '{print $4}'`
                  swap=`/etc/swapinfo -tam|grep total|awk '{print $5}'|sed "s/%//g"`
                  df -h |grep -v Capacity| awk '{print $5":"$6":"$2}'>/home/provseti/salida
          else # [ SO = Linux ]
                  #Datos CPU
                  local CPU=`sar -u 1 2|grep Avera|awk '{print $3":"$5":"$6}'`
                  local CPU_USR=`echo "$CPU"|cut -f1 -d:`
                  local CPU_SYS=`echo "$CPU"|cut -f2 -d:`
                  local CPU_WIO=`echo "$CPU"|cut -f3 -d:`

                  #Datos Filesystems
                  local FILESYSTEMS=`df -H| awk 'match($0,/[0-9]+% /) { print substr($0,RSTART,RLENGTH) $NF  } '|awk '{print $1"_"$2"_"$3}' |paste -sd "" -`

                  #Datos Memoria RAM
                  local MEMORIA=`free |grep Mem:|awk '{print $2":"$3":"$4}'`
                  local TMEM=`echo "$MEMORIA" | cut -f1 -d:`
                  local UMEM=`echo "$MEMORIA" | cut -f2 -d:`

                  #Datos Memoria SWAP
                  local SWAPRAW=`free|grep Swap:|awk '{print $2":"$3}'|sed "s/%//g"`
                  local SWAPTOTAL=`echo $SWAPRAW | cut -f1 -d:`
                  local SWAPUSED=`echo $SWAPRAW | cut -f2 -d:`
                fi
          fi
        fi

        # Calculo Porcentajes de los Recursos

        # RAM
        local PORCRAM=$(echo "scale=4; $UMEM/$TMEM * 100" |bc)
        local RAM=`echo $PORCRAM|awk '{printf ("%d\n",$1 + 0.5)}'`
        local FREE=$((100-RAM))

        # SWAP
        local PORCSW=$(echo "scale=4; $SWAPUSED/$SWAPTOTAL * 100" |bc)
        local SWAP=`echo $PORCSW|awk '{printf ("%d\n",$1 + 0.5)}'`

        # CPU
        local CPU_USR=`echo $CPU_USR|awk '{printf ("%d\n",$1 + 0.5)}'`
        local CPU_SYS=`echo $CPU_SYS|awk '{printf ("%d\n",$1 + 0.5)}'`
        local CPU_WIO=`echo $CPU_WIO|awk '{printf ("%d\n",$1 + 0.5)}'`

        echo "$FECHA:$SERVER:$CPU_USR:$CPU_SYS:$CPU_WIO:$RAM:$FREE:$SWAP:$FILESYSTEMS"

}

# Si el servidor esta en mantenimiento lo ignoro
enVentana $IP
[ "$RETURN" -eq "0" ] && continue

# Si no esta en mantenimiento intento conexion ssh para correr la funcion que recolecta los datos
ENTRADA_ARCH=`ssh $USER@$IP -o ConnectTimeout=2 "$(typeset -f); valoresRecursosPorc $SERVER $FECHA"` 1>/dev/null 2>/dev/null

# Si no puedo hacer la conexion ssh guardo en el log y continuo con el siguiente servidor
[ "$?" -eq "255" ] && echo "No se pudo hacer la conexión ssh para generar los datos del servidor $HOSTNAME" && continue

# Retorno valores recolectados
echo $ENTRADA_ARCH
