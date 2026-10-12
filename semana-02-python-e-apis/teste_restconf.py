# ================================================================
# teste_restconf.py — SEMANA 2: ferramenta RESTCONF COMPLETA
# Rode no devnet-1:  python3 teste_restconf.py
# Traz: hostname · interfaces (config) · status + IP + tráfego ao vivo
# Domínios: 1 (funções, dict, loop) + 2 (requests, status, auth)
# ================================================================
import sys
import time                 # para a amostra de throughput
import requests
import json
import urllib3

urllib3.disable_warnings()

USER = "admin"
PASS = "cisco123"
HEADERS = {"Accept": "application/yang-data+json"}


# --- a função genérica: UM GET que serve pra QUALQUER path ------------
def get_restconf(host, path):
    """GET no RESTCONF → objeto response (ou None se falhou)."""
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


# --- helpers ----------------------------------------------------------
def pega_ip_da_interface(host, nome):
    """IP via path DIRETO (o GET largo vem sem ietf-ip:ipv4 — augmentation)."""
    r = get_restconf(host, f"ietf-interfaces:interfaces-state/interface={nome}")
    if not r:
        return "sem IP"

    # --- ESPIADA TEMPORÁRIA (remover depois de achar a chave) ---
    if nome == "GigabitEthernet1":
        print(json.dumps(r.json(), indent=2)[:800])
    # ------------------------------------------------------------
    
    ficha = r.json().get("ietf-interfaces:interface", {})
    enderecos = ficha.get("ietf-ip:ipv4", {}).get("address", [])
    return ", ".join(e.get("ip") for e in enderecos) or "sem IP"


def mostra_hostname(host):
    r = get_restconf(host, "Cisco-IOS-XE-native:native/hostname")
    if r:
        dado = r.json()
        print("Hostname:", dado["Cisco-IOS-XE-native:hostname"])


def mostra_interfaces(host):
    """A CONFIG (running-config em JSON — o 'show run' da API)."""
    r = get_restconf(host, "Cisco-IOS-XE-native:native/interface")
    if not r:
        return
    dado = r.json()
    ifaces = dado["Cisco-IOS-XE-native:interface"]["GigabitEthernet"]

    print(f"\n{'INTERFACE':<20}{'IP (config)':<16}{'DESCRIÇÃO'}")
    print("-" * 50)
    for i in ifaces:
        nome  = "GigabitEthernet" + str(i.get("name", "?"))
        descr = i.get("description", "-")
        ip    = i.get("ip", {}).get("address", {}) \
                    .get("primary", {}).get("address", "sem IP")
        print(f"{nome:<20}{ip:<16}{descr}")


def pega_state(host):
    """Estado de TODAS as interfaces: nome, status, speed, contadores."""
    r = get_restconf(host, "ietf-interfaces:interfaces-state")
    if not r:
        return []
    dado = r.json()
    saida = []
    for i in dado["ietf-interfaces:interfaces-state"]["interface"]:
        saida.append({
            "nome":   i.get("name", "?"),
            "status": i.get("oper-status", "?"),
            "speed":  int(i.get("speed", 0)),                      # bps
            "in":     int(i.get("statistics", {}).get("in-octets", 0)),
            "out":    int(i.get("statistics", {}).get("out-octets", 0)),
        })
    return saida


def mostra_state_e_trafego(host):
    """Status + IP real + throughput ao vivo (2 amostras, 5s de intervalo)."""
    print("\nMedindo tráfego (amostra 1)... aguarde 5s... amostra 2")
    a = pega_state(host)
    time.sleep(5)
    b = pega_state(host)

    print(f"\n{'INTERFACE':<20}{'STATUS':<18}{'IP':<16}{'IN':>10}{'OUT':>10}  (Mbps)")
    print("-" * 78)
    for x, y in zip(a, b):                 # mesma ordem nas 2 amostras
        delta_in  = (y["in"]  - x["in"])  * 8 / 5 / 1_000_000   # octets→bits→Mbps
        delta_out = (y["out"] - x["out"]) * 8 / 5 / 1_000_000
        ip = pega_ip_da_interface(host, x["nome"])
        print(f"{x['nome']:<20}{x['status']:<18}{ip:<16}"
              f"{delta_in:>10.2f}{delta_out:>10.2f}")


# --- main --------------------------------------------------------------
HOST = input("IP do roteador: ").strip()
if not HOST:
    print("IP vazio — nada a fazer")
    sys.exit(1)

mostra_hostname(HOST)
mostra_interfaces(HOST)
mostra_state_e_trafego(HOST)