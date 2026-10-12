# ================================================================
# passo1_coleta.py — FASE 1.2, PASSO 1: a coleta RESTCONF isolada
# ================================================================
# Roda SÓ a parte 1 da ponte (coleta) e mostra o resultado no terminal.
# Por que separar? Testar cada peça isolada = achar erro na peça certa.
# Se isto funciona, qualquer problema depois é do POST, não da coleta.
#
# Rodar no devnet-1:  python3 passo1_coleta.py
#
# O QUE APRENDE AQUI:
#   - função pura de coleta (reutilizável — o ponte_ia.py chama a MESMA)
#   - lista de dicts: o formato de dados mais comum de Python
#   - json.dumps(..., indent=2): dict → texto legível (o corpo do prompt!)
# ================================================================
import requests
import json
import urllib3

urllib3.disable_warnings()     # lab: certificado self-signed

ROUTER_USER = "admin"          # credencial de LAB (convenção Cisco)
ROUTER_PASS = "cisco123"


def get_restconf(host, path):
    """GET no RESTCONF → response (ou None). A mesma função de sempre —
    reutilizar código testado é o que separa engenharia de improviso."""
    url = f"https://{host}/restconf/data/{path}"
    try:
        r = requests.get(url, auth=(ROUTER_USER, ROUTER_PASS),
                         headers={"Accept": "application/yang-data+json"},
                         verify=False, timeout=10)
    except requests.exceptions.ConnectionError:
        print("Sem rota até o roteador — confira o IP (show ip int brief)")
        return None
    return r if r.status_code == 200 else None


def coleta_interfaces(host):
    """Estado de todas as interfaces → lista de dicts {nome, status}.

    É o 'peão' da ponte: dados crus, sem formatação. Quem formata
    é o passo seguinte (prompt). Separar coleta de formatação
    deixa cada função com UM papel (princípio da responsabilidade única).
    """
    r = get_restconf(host, "ietf-interfaces:interfaces-state")
    if not r:
        return []
    dado = r.json()
    lista = []
    # desce a árvore YANG: raiz → lista de interfaces
    for i in dado["ietf-interfaces:interfaces-state"]["interface"]:
        lista.append({
            "nome":   i.get("name"),            # ex.: GigabitEthernet1
            "status": i.get("oper-status"),    # ex.: up / lower-layer-down
        })
    return lista


# --- main: pede o IP, coleta, mostra --------------------------------
HOST = input("IP do roteador: ").strip()

print("\nColetando interfaces via RESTCONF...")
interfaces = coleta_interfaces(HOST)

if not interfaces:
    print("❌ Nada coletado — confira IP/rota/restconf na borda")
    raise SystemExit(1)

print(f"✅ {len(interfaces)} interfaces coletadas:\n")

# mostra como LISTA (o formato que o Python usa)
print("1) Como lista de dicts (formato interno):")
print(interfaces)

# mostra como TEXTO JSON (o formato que viaja no corpo do prompt!)
print("\n2) Como JSON formatado (é isto que vai DENTRO do prompt):")
print(json.dumps(interfaces, indent=2, ensure_ascii=False))

# \U0001F3C6 o momento didático: os DOIS são o MESMO dado, em 2 roupas.
# dict = como Python guarda · JSON = como o dado VIAJA pela internet.
