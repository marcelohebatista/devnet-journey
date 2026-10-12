# ================================================================
# ponte_ia.py — FASE 1.2: A PONTE COMPLETA (versão final de referência)
# ================================================================
# Rede → código → IA: coleta interfaces via RESTCONF, envia à LLM,
# mostra o diagnóstico. Este arquivo é a VERSÃO COMPLETA — compare
# com o esqueleto dos TODOs e veja o que cada preenchimento faz.
#
# Rodar no devnet-1:  python3 ponte_ia.py
# Antes:  export GROQ_API_KEY='gsk_...'   (passo0_testa_key.py valida)
#
# FLUXO: [1] COLETA → [2] PROMPT → [3] POST → [4] LÊ
# ================================================================
import sys
import os
import requests
import json
import urllib3

urllib3.disable_warnings()

# --- credenciais de LAB do roteador (convenção Cisco — pode subir) ---
ROUTER_USER = "admin"
ROUTER_PASS = "cisco123"

# --- a key da LLM mora NO AMBIENTE, nunca no código ------------------
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
#MODEL    = "llama-3.3-70b-versatile"
MODEL = "openai/gpt-oss-120b"

# --- [1] COLETA: dados REAIS da rede via RESTCONF ---------------------
def get_restconf(host, path):
    """GET no RESTCONF → response (ou None). A mesma função de sempre."""
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
    """Estado das interfaces → lista de dicts {nome, status}."""
    r = get_restconf(host, "ietf-interfaces:interfaces-state")
    if not r:
        return []
    dado = r.json()
    return [
        {"nome": i.get("name"), "status": i.get("oper-status")}
        for i in dado["ietf-interfaces:interfaces-state"]["interface"]
    ]
    # ↑ list comprehension: o loop de sempre em 1 linha (cai na prova!)


# --- [2] PROMPT: dados + instrução no formato da API ------------------
def monta_prompt(lista_interfaces):
    """As 'messages' com papéis system/user (padrão de toda API de chat)."""
    dados_txt = json.dumps(lista_interfaces, indent=2, ensure_ascii=False)
    return [
        {"role": "system",
         "content": ("Você é um engenheiro de redes sênior especialista em "
                      "IOS XE. Responda em português, de forma direta e técnica.")},
        {"role": "user",
         "content": ("Analise o status destas interfaces de um roteador "
                      "IOS XE e diga o que está OK e o que merece atenção, "
                      "de forma direta:\n\n" + dados_txt)},
    ]


# --- [3] POST: o envio à LLM (a única parte realmente nova) -----------
def pergunta_llm(messages):
    """POST pra Groq → response (ou None). Bearer + corpo JSON."""
    if not GROQ_KEY:
        print("GROQ_API_KEY não definida — rode: export GROQ_API_KEY='...'")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",   # igual ao Meraki!
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,       # diagnóstico: determinístico
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    except requests.exceptions.ConnectionError:
        print("Sem rota até api.groq.com — confira DNS/gateway")
        return None

    if r.status_code == 200:
        return r
    # o corpo explica o erro — LEIA (401=key, 400=modelo, 429=rate limit)
    print("Erro na chamada:", r.status_code)
    print("Corpo:", r.text[:300])
    return None


# --- [4] LÊ: o texto que o modelo escreveu ----------------------------
def extrai_texto(r):
    """O caminho padrão de TODA API de chat: choices[0].message.content."""
    return r.json()["choices"][0]["message"]["content"]


# --- MAIN: a ponte inteira em 4 chamadas ------------------------------
if __name__ == "__main__":
    HOST = input("IP do roteador: ").strip()
    if not HOST:
        print("IP vazio — nada a fazer")
        sys.exit(1)

    print("\n[1/4] Coletando interfaces via RESTCONF...")
    interfaces = coleta_interfaces(HOST)
    if not interfaces:
        print("Nada coletado — abortando")
        sys.exit(1)
    print(f"      {len(interfaces)} interfaces coletadas")

    print("[2/4] Montando o prompt...")
    messages = monta_prompt(interfaces)

    print("[3/4] Enviando ao modelo (POST)...")
    r = pergunta_llm(messages)

    if r:
        print("[4/4] Diagnóstico da IA:\n")
        print(extrai_texto(r))
    else:
        print("Chamada falhou — veja a mensagem acima")
