#!/usr/bin/env python3
from pysnmp.hlapi import *
import json
from datetime import datetime
import time
import sys
from configx.configx import ConfigX
import os

try:
    conf_default_path = os.environ['conf_default']
    conf_user_path = os.environ['conf_user']
except:
    conf_default_path = "/opt/modules/snmpx/conf"
    conf_user_path = "/opt/modules/snmpx/conf.d"

snmp_config = ConfigX("snmpx.toml",conf_default_path,conf_user_path).get_all_configuration(True)


def walk(host, oid):
    time_stamp = time.mktime(datetime.now().timetuple())
    filename = 'snmp' + str(time_stamp)
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData(snmp_config['walk']['community_string']),
                                                                        UdpTransportTarget((host, snmp_config['walk']['listen_port'])), ContextData(),
                                                                        ObjectType(ObjectIdentity(oid)),ignoreNonIncreasingOid=True):
        if errorIndication:
            print(errorIndication, file=sys.stderr)
            f = open(filename, "a+")
            f.write(errorIndication + '\n', file=sys.stderr)
            f.flush()
            f.close()
            break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                  file=sys.stderr)
            f = open(filename, "a+")
            f.write('%s at %s \n' % (errorStatus.prettyPrint(),
                                     errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                    file=sys.stderr)
            f.flush()
            f.close()
            break
        else:
            for varBind in varBinds:
                print(varBind)
                f = open(filename, "a+")
                f.write(str(varBind) + ' \n')
                f.flush()
                f.close()
    dict1 = {}
    with open(filename) as fh:
        for line in fh:
            command, description = line.strip().split(None, 1)
            dict1[command] = description.strip()
    out_file = open(snmp_config['walk']['walk_file_path'] + filename + ".json", "w")
    json.dump(dict1, out_file, indent=4, sort_keys=False)
    out_file.close()
walk(snmp_config['walk']['agent_list'], snmp_config['walk']['oid_number'])

