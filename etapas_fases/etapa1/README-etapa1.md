# ETAPA 1 — Python + APIs de Rede 🟡

> A etapa central da certificação: usar Python para conversar com
> equipamentos de rede via APIs (RESTCONF, NETCONF) — e ir além:
> estender a mesma estrutura até uma LLM.

## Fase 1.1 — curl → requests ✅

> *Concluída em 2026-10-12 · arquivos: `fase1.1/`*

A primeira conversa com a API do roteador — primeiro no shell (curl),
depois em Python (requests). O objetivo: provar que a API é a mesma,
só muda a ferramenta.

### O que esta fase ensinou

- **requests + auth Basic** (`auth=(user, pass)` — o base64 é automático)
- **Status codes**: 200/401/404 — a tabela que cai na prova
- **JSON**: `r.json()` → dict Python; `json.dumps(..., indent=2)` → leitura humana
- **`input()` + `.strip()`**: ferramenta pergunta, não hardcode (o DHCP
  mudou o IP da borda de .141 pra .142 — a lição veio da dor)
- **`verify=False`**: lab com certificado self-signed (nunca em produção!)
- **`timeout=10`**: chamada HTTP sem timeout é bug esperando acontecer
- **Header YANG**: `Accept: application/yang-data+json` — o MIME do RESTCONF

### Evoluções já incorporadas

- `teste_restconf.py`: ferramenta completa — hostname + state + IP real
  (via `Cisco-IOS-XE-interfaces-oper`) + **throughput ao vivo**
  (Δcontadores/Δt em 2 amostras — como todo monitor de tráfego faz)
- `curls-restconf.md`: cheatsheet com 7 seções — os curls que funcionaram
  E os que falharam (com o porquê), gabarito de erros, regras de ouro

### Lições pagas nesta fase

| Erro | Causa raiz | Cura |
|---|---|---|
| `KeyError: 'Cisco-IOS-XE-native:hostname'` | mudou o path, não mudou o parse | a chave raiz espelha o FINAL do path pedido |
| `sem IP` na Gi1 (state) | config mostra `ip address dhcp`; ietf não exporta ipv4 no state | `Cisco-IOS-XE-interfaces-oper` (ietf = interoperab., oper = riqueza) |
| `invalid-value: uri keypath not found` | bloco de augmentation não montado pelo IOS | pedir o modelo oper da Cisco |
| `sys.exit` sem `import sys` | NameError na hora do guard | imports no topo, sempre |

## Fase 1.2 — Ferramenta RESTCONF completa ✅

> *Concluída em 2026-10-12 · arquivo: `fase1.1/teste_restconf.py`*

O `show interface` inteiro servido por API: hostname, config × state,
IP real por interface, status operacional e taxa de tráfego ao vivo.

**Conceitos-chave:** datastores config × state · modelos ietf × Cisco-oper ·
list-all resume, get-one detalha · Δcontadores/Δt = throughput.

## Fase 1.3 — Ponte Rede → IA ⬅️ **ATUAL**

> *Em andamento · arquivo: `fase1.1/ponte_ia.py` (esqueleto com 5 TODOs)*

A tese: **API é API** — a mesma estrutura que fala com o roteador fala
com uma LLM. Mudam 3 coisas: URL, auth (Basic → Bearer) e verbo (GET → POST).

```
[1] COLETA (RESTCONF) → [2] PROMPT (messages) → [3] POST (Groq) → [4] LÊ (choices)
```

**Novos conceitos:** POST com corpo JSON · Bearer token · papéis
system/user · temperature · `os.environ` pra key.

## Fase 1.4 — NETCONF: 1º contato ✅

> *Concluída em 2026-10-11 · arquivo: `fase1.1/teste_ncclient.py`*

O hostname de novo — agora em **XML via SSH:830** (ncclient, filtro XPath).
A mesma ficha YANG, outro transporte. O "quadro de 4 linguagens" do lab
fechou: CLI · RESTCONF · NETCONF · Meraki.

