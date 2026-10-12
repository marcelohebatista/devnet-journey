# ================================================================
# passo4_parse.py — FASE 1.2, PASSO 4: ler a resposta (sem gastar key)
# ================================================================
# Navega o JSON de resposta da LLM usando uma resposta FICTÍCIA —
# não chama a API. É a aula de "JSON aninhado" isolada.
#
# Rodar em QUALQUER máquina com Python:  python3 passo4_parse.py
# (nem precisa do lab — é Python puro)
#
# O QUE APRENDE AQUI:
#   - o caminho choices[0].message.content (padrão de TODA API de chat)
#   - navegar dict aninhado: cada [] desce um nível da árvore
#   - json.dumps pra VER a árvore antes de navegar (o truque de sempre)
# ================================================================
import json

# --- uma resposta de chat REAL, capturada do formato da Groq ---------
# (é exatamente isto que r.json() devolve num POST com status 200)
resposta_ficticia = {
    "id": "chatcmpl-abc123",
    "object": "chat.completion",
    "created": 1760000000,
    "model": "llama-3.3-70b-versatile",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "A Gi1 está up com IP 192.168.0.142 — saudável. As demais estão lower-layer-down, esperado sem cabo no GNS3."
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 120,
        "completion_tokens": 45,
        "total_tokens": 165
    }
}

# --- 1. VER a árvore inteira antes de navegar -------------------------
print("A resposta completa (é ISTO que r.json() devolve):\n")
print(json.dumps(resposta_ficticia, indent=2, ensure_ascii=False))

# --- 2. NAVEGAR nível por nível ----------------------------------------
print("\n" + "=" * 60)
print("Navegando até o texto (cada [] desce um nível):\n")

print("1. ['choices']        →", type(resposta_ficticia["choices"]).__name__,
      " (a lista de alternativas)")
print("2. ['choices'][0]    →", "a PRIMEIRA alternativa (pedimos 1)")
print("3. ...['message']    →", "o pacote da resposta")
print("4. ...['content']    → o TEXTO que o modelo escreveu:\n")

# --- o caminho completo (a linha do TODO 5) ---------------------------
texto = resposta_ficticia["choices"][0]["message"]["content"]
print(texto)

# --- 3. BÔNUS: o "usage" — o que a API cobra/contabiliza --------------
print("\n" + "=" * 60)
print("Bônus — o campo usage (contabilidade de tokens):")
print(json.dumps(resposta_ficticia["usage"], indent=2))
print("\nTokens = pedaços de palavra. prompt_tokens = o que você mandou;")
print("completion_tokens = o que o modelo gerou. No free tier é GRÁTIS,")
print("mas em produção é ISTO que aparece na fatura — por isso prompts")
print("enxutos são engenharia, não economia.")
