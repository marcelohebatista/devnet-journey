# FASE 1.2 — Ponte Rede → IA 🏆

> **Conquistada em 2026-10-12** · `ponte_ia-completo.py`
>
> Um script Python que coleta o status das interfaces de um roteador Cisco
> via RESTCONF e envia a uma LLM (Groq) para diagnóstico — provando na
> prática que **API é API**: a estrutura que fala com o roteador fala
> com qualquer servidor. Mudam só 3 coisas: URL, auth e verbo.

---

## COMEÇO — A tese e o desafio

**A tese:** você já conversava com o roteador (RESTCONF, GET, Basic auth).
Toda API cloud fala a mesma língua — inclusive uma LLM. Se a tese estiver
certa, a MESMA estrutura de código conversa com os dois mundos.

**O desafio:** construir em 4 passos — coletar dados reais da rede,
montar o prompt, fazer o POST, ler a resposta — cada peça testada
**isolada** antes da ponte inteira.

**O que muda do roteador pra LLM (a tabela que resume a fase):**

| | RESTCONF (roteador) | Groq (LLM) |
|---|---|---|
| URL | `https://IP/restconf/data/...` | `https://api.groq.com/openai/v1/chat/completions` |
| Auth | Basic (`admin:cisco123`) | **Bearer** (`Authorization: Bearer gsk_...`) |
| Verbo | **GET** (o pedido vai na URL) | **POST** (o pedido vai no CORPO) |
| Segredo | credencial de lab (pode no código) | API key → `os.environ` (nunca no código!) |

---

## MEIO — Os 6 passos (o que cada um faz e por quê)

### `passo0_testa_key.py` — A chave está viva?
Valida as 2 pré-condições antes de qualquer coisa: a `GROQ_API_KEY` está
exportada no ambiente? E é **válida**? Faz um GET no endpoint `/models`
— o "menu" da API — que é leve (não gasta tokens) e autentica de verdade.
**Bônus que salvou a fase:** a lista de modelos retornada é a **fonte da
verdade** do catálogo da Groq (e catálogo de LLM muda — o modelo sugerido
na doc já não existia mais).

### `passo1_coleta.py` — Os dados da rede, isolados
A peça que você já dominava (fase 1.1): GET RESTCONF no
`ietf-interfaces:interfaces-state` → lista de dicts `{"nome", "status"}`.
O script mostra o mesmo dado em **2 roupas**: como Python guarda (dict) e
como o dado **viaja** (JSON) — a roupa que entra no prompt.

### `passo2_prompt.py` — O ensaio do prompt (sem gastar chamada)
Monta as `messages` no formato padrão de TODA API de chat
(`system` = comportamento · `user` = pedido + dados) e **mostra na tela**
antes de enviar. Usando dados fictícios — testar formatação não precisa
de lab nem de key. **Por quê:** se a LLM responder bobagem, o bug
geralmente está no prompt, não nela.

### `passo3_post.py` — O POST mínimo (o coração da fase)
O primeiro POST da jornada: Bearer no header + corpo JSON + `requests.post`.
Com o menor prompt possível ("diga Oi") — se isto funciona, a ponte
funciona; o resto é trocar o conteúdo pelos dados reais.
**O erro que pagamos aqui:** `404 model_not_found` — o modelo
`llama-3.3-70b-versatile` tinha sido descontinuado. A cura estava no
próprio passo 0: a lista do `/models` mostrou os 11 modelos reais
disponíveis. **Lição:** ler o corpo do erro (`r.text`) + consultar o
catálogo vivo > confiar em documentação. Corrigido para `openai/gpt-oss-120b`.

### `passo4_parse.py` — Ler a resposta (Python puro, sem API)
Navega o JSON aninhado da resposta usando uma resposta **fictícia** —
não gasta chamada. O caminho: `choices[0].message.content` — padrão de
toda API de chat (Groq, OpenAI, Ollama local). De brinde, o campo
`usage`: a contabilidade de tokens (grátis no free tier, fatura em produção).

### `ponte_ia-completo.py` — TUDO JUNTO (o troféu)
A ponte inteira: coleta real → prompt com dados reais → POST → diagnóstico.
É o mesmo código dos passos, agora encadeado em 4 chamadas no main.

---

## FIM — O troféu e o que ficou

```
[1/4] Coletando interfaces via RESTCONF...
      4 interfaces coletadas
[2/4] Montando o prompt...
[3/4] Enviando ao modelo (POST)...
[4/4] Diagnóstico da IA:

  | GigabitEthernet1 | up              | Operando normalmente... |
  | GigabitEthernet2 | lower-layer-down | Falha na camada física... |
  ...
  Conclusão: Gi1 OK. Gi2-4 requerem investigação física.
```

A LLM diagnosticou **corretamente** as interfaces reais do lab — com
causas prováveis e ações recomendadas. Um **agente de IA operacional**
em miniatura: o padrão "coleta do ambiente → LLM → análise" dos
copilotos de rede modernos, construído com `requests` puro.

### O que esta fase deixou de permanente (reutilizável pra sempre)

- `get_restconf(host, path)` — GET genérico RESTCONF (fase 1.1)
- `monta_prompt(dados)` — messages no padrão da indústria
- `pergunta_llm(messages)` — POST com Bearer (trocar URL = trocar provedor:
  Groq hoje, **Ollama local amanhã** — o código não muda)
- `extrai_texto(r)` — o parse que serve pra qualquer API de chat

### Lições pagas (o ouro do caderno)

| Erro | Cura | Lição |
|---|---|---|
| `404 model_not_found` no POST | ler `r.text` + lista do `GET /models` | catálogo de LLM é VIVO — a fonte da verdade é a própria API |
| key vazia (console novo) | `echo $GROQ_API_KEY` + re-export | `export` vale só pra sessão atual |
| (prevenido) dados `"???"` no prompt | testar cada peça isolada | passo isolado = erro na peça certa |

### Como cai na prova (domínio 2)

- **POST não é idempotente** (GET é) — a pegadinha clássica
- **Bearer vs Basic** — token no header Authorization (padrão OAuth2/cloud)
- **401 × 403** — não autenticado × sem permissão
- **Content-Type** (o que EU envio) × **Accept** (o que EU aceito receber)
- **Corpo do POST** viaja no corpo (`json=payload`), não na URL

---
*Fase 1.2 · etapa 1 · devnet-journey · 2026-10-12 · docs/teoria/apis-rest.md (caderno) · docs/roteiros/fase1.2.md (roteiro)*
