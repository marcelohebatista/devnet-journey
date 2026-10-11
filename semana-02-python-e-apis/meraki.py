import requests, os
KEY = os.environ['MERAKI_KEY']
H = {"Authorization": f"Bearer {KEY}"}
BASE = "https://api.meraki.com/api/v1"
ORG = "669910444571370482"          # sua org (o print do Settings te deu)

orgs = requests.get(f"{BASE}/organizations", headers=H)
print("Orgs:", orgs.status_code, [(o["name"], o["id"]) for o in orgs.json()])

nets = requests.get(f"{BASE}/organizations/{ORG}/networks", headers=H)
print("Redes:", nets.status_code, [(n["name"], n["id"]) for n in nets.json()])

net_id = nets.json()[0]["id"]
devs = requests.get(f"{BASE}/networks/{net_id}/devices", headers=H)
print("Devices:", devs.status_code)
for d in devs.json():
    print("  -", d.get("model"), "| serial:", d.get("serial"), "| nome:", d.get("name"))

