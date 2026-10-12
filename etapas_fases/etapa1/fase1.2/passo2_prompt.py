# ================================================================
# passo2_prompt.py — FASE 1.2, PASSO 2: o prompt isolado
# ================================================================
# Monta as "messages" que a API de chat espera e mostra na tela —
# SEM chamar a LLM. É o ensaio: ver exatamente o que será enviado.
#
# Rodar no devnet-1:  python3 passo2_prompt.py
#
# O QUE APRENDE AQUI:
#   - a gramática das APIs de chat: messages com papéis system/user
#   - system = comportamento · user = pedido + dados
#   - json.dumps(..., ensure_ascii=False): acentos preservados
#   - POR QUE separar: prompt malformado = resposta ruim. Ver antes
#     de enviar = debugar a pergunta, não a resposta.
# ================================================================
import json

# --- dados FICTÍCIOS (o teste isolado não precisa do roteador!) ----
# Truque de engenharia: pra testar SÓ o prompt, não dependa do lab.
# Depois de validar o formato, o ponte_ia.py usa os dados REAIS.
interfaces_fake = [
    {"nome": "GigabitEthernet1", "status": "up"},
    {"nome": "GigabitEthernet2", "status": "lower-layer-down"},
    {"nome": "GigabitEthernet3", "status": "lower-layer-down"},
]


def monta_prompt(lista_interfaces):
    """Dados + instrução → as messages que a API espera.

    A API de chat recebe SEMPRE uma lista de mensagens com papéis.
    Isso é PADRÃO DA INDÚSTRIA (OpenAI, Groq, Ollama local — todos iguais):
      [{"role": "system", "content": ...},   ← como o modelo deve se comportar
       {"role": "user",   "content": ...}]   ← o pedido, com os dados embutidos
    """
    # lista de dicts → texto JSON indentado (legível pro modelo E pra você)
    dados_txt = json.dumps(lista_interfaces, indent=2, ensure_ascii=False)

    messages = [
        {
            "role": "system",
            # o system define o COMPORTAMENTO: persona, idioma, formato.
            # sem isto, o modelo responde como "default" — genérico.
            "content": ("Você é um engenheiro de redes sênior especialista em "
                        "IOS XE. Responda em português, de forma direta e técnica.")
        },
        {
            "role": "user",
            # o user carrega o PEDIDO + os DADOS. A LLM não vê seu
            # roteador — ela só conhece o que está ESCRITO nesta mensagem.
            # (por isso dados estruturados = respostas melhores)
            "content": ("Analise o status destas interfaces de um roteador "
                        "IOS XE e diga o que está OK e o que merece atenção, "
                        "de forma direta:\n\n" + dados_txt)
        },
    ]
    return messages


# --- main: monta e mostra o que será enviado ------------------------
print("Ensaio do prompt (nada é enviado à LLM):\n")
messages = monta_prompt(interfaces_fake)

# mostra a estrutura completa — é ISTO que viaja no corpo do POST
print(json.dumps(messages, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
print("Repare: 2 mensagens — 'system' (comportamento) e 'user' (pedido).")
print("Este objeto JSON inteiro é o CORPO do POST do ponte_ia.py.")
print("Se a LLM responder bobagem, o bug geralmente está AQUI, não nela.")
