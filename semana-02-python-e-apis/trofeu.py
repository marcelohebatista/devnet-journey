# ================================================================
# trofeu.py — SEMANA 2, DIA 1: o troféu RESTCONF (curl) → Python
# Rode no devnet-1:  python3 trofeu.py
# Antes: confirme o IP da borda (show ip int brief) — DHCP pode mudar!
# Domínios: 1 (Python básico) + 2 (requests, status codes, auth)
# ================================================================
import requests          # a biblioteca oficial do exame (cap. 2.3 do livro)
import json              # parser/serializador de JSON (cap. 2.4)
import urllib3           # só para silenciar o aviso do certificado self-signed

urllib3.disable_warnings()   # lab: certificado self-signed → verify=False

# --- variáveis: nunca hardcode de credenciais em produção (cap. 2.5) ---
HOST = "192.168.0.142"        # IP atual da Gi1 do CSR8000v (confira amanhã!)
USER = "admin"
PASS = "cisco123"

URL = f"https://{HOST}/restconf/data/Cisco-IOS-XE-native:native/hostname"
HEADERS = {"Accept": "application/yang-data+json"}   # MIME do RESTCONF (cai na prova!)

# --- a chamada (o curl virou 1 linha de Python) ---
r = requests.get(
    URL,
    auth=(USER, PASS),        # Basic Auth — base64 automático (tópico 2.7)
    headers=HEADERS,
    verify=False,             # self-signed do lab
    timeout=10,               # NUNCA sem timeout (cap. 2.3 — cai na prova!)
)

# --- tratamento de resposta: o coração do domínio 2 ---
print("Status:", r.status_code)          # 200 = OK (decorar a tabela de codes!)

if r.status_code == 200:
    dado = r.json()                      # JSON string → dict Python (json.loads por dentro)
    hostname = dado["Cisco-IOS-XE-native:hostname"]
    print("Hostname:", hostname)
    print("JSON completo:", json.dumps(dado, indent=2))   # dict → JSON bonito (dumps)
elif r.status_code == 401:
    print("Credencial errada — check username/password na borda")
elif r.status_code == 404:
    print("Caminho não existe — restconf está ligado? (show run | include restconf)")
else:
    print("Resposta inesperada:", r.text[:200])

# ================================================================
# DESAFIOS p/ evoluir o script (faça 1 por dia esta semana):
# 1. Trocar o IP hardcode por input("IP da borda: ") ou sys.argv
# 2. Pedir OUTRO campo (ex.: /native/interface → liste as interfaces!)
# 3. Envolver em try/except requests.exceptions.ConnectionError
# 4. Transformar em função: get_restconf(path) → retorna dict
# 5. BÔNUS PONTE-IA: a MESMA estrutura chama uma API de LLM
#    (só mudam URL + Bearer token — prove que a ponte existe)
# ================================================================
