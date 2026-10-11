# 🚀 DevNet Journey — Marcelo Batista

> Jornada rumo à certificação **Cisco DevNet Associate (200-901)** com
> laboratório próprio (GNS3 + Docker) e registro semanal do progresso.
> Cada pasta = uma semana. Cada script = um troféu conquistado no lab.

## 🏆 Troféus

| Data | Troféu | Domínio | Tecnologia |
|---|---|---|---|
| 2026-10-09 | Primeiro RESTCONF: hostname via curl | APIs | RESTCONF, curl |
| 2026-10-11 | Topologia de lab montada do zero | Rede | GNS3, IOS XE, IOSvL2 |
| 2026-10-11 | Sandbox Meraki: org própria, 200×3 | Plataformas | REST, Bearer, requests |
| 2026-10-11 | NETCONF: hostname em XML via ncclient | Automação | NETCONF, YANG, SSH:830 |
| 2026-10-12 | trofeu.py: curl → Python requests | APIs | requests, JSON, Basic Auth |

## 🧪 O laboratório

Topologia 100% própria, custo zero:

`devnet-1 (Docker/Ubuntu + arsenal Python) ↔ vIOS-L2 (switch) ↔ CSR8000v (IOS XE 17.6, RESTCONF+NETCONF) ↔ Cloud`

Container tudo-em-um construído com Dockerfile próprio (ver `lab/`):
Python 3, requests, netmiko, ncclient, napalm, ansible, nmap, tcpdump, git.

## 📅 Progresso (12 semanas)

- [x] Semana 1-2 — Git + Python + requests (trofeu.py)
- [ ] Semana 3 — Git avançado + este portfólio
- [ ] Semana 4 — APIs REST a fundo (Flask, webhooks, auth)
- [ ] Semana 5 — NETCONF/YANG avançado
- [ ] Semana 6 — Docker + deploy
- [ ] Semana 7 — Ansible
- [ ] Semana 8 — Plataformas Cisco (sandboxes)
- [ ] Semanas 9-12 — Rede, segurança, simulados, prova

## 📚 Sobre mim

20+ anos docência em redes (CCAI/CCNA), mestrado em computação, pós em
Data Science e IA Aplicada à Saúde.

## 🗂️ Estrutura

- `semana-XX/` — códigos e labs de cada semana
- `lab/` — Dockerfile, entrypoint e scripts do laboratório
- `docs/` — blueprint, rota de estudos, instalação do lab
- `diario-de-estudos.md` — registro de cada sessão
