# ================================================================
# trofeu.py — SEMANA 2: ferramenta RESTCONF completa
# Rode no devnet-1:  python3 trofeu.py
# Evolução: dia 1 (hostname) + dia 2 (input) + dia 3 (interfaces)
#           + dia 4 (função genérica — um GET pra qualquer path)
# Domínios: 1 (funções, dict, loop) + 2 (requests, status, auth)
# ================================================================
import sys                 # faltava no dia 2! (sys.exit precisa dele)
import requests
import json
import urllib3

urllib3.disable_warnings()

USER = "admin"
PASS = "cisco123"
HEADERS = {"Accept": "application/yang-data+json"}   # MIME do RESTCONF (cai na prova!)


# --- a função genérica: UM GET que serve pra QUALQUER path ------------
def get_restconf(host, path):
    """Faz GET no RESTCONF e devolve o objeto response (ou None se falhou)."""
    url = f"https://{host}/restconf/data/{path}"
    try:
        r = requests.get(url, auth=(USER, PASS), headers=HEADERS,
                         verify=False, timeout=10)
    except requests.exceptions.ConnectionError:
        print("Sem rota até o roteador — confira o IP (show ip int brief)")
        return None

    if r.status_code == 200:
        return r
    if r.status_code == 401:
        print("Credencial errada — check username/password na borda")
    elif r.status_code == 404:
        print(f"Path não existe ({path}) — restconf está ligado?")
    else:
        print("Resposta inesperada:", r.status_code, r.text[:200])
    return None


# --- as "vistas": cada uma lê o SEU documento ------------------------
def mostra_hostname(host):
    r = get_restconf(host, "Cisco-IOS-XE-native:native/hostname")
    if r:
        dado = r.json()
        print("Hostname:", dado["Cisco-IOS-XE-native:hostname"])

def mostra_interfaces_state(host):
    r = get_restconf(host, "ietf-interfaces:interfaces-state")
    if not r:
        return
    dado = r.json()
    for i in dado["ietf-interfaces:interfaces-state"]["interface"]:
        nome = i.get("name")
        status = i.get("oper-status", "?")
        # o IP vive em ipv4/ietf-ip:ipv4/address
        enderecos = i.get("ietf-ip:ipv4", {}).get("address", [])
        ips = ", ".join(e.get("ip") for e in enderecos) or "sem IP"
        print(f"{nome:<20}{status:<10}{ips}")

def mostra_interfaces(host):
    r = get_restconf(host, "Cisco-IOS-XE-native:native/interface")
    if not r:
        return
    dado = r.json()
    # desce a árvore YANG: interface → GigabitEthernet → lista
    ifaces = dado["Cisco-IOS-XE-native:interface"]["GigabitEthernet"]

    print(f"\n{'INTERFACE':<20}{'IP':<16}{'DESCRIÇÃO'}")
    print("-" * 50)
    for i in ifaces:
        # nome  = i.get("name", "?")
        nome = "GigabitEthernet" + str(i.get("name", "?"))
        descr = i.get("description", "-")
        ip    = i.get("ip", {}) \
                    .get("address", {}) \
                    .get("primary", {}) \
                    .get("address", "sem IP")
        print(f"{nome:<20}{ip:<16}{descr}")


# --- main: o programa em si ------------------------------------------
HOST = input("IP do roteador: ").strip()
if not HOST:
    print("IP vazio — nada a fazer")
    sys.exit(1)

mostra_hostname(HOST)
mostra_interfaces(HOST)
mostra_interfaces_state(HOST)