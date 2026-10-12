# NETCONF: a MESMA pergunta do troféu RESTCONF, agora em XML
from ncclient import manager

m = manager.connect(
    host="192.168.0.142", port=830,
    username="admin", password="cisco123",
    hostkey_verify=False,                 # self-signed do lab
    device_params={"name": "iosxe"},      # dialeto YANG do IOS XE
)

# filtro XPath: pede SÓ o hostname (não a config inteira)
filtro = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <hostname/>
  </native>
</filter>"""

resposta = m.get_config(source="running", filter=filtro)
print(resposta.data_xml)     # ← compare com o JSON do RESTCONF: mesmo dado, outro formato!
m.close_session()
