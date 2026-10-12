# ================================================================
# ponte_ia.py — SEMANA 2, DIA 4: A PONTE REDE → IA
# ================================================================
# A TESE DO DESAFIO: "API é API"
#   A mesma estrutura que fala com o roteador (requests + auth + JSON)
#   fala com uma LLM. O que muda:
#     1. URL:        api.groq.com (nuvem) em vez do roteador
#     2. Auth:       Bearer token (como o Meraki!) em vez de Basic
#     3. Verbo:      POST com corpo JSON em vez de GET
#
# O FLUXO (decora — é o padrão de qualquer ferramenta "IA operacional"):
#   [1] COLETA  → pega dados REAIS da rede via RESTCONF
#   [2] PROMPT  → monta a mensagem pro modelo (dados + instrução)
#   [3] POST    → envia pra LLM (a única parte realmente NOVA)
#   [4] LÊ      → parseia a resposta e mostra o diagnóstico
#
# Rode no devnet-1:  python3 ponte_ia.py
# Antes: export GROQ_API_KEY="sua-key"   (NUNCA no código!)
# Key grátis: console.groq.com/keys
#
# Domínios: 2 (APIs, POST, auth Bearer) + a ponte pro seu futuro MLOps
# ================================================================
import sys
import os                     # lê variáveis de ambiente (a casa da API key)
import requests
import json
import urllib3

urllib3.disable_warnings()

# --- credenciais de LAB do roteador (convenção Cisco — pode subir) ---
ROUTER_USER = "admin"
ROUTER_PASS = "cisco123"

# --- a key da LLM mora NO AMBIENTE, nunca no código (lição Meraki) ---
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL    = "llama-3.3-70b-versatile"     # veja console.groq.com/docs/models


# ================================================================
# PARTE 1 — COLETA (você JÁ domina tudo aqui: é o teste_restconf!)
# ================================================================
def get_restconf(host, path):
    """GET no RESTCONF → objeto response (ou None). (A mesma de sempre.)"""
    url = f"https://{host}/restconf/data/{path}"
    try:
        r = requests.get(url, auth=(ROUTER_USER, ROUTER_PASS),
                         headers={"Accept": "application/yang-data+json"},
                         verify=False, timeout=10)
    except requests.exceptions.ConnectionError:
        print("Sem rota até o roteador — confira o IP")
        return None
    return r if r.status_code == 200 else None


def coleta_interfaces(host):
    """Pega nome+status+IP de cada interface e devolve uma LISTA de dicts."""
    r = get_restconf(host, "ietf-interfaces:interfaces-state")
    if not r:
        return []
    dado = r.json()
    lista = []
    for i in dado["ietf-interfaces:interfaces-state"]["interface"]:
        # TODO(1): monte o dict de cada interface com as chaves:
        #          "nome" (i.get("name")), "status" (i.get("oper-status"))
        #          Dica: o IP você já sabe que mora no modelo oper da Cisco —
        #          pega_ip_da_interface(host, nome) — copie-a do teste_restconf.py
        lista.append({
            "nome":   "???",   # preencha
            "status": "???",   # preencha
        })
    return lista


# ================================================================
# PARTE 2 — PROMPT (a arte nova: transformar dados em pergunta)
# ================================================================
def monta_prompt(lista_interfaces):
    """Dados da rede + instrução → as 'messages' que a API espera.

    A API de chat recebe SEMPRE uma lista de mensagens com papéis:
      [{"role": "system", "content": ...},   ← o "comportamento" do modelo
       {"role": "user",   "content": ...}]   ← o pedido com os dados
    """
    dados_txt = json.dumps(lista_interfaces, indent=2)   # lista → texto bonito

    messages = [
        {
            "role": "system",
            "content": ("Você é um engenheiro de redes sênior especialista em "
                         "IOS XE. Responda em português, de forma direta e técnica.")
        },
        {
            "role": "user",
            # TODO(2): escreva o pedido. Ex.: "Analise o status destas
            #          interfaces e diga o que está OK e o que merece atenção:
            #          <dados_txt>". Use f-string para embutir os dados.
            "content": "???"
        },
    ]
    return messages


# ================================================================
# PARTE 3 — POST (a ÚNICA parte realmente nova do desafio)
# ================================================================
def pergunta_llm(messages):
    """POST pra Groq → texto da resposta (ou None se falhou).

    Compare com o GET do RESTCONF — o que mudou:
      - auth=...        → header "Authorization: Bearer <key>"
      - sem corpo       → json=payload (o corpo da requisição!)
      - Accept: yang    → Content-Type: application/json
    """
    if not GROQ_KEY:
        print("GROQ_API_KEY não definida — rode: export GROQ_API_KEY='...'")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",     # igual ao Meraki!
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.3,     # 0=determinístico, 1=criativo. Diagnóstico: baixo.
    }

    # TODO(3): o POST. UMA linha de requests (a mais importante da semana):
    #   r = requests.post(GROQ_URL, headers=..., json=..., timeout=30)
    #   Dica: use try/except requests.exceptions.ConnectionError igual ao GET.
    r = None   # ← substitua

    if r is None:
        return None
    if r.status_code != 200:
        # TODO(4): imprima o diagnóstico: status + r.text[:300]
        #          (erros da LLM vêm explicadinhos no corpo — LEIA!)
        return None
    return r


# ================================================================
# PARTE 4 — LÊ a resposta (o parse final)
# ================================================================
def extrai_texto(r):
    """Response → o texto que o modelo escreveu.

    A resposta vem aninhada:  r.json()["choices"][0]["message"]["content"]
    (choices = as N alternativas; [0] = a primeira; message.content = o texto)
    """
    # TODO(5): navegue o JSON e devolva o texto:
    #   return r.json()[???][???][???][???]
    return "???"


# ================================================================
# MAIN — a ponte inteira em 4 chamadas
# ================================================================
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
