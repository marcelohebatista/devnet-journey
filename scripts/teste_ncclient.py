from ncclient import manager
m = manager.connect(host="192.168.0.142", port=830, username="admin",
                    password="cisco123", hostkey_verify=False)
# pede a configuração inteira em XML estruturado
print(m.get_config(source="running").data_xml[:200])

