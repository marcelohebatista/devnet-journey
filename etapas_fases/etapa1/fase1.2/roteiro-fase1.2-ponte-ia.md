# Roteiro de Prática — Fase 1.2: Ponte Rede → IA

> **Objetivo:** um script Python que coleta o status das interfaces de um
> roteador Cisco via RESTCONF e envia a uma LLM (Groq) para diagnóstico —
> provando na prática que "API é API".
>
> **Pré-requisitos:** lab do repositório devnet-journey rodando (Etapa 0) ·
> borda CSR8000v com RESTCONF ligado · container devnet-1 com acesso à internet.
>
> **Duração estimada:** 60-90 min · **Custo:** R$ 0
>
> Quem tiver um roteador IOS XE 16.6+ (ou CML/sandbox) e Python 3 pode
> adaptar este roteiro — a estrutura é a mesma.

---

## PASSO 0 — Preparar a chave da LLM (10 min, uma vez só)

1. Acesse **console.groq.com** → criar conta (grátis, login com e-mail)
2. Menu lateral → **API Keys** → **Create API Key**
3. Dê um nome (ex.: `devnet-lab`) → copie a chave `gsk_...` **na hora**
   (ela não é mostrada de novo)
4. No terminal do devnet-1 (ou onde o script vai rodar):

```bash
export GROQ_API_KEY="gsk_cole_aqui"
```

⚠️ **Por que `export` e não colar no código?** A chave é um segredo real
(funciona na internet). Código vai pro GitHub; segredo fica no ambiente.
Conferir:

```bash
echo $GROQ_API_KEY        # deve mostrar a gsk_...
```

> **Nota:** o `export` vale só para a sessão atual do terminal. Abriu
> console novo? Exporte de novo.

---

## PASSO 1 — Baixar o esqueleto (5 min)

O esqueleto `ponte_ia.py` está no repositório. No ambiente de execução:

```bash
cd /lab && git pull        # se /lab é clone do repo
```

Abra o arquivo e localize os **5 TODOs** numerados — este roteiro preenche
cada um, **na ordem**.

---

## PASSO 2 — TODO 1: coletar as interfaces (15 min)

**O que faz:** repetir a coleta da fase 1.1 (GET RESTCONF), montando uma
lista de dicts `{"nome": ..., "status": ...}`.

No arquivo, em `coleta_interfaces`, substitua os `"???"`:

```python
lista.append({
    "nome":   i.get("name"),
    "status": i.get("oper-status"),
})
```

**Teste isolado** (roteiro de verdadeiro aprendizado — teste cada função
antes de seguir): comente as chamadas do main e rode só isto:

```python
HOST = input("IP: ").strip()
print(coleta_interfaces(HOST))
```

**Saída esperada:**

```python
[{'nome': 'GigabitEthernet1', 'status': 'up'},
 {'nome': 'GigabitEthernet2', 'status': 'lower-layer-down'},
 ...]
```

> **Se falhar:** confira o IP (`show ip int brief` na borda), se o RESTCONF
> está ligado (`show run | include restconf`) e se você está rodando de
> DENTRO do container (o host não alcança os nós do lab).

---

## PASSO 3 — TODO 2: montar o prompt (10 min)

**O que faz:** transformar os dados + uma instrução no formato que a API
de chat espera (lista `messages` com papéis `system` e `user`).

Em `monta_prompt`, preencha o `"content"` do user:

```python
"content": (
    "Analise o status destas interfaces de um roteador IOS XE e diga "
    "o que está OK e o que merece atenção, de forma direta:\n\n"
    f"{dados_txt}"
)
```

**Teste isolado:**

```python
print(json.dumps(monta_prompt(interfaces), indent=2, ensure_ascii=False))
```

**Saída esperada:** duas mensagens — a `system` (engenheiro sênior) e a
`user` (o pedido com os dados embutidos no final).

> **Conceito no ato:** os dados vão DENTRO do texto do prompt. A LLM não
> "vê" seu roteador — ela só conhece o que está escrito na mensagem.

---

## PASSO 4 — TODO 3: O POST (15 min — o coração da fase)

**O que faz:** o primeiro POST da jornada. O pedido viaja no **corpo**
da requisição (não na URL, como no GET).

Em `pergunta_llm`, substitua o `r = None`:

```python
try:
    r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
except requests.exceptions.ConnectionError:
    print("Sem internet/rota até a Groq — confira DNS/gateway")
    return None
```

> **Compare com o GET do RESTCONF:** mesmo `requests`, mesmo try/except —
> mudam o verbo (`post`), o auth (Bearer no header) e o corpo (`json=payload`).

---

## PASSO 5 — TODO 4: ler os erros (5 min)

**O que faz:** quando o status NÃO é 200, imprimir o diagnóstico.

Preencha dentro do `if r.status_code != 200:`

```python
print("Erro na chamada:", r.status_code)
print("Corpo da resposta:", r.text[:300])
```

> **Conceito no ato:** APIs de LLM explicam o erro no corpo (JSON com
> campo `error`). Ler `r.text` resolve 90% dos problemas.

**Tabela dos erros prováveis:**

| Status | Causa | Cura |
|---|---|---|
| 401 | key não exportada / inválida | `echo $GROQ_API_KEY`; re-exportar |
| 400 `model_not_found` | ID do modelo errado/descontinuado | conferir console.groq.com/docs/models |
| 429 | free tier: rate limit | esperar 1 min e rodar de novo |
| `Errno -3` | DNS no container | `dhclient eth0` / resolv.conf |

---

## PASSO 6 — TODO 5: extrair a resposta (5 min)

**O que faz:** navegar o JSON aninhado até o texto do modelo.

Em `extrai_texto`:

```python
return r.json()["choices"][0]["message"]["content"]
```

> **Mapa do caminho:** `choices` (alternativas) → `[0]` (a primeira) →
> `message` (a resposta) → `content` (o texto). Esse caminho é o padrão
> de TODA API de chat (Groq, OpenAI, Ollama local).

---

## PASSO 7 — O TROFÉU 🏆

Rode o script completo:

```bash
python3 ponte_ia.py
```

**Saída esperada:**

```
[1/4] Coletando interfaces via RESTCONF...
      4 interfaces coletadas
[2/4] Montando o prompt...
[3/4] Enviando ao modelo (POST)...
[4/4] Diagnóstico da IA:

  Sua topologia está saudável: a GigabitEthernet1 está operando (up)
  com conectividade... As interfaces Gi2-Gi4 estão lower-layer-down,
  o que é esperado quando não há cabo/conexão conectada...
```

**Quando isso aparecer, a fase 1.2 está conquistada:** rede → código → IA,
de ponta a ponta, com dados reais do SEU lab.

---

## Registro pós-prática (10 min)

1. Preencher os campos **✍️ minhas palavras** do caderno
   (`docs/teoria/apis-rest.md`)
2. `git add . && git commit -m "fase 1.2: ponte rede→IA — POST, Bearer, LLM" && git push`
3. Marcar a fase ✅ no README da etapa 1 + nova linha na tabela de troféus

---

## Reprodução por terceiros (checklist do ambiente)

- [ ] Roteador IOS XE 16.6+ com `restconf` + usuário privilegiado
- [ ] Máquina Linux com Python 3 + `requests` + `urllib3`
- [ ] Acesso à internet (api.groq.com) e ao roteador (rota + HTTPS:443)
- [ ] Conta Groq + API key exportada
- [ ] Clonar o repo: `git clone https://github.com/marcelohebatista/devnet-journey.git`

---
*Roteiro da fase 1.2 · devnet-journey · testado em 2026-10-12*
