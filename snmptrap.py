# python snmp trap receiver
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
from configx.configx import ConfigX
import os

try:
    conf_default_path = os.environ['conf_default']
    conf_user_path = os.environ['conf_user']
except:
    conf_default_path = "/opt/modules/snmpx/conf"
    conf_user_path = "/opt/modules/snmpx/conf.d"

snmp_config = ConfigX("snmpx.toml",conf_default_path,conf_user_path).get_all_configuration(True)

snmpEngine = engine.SnmpEngine()


listen_ip = snmp_config['trap']['listen_ip']  # Trap listener address (this machine ip)
Port = str(snmp_config['trap']['listen_port']) # trap listener port (default 162)

print("Agent is listening SNMP Trap on " + listen_ip + " , Port : " + Port)
print('--------------------------------------------------------------------------')
config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((listen_ip, int(Port)))
)

# Configure community here
config.addV1System(snmpEngine,snmp_config['trap']['community_name'], snmp_config['trap']['community_string'])


def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    print("Received new Trap message");
    for name, val in varBinds:
        f = open(snmp_config['trap']['trap_file_path'], "a+")
        print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
        f.write(('%s = %s\n' % (name.prettyPrint(), val.prettyPrint())))
        f.flush()
        f.close()


ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)

try:
    snmpEngine.transportDispatcher.runDispatcher()

except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise
