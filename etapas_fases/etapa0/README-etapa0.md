# ETAPA 0 — Fundações do Lab ✅

> Onde tudo acontece: o laboratório GNS3 + Docker e o fluxo de trabalho
> repo → GitHub → lab. Concluída em 2026-10-11.

## Fase 0.1 — Lab GNS3 + Docker montado do zero

### Topologia

```
devnet-1 (Docker/Ubuntu 22.04) ↔ vIOS-L2 (IOSvL2 15.2) ↔ CSR8000v (IOS XE 17.6) ↔ Cloud (NAT de casa)
```

- **devnet-1**: container próprio `devnet:1.0` (Ubuntu 22.04 + arsenal do exame:
  requests, netmiko, ncclient, napalm, ansible, nmap, tcpdump, git)
- **vIOS-L2**: switch L2 (8×e1000, console serial de fábrica)
- **CSR8000v**: roteador de borda — RESTCONF + NETCONF + WebUI habilitados
- **Cloud**: ponte com a rede de casa → DHCP + internet no lab

### Configuração da borda (o coração do lab)

```bash
hostname CSR8000v
ip domain-name lab.local
username admin privilege 15 secret cisco123
restconf
netconf-yang
ip http secure-server
crypto key generate rsa modulus 2048
interface GigabitEthernet1
 ip address dhcp
```

**⚠️ Lei do lab: mudou config na borda → `wr` imediato.** IOS XE no GNS3
reboota amnésico — sem `copy run start`, o lab volta de fábrica.

### Lições pagas nesta fase (o ouro do lab)

| Erro | Causa raiz | Cura |
|---|---|---|
| uBridge not available | grupos aplicados só no PRÓXIMO login | logout/reboot do sistema inteiro |
| Console "port 5005 < 5900" | console type × porta desalinhados | Configure do nó → telnet ou vnc |
| CSR não fala no telnet | build VGA → console vnc de fábrica | `platform console serial` + `wr` + reload |
| 404 no RESTCONF | feature desligada (reboot sem wr) | reconfigurar + `wr` |
| Host não alcança nós do Cloud | filtro anti-loop do ubridge (by design) | rodar scripts DENTRO do devnet-1 |
| `Errno -3` no Python | DNS sem resolver no container | `dhclient` / `resolv.conf` |

## Fase 0.2 — Git + GitHub + fluxo repo→push→pull→lab

### O fluxo (selado em 2026-10-11)

```
~/devnet-journey (FONTE DE VERDADE)
        │  edita → git add → commit → push
        ▼
     GitHub (backup + portfólio)
        │  git pull (no devnet-1, /lab é clone)
        ▼
  devnet-1 /lab (MALA DESCARTÁVEL — se morrer: git clone e tudo volta)
```

**Regras do fluxo:**
1. **Edita SEMPRE no repo do PC** — nunca na mala (descartável por design)
2. Caminho de emergência lab→repo: `docker cp <id>:/lab/... ~/devnet-journey/...`
3. Pull de repo público não pede token; push usa PAT (`credential.helper store`)
4. Segredo NUNCA sobe: API keys via `os.environ` (`.gitignore` protege, mas a regra é sua)

### Lições de Git pagas nesta fase

| Erro | Significado |
|---|---|
| `not a git repository ... up to mount point /mnt` | comando rodado fora do repo — discos montados são fronteira de descoberta |
| `src refspec main does not match any` | commit fantasma — faltava `user.name`/`user.email` |
| `Password authentication is not supported` | GitHub exige PAT desde 2021 (senha do site nunca) |
| `Your local changes would be overwritten by merge` | o Git protegendo edição não commitada — `checkout --` descarta, `stash` guarda |
| `nothing to commit, working tree clean` | tudo já salvo (boa notícia, não erro) |

## Troféus desta etapa

- 🏆 Topologia viva: 3 nós + Cloud, CPU ~20% / RAM ~37%
- 🏆 Primeiro RESTCONF via curl (hostname do CSR8000v em JSON)
- 🏆 Fluxo completo repo→GitHub→lab funcionando de ponta a ponta

---
*Artefatos relacionados: `lab/` (Dockerfile, entrypoint, compose, scripts) · `docs/comandos-instalacao-gns3.txt` · `docs/curls-restconf.md`*
