# ================================================================
# passo3_post.py — FASE 1.2, PASSO 3: O POST (o coração da fase)
# ================================================================
# Faz um POST COMPLETO na Groq com um prompt mínimo ("diga Oi") —
# sem roteador, sem coleta. Testa SÓ a mecânica: Bearer + corpo + POST.
#
# Se este script funciona, a ponte inteira funciona — o resto é só
# trocar o conteúdo do prompt pelos dados reais.
#
# Rodar no devnet-1:  python3 passo3_post.py   (key já exportada!)
#
# O QUE APRENDE AQUI:
#   - POST vs GET: o pedido vai no CORPO (json=payload), não na URL
#   - Bearer token no header (o padrão OAuth2/API cloud — igual Meraki)
#   - o payload: model + messages + temperature
#   - ler o erro no r.text — APIs explicam o que deu errado
# ================================================================
import os
import requests

KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"     # confira console.groq.com/docs/models

if not KEY:
    print("❌ Exporte a key primeiro: export GROQ_API_KEY='gsk_...'")
    raise SystemExit(1)

# --- o header: autenticação + formato -------------------------------
headers = {
    # Bearer = "portador". O servidor lê o token e sabe quem você é.
    # Compare com o roteador: lá era auth=(user, pass) — Basic.
    # Mesmo LUGAR (header Authorization), formato DIFERENTE.
    "Authorization": f"Bearer {KEY}",

    # Content-Type: o formato do CORPO que EU envio.
    # (Accept = o formato que EU aceito RECEBER — a prova adora confundir)
    "Content-Type": "application/json",
}

# --- o corpo do POST: o pedido inteiro em JSON -----------------------
payload = {
    "model": MODEL,              # QUAL modelo responde
    "messages": [
        {"role": "user", "content": "Diga exatamente: Oi, ponte funcionando!"},
    ],
    "temperature": 0.3,          # 0=determinístico · 1=criativo (0.3: técnico)
}

# --- O POST — a linha mais importante da semana -----------------------
try:
    r = requests.post(URL, headers=headers, json=payload, timeout=30)
    #           ↑ verbo    ↑ auth já no header  ↑ O CORPO vai AQUI
    #           (compare: no GET do RESTCONF não havia corpo nenhum!)
except requests.exceptions.ConnectionError:
    print("❌ Sem rota até api.groq.com — confira DNS/gateway do container")
    raise SystemExit(1)

# --- diagnóstico por status code --------------------------------------
if r.status_code == 200:
    texto = r.json()["choices"][0]["message"]["content"]
    print("✅ Status 200 — a LLM respondeu:\n")
    print(texto)
    print("\n🏆 O POST funciona! A ponte inteira é isto + dados reais.")
elif r.status_code == 401:
    print("❌ 401: key inválida — gere outra em console.groq.com/keys")
elif r.status_code == 400:
    # 400 = corpo malformado OU modelo errado. O r.text diz qual!
    print(f"❌ 400 — o corpo explica: {r.text[:300]}")
elif r.status_code == 429:
    print("❌ 429: rate limit do free tier — espere 1 min e rode de novo")
else:
    print(f"❌ Status {r.status_code}: {r.text[:300]}")
