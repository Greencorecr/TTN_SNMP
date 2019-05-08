# Conector entre SNMP e InfluxDB
# Se encarga de pedir los datos a los sensores via SNMP, e insertarlos
# en la BD de Influx para ser consumido los scripts que presentan a Check_MK
from influxdb import InfluxDBClient
from pysnmp.hlapi import *
from datetime import datetime

# InfluxDB
influxHost='localhost'
influxPort=8086
influxUser = 'root'
influxPassword = 'root'
influxDbname = 'sensores'
influxDbuser = 'greencore'
influxClient = InfluxDBClient(influxHost, influxPort, influxUser, influxPassword, influxDbname)

field = {}
fields = {}
# Consulta SNMP a ESP32
config = {
        'caida'       : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.214', 'snmpOID': '1.3.6.1.4.1.5.0', 'payload': 'caida'},
        'consumo_01'  : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.212', 'snmpOID': '1.3.6.1.4.1.5.0', 'payload': 'amps'},
        'consumo_02'  : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.212', 'snmpOID': '1.3.6.1.4.1.5.1', 'payload': 'amps'},
        'consumo_03'  : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.212', 'snmpOID': '1.3.6.1.4.1.5.2', 'payload': 'amps'},
        'consumo_04'  : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.212', 'snmpOID': '1.3.6.1.4.1.5.3', 'payload': 'amps'},
        'gotas'       : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.211', 'snmpOID': '1.3.6.1.4.1.5.0', 'payload': 'gotas'},
        'humedad'     : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.210', 'snmpOID': '1.3.6.1.4.1.5.1', 'payload': 'temphum'},
        'temperatura' : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.210', 'snmpOID': '1.3.6.1.4.1.5.0', 'payload': 'temphum'},
        'puerta'      : {'snmpCommunity': 'greencore', 'snmpHost': '10.42.22.213', 'snmpOID': '1.3.6.1.4.1.5.0', 'payload': 'puerta'},
        # TODO: puerta Open
         }

def influx_insert(json_body):
    try:
        influxClient.write_points(json_body)
    except:
        if __debug__:
            print("Write points: {0}".format(json_body))
            print ("Error: paquete con error")


for c_id, c_info in config.items():
    if __debug__:
        print("Config ID:", c_id)

    errorIndication, errorStatus, errorIndex, varBinds = next(
       getCmd(SnmpEngine(),
       CommunityData(config[c_id]['snmpCommunity'], mpModel=0),
       UdpTransportTarget((config[c_id]['snmpHost'], 161)),
       ContextData(),
       ObjectType(ObjectIdentity(config[c_id]['snmpOID'])))
    )
    if errorIndication:
        print("Error: " + str(errorIndication))
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        snmpdata = str(varBinds[0]).split("= ")
        if __debug__:
            print(snmpdata[1])
        if c_id == "caida":
            json_body = [
                {
                    "measurement": "sensorcaida",
                    "tags": {
                        "dev_id": c_id,
                        "type": config[c_id]['payload']
                    },
                    "time": datetime.now().isoformat(),
                    "fields": {
                        "Caida": snmpdata[1]
                    }
                }
            ]
            influx_insert(json_body)
        elif c_id == "gotas":
            json_body = [
                {
                    "measurement": "sensorgotas",
                    "tags": {
                        "dev_id": c_id,
                        "type": config[c_id]['payload']
                    },
                    "time": datetime.now().isoformat(),
                    "fields": {
                        "Gotas": snmpdata[1]
                    }
                }
            ]
            influx_insert(json_body)
        elif c_id == "humedad":
            hum = float(snmpdata[1])
        elif c_id == "temperatura" or c_id == "humedad":
            if c_id == "humedad":
                hum = float(snmpdata[1])
            else:
               json_body = [
                   {
                       "measurement": "sensortemphum",
                       "tags": {
                           "dev_id": c_id,
                           "type": config[c_id]['payload']
                       },
                       "time": datetime.now().isoformat(),
                       "fields": {
                           "Hum": hum,
                           "Temp": float(snmpdata[1])
                       }
                   }
               ]
               influx_insert(json_body)
        elif c_id == "puerta":
            json_body = [
                {
                    "measurement": "sensorpuerta",
                    "tags": {
                        "dev_id": c_id,
                        "type": config[c_id]['payload']
                    },
                    "time": datetime.now().isoformat(),
                    "fields": {
                        "Count": snmpdata[1]
                        # TODO: Open
                    }
                }
            ]
            influx_insert(json_body)
        elif "consumo" in c_id:
            if c_id in consumo_01
            field[c_id[-1:]] = { "header": "Amps" + c_id[-1:],
                                 "body": float(snmpdata[1]) }
            json_body = [
                {
                    "measurement": "sensoramps",
                    "tags": {
                        "dev_id": c_id,
                        "type": config[c_id]['payload']
                    },
                    "time": datetime.now().isoformat(),
                    "fields": "fields"
                }
            ]
            influx_insert(json_body)
        else:
            raise Exception('Campo no encontrado')

