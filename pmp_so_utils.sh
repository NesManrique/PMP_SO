######################################################################################
#!/bin/bash
#
# pmp_so_utils.sh
#
# Script utilitario con funciones para usar dentro de otros scripts
#
# Autor: Nestor Manrique
#
#
# Ultima Modificación: 22/01/2015, por Nestor Manrique
#
######################################################################################
#
# Uso: dentro del script que se deseen usar las funciones definidias a continuación 
#      escribir al principio source pmp_so_utils.sh
#
######################################################################################


# Convierte un el Timestamp "MM-DD-YYYY:HH:MM" a timestamp de unix
tstampUnixt () {
 if [ "$1" ]; then
     local timestamp="$1"
     RETURN=$(date -d "`echo "$timestamp"|sed 's/-/\//g'| sed 's/\(..........\).\(..\).\(..\)$/\1 \2:\3/'`" +"%s" 2>/dev/null)
 else
     RETURN=""
 fi
}

# Convierte un timestamp de unix al timestamp "MM-DD-YYYY:HH:MM" 
unixtTstamp () {
 if [ "$1" ]; then
     local unixTime="$1"
     RETURN=`date -d @$unixTime +"%m-%d-%Y:%H:%M" 2>/dev/null`
 else
     RETURN=""
 fi
}

# Calcula la diferencia en minutos entre dos timestamps de formato "MM-DD-YYYY:HH:MM" 
tstampDiff () {
 if [ "$1" ] && [ "$2" ]; then
     local TSTAMP1=$1
     local TSTAMP2=$2

     tstampUnixt $TSTAMP1
     local UNIXTSTAMP1="$RETURN"

     tstampUnixt $TSTAMP2
     local UNIXTSTAMP2="$RETURN"

     [ $UNIXTSTAMP1 -gt $UNIXTSTAMP2 ] && local DIFF=$(($UNIXTSTAMP1-$UNIXTSTAMP2))

     [ $UNIXTSTAMP2 -ge $UNIXTSTAMP1 ] && local DIFF=$(($UNIXTSTAMP2-$UNIXTSTAMP1))

     RETURN=`date -u -d @"$DIFF" +'%-M'`
 else
     RETURN=""
 fi

}

# Genera timestamp actual en formato "MM-DD-YYYY:HH:MM" 
timestamp () {
 RETURN=`date +"%m-%d-%Y:%H:%M"`
}

# Genera timestamp actual en formato unix
timestamp_unix () {
 RETURN=`date +%s`
}

# Crea mensaje de alerta para el recurso
#
# $1: Hostname del servidor alertado
# $2: IP del servidor alertado
# $3: Recurso alertado
# $4: Valor del recurso
#

mensajeAlerta () {

	local HOSTNAME=$1
	local IP=$2
    local RECURSO=$3
	local VALOR=$4

    case $RECURSO in
    	DISP) RETURN="Alerta. El servidor $HOSTNAME no esta disponible." ;;
        RED) RETURN="Alerta. El servidor $HOSTNAME perdio $VALOR de los paquetes ping." ;;
		*) RETURN="Alerta! El porcentaje de uso de $RECURSO en $IP $HOSTNAME esta en $VALOR revise y corrija el problema."
    esac
}

# Revisa si un servidor esta en ventana de mantenimiento
#
# $1: IP del servidor a revisar
#
# Retorna en la variable RETURN 0 si esta en ventana 1 si no lo esta
#

enVentana () {

	IP=$1

 	# Si el servidor esta en mantenimiento lo ignoro
   	INICIO_VENT=`grep "^$IP|" mantenimiento.servers | tail -1 | cut -f2 -d\|`
   	FIN_VENT=`grep "^$IP|" mantenimiento.servers | tail -1 | cut -f3 -d\|`

   	tstampUnixt $INICIO_VENT
   	INICIO_VENT=$RETURN

   	tstampUnixt $FIN_VENT
   	FIN_VENT=$RETURN

   	timestamp_unix

	if [ "$INICIO_VENT" ] && [ "$RETURN" -ge "$INICIO_VENT" ] && [ "$RETURN" -lt "$FIN_VENT" ]; then
		echo "EN VENTANA $IP"
		RETURN=0
	else
		RETURN=1
	fi
}


# Chequea el estado de un recurso y envia un mensaje por correos si este se 
# encuentra entre los valores especificados sin incluirlos. 
#
# $1: Nombre del recurso: CPU_USR, CPU_SYS, RAM, SWAP, DISP, RED, FS_<Nombre del FS>.
# $2: Valor del estado del recurso
# $3: IP:HOSTNAME del servidor a revisar
# $4: Umbral inferior (default=0)
# $5: Umbral superior (default=100)
#

alertaRecEnRango () {

	[ "$#" -lt 4 ] && [ "$#" -ge 6 ] && echo "alertaRecEnRango Numero incorrecto de parámetros" && exit 1

	local RECURSO=$1
	local VALOR=$2
    local SERV=$3
	[ "$4" ] && local COTAINFERIOR=$4 || local COTAINFERIOR=0
	[ "$5" ] && local COTASUPERIOR=$5 || local COTASUPERIOR=100
    
    # Obtengo IP y nombre del servidor
	local IP=`echo $SERV | cut -f1 -d":"`
    local HOSTNAME=`echo $SERV | cut -f2 -d":"`

    #Debugging stuff
	#echo $VALOR
    #echo $COTAINFERIOR
    #echo $COTASUPERIOR

	if [ "$VALOR" -gt "$COTAINFERIOR" ] && [ "$VALOR" -lt "$COTASUPERIOR" ]; then
		# Creo log para guardar los mails de alerta que se han enviado y cuando se enviaron
		# o capturo la información del último mail enviado por la misma alerta si el log ya existe
		[ -e $ALERT_MAIL_LOG ] && ULTIMO_MAIL_ENVIADO=`grep "^$RECURSO|$SERV" $ALERT_MAIL_LOG |tail -1 | cut -f3 -d\|` || touch $ALERT_MAIL_LOG
		timestamp
		[ "$ULTIMO_MAIL_ENVIADO" ] && tstampDiff $RETURN $ULTIMO_MAIL_ENVIADO || RETURN=$((TIEMPO_REENVIO_MAIL+1))

		# Si el ultimo mail se envio hace mas tiempo del configurado entonces se reenvía la alerta
		# en un nuevo correo y se actualiza el log de envio de alertas
		if [ "$RETURN" -ge "$TIEMPO_REENVIO_MAIL" ]; then
		   #ENVIAR MAIL DE ALERTA DE DESCONEXION
		   mensajeAlerta $HOSTNAME $IP $RECURSO $VALOR
           echo $RETURN
		   timestamp
		   echo "$RECURSO|$SERV|$RETURN" >> $ALERT_MAIL_LOG
	   fi
	fi

}
