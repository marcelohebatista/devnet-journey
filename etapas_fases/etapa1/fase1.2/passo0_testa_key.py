# ================================================================
# passo0_testa_key.py — FASE 1.2, PASSO 0: a key da Groq está viva?
# ================================================================
# Rodar ANTES de tudo. Testa as 2 pré-condições da fase:
#   1. GROQ_API_KEY exportada no ambiente?
#   2. A key é VÁLIDA na Groq? (faz um GET no endpoint de modelos)
#
# Rodar no devnet-1:  python3 passo0_testa_key.py
#
# O QUE APRENDE AQUI:
#   - os.environ.get() com valor default (padrão profissional p/ segredos)
#   - endpoint /models: o "menu" da API (toda API cloud tem um)
#   - Bearer token já no header — o mesmo do ponte_ia.py
# ================================================================
import os                      # acesso a variáveis de ambiente
import requests                # o HTTP client de sempre

# --- 1. A key está no ambiente? ---------------------------------
KEY = os.environ.get("GROQ_API_KEY", "")

if not KEY:
    # falha 1: esqueceu de exportar (ou console novo sem o export)
    print("❌ GROQ_API_KEY não está definida!")
    print("   Rode:  export GROQ_API_KEY='gsk_sua_key_aqui'")
    print("   (lembrete: o export vale só pra sessão atual do terminal)")
    raise SystemExit(1)        # para o script com código de erro

print(f"✅ Key encontrada no ambiente: {KEY[:8]}...{KEY[-4:]}")
#                            ↑ mostra só o começo/fim — NUNCA a key inteira!
#                              (se alguém ver seu terminal, não vê o segredo)

# --- 2. A key é válida? GET no endpoint de modelos --------------
# O endpoint /models lista os modelos disponíveis — é o teste perfeito:
# é LEVE (não gasta tokens) e valida a autenticação de verdade.
URL_MODELOS = "https://api.groq.com/openai/v1/models"

r = requests.get(
    URL_MODELOS,
    headers={"Authorization": f"Bearer {KEY}"},   # Bearer — igual ao Meraki
    timeout=15,
)

# --- 3. Diagnóstico por status code -----------------------------
if r.status_code == 200:
    dados = r.json()
    modelos = [m["id"] for m in dados["data"]]     # extrai só os IDs
    print(f"✅ Key VÁLIDA! {len(modelos)} modelos disponíveis:")
    for m in modelos:
        print(f"   - {m}")
    print("\n🏆 Passo 0 completo — pode seguir pro ponte_ia.py")
elif r.status_code == 401:
    print("❌ 401: key inválida/revogada — gere outra em console.groq.com/keys")
else:
    # erro inesperado: mostra o corpo (APIs explicam o erro no r.text)
    print(f"❌ Status inesperado: {r.status_code}")
    print("   Corpo:", r.text[:300])
