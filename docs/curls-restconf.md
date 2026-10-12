# Curls RESTCONF — CSR8000v (IOS XE 17.6)

> Cheatsheet da jornada Semana 2 — testado no lab: `devnet-1 → CSR8000v 17.6 (192.168.0.142)`.
> Convenção: `curl -sk` = silencioso + ignora certificado self-signed (lab!).
> Header obrigatório: `-H "Accept: application/yang-data+json"` (o MIME do RESTCONF — cai na prova).
> Auth: Basic (`-u admin:cisco123`) — credencial de lab.

---

## 1. O básico — descobrindo a API

### 1.1 Enumerar TODOS os módulos YANG disponíveis
```bash
curl -sk -u admin:cisco123 -H "Accept: application/yang-data+json" \
  "https://192.168.0.142/restconf/data?depth=1"
```
→ 200: a lista de módulos que o roteador exporta. **O ponto de partida de tudo** — antes de adivinhar path, enumere.

### 1.2 Recursos RESTCONF (o "menu" da API)
```bash
curl -sk -u admin:cisco123 "https://192.168.0.142/restconf/"
```
→ 200: XML/JSON listando os datastores (`data`, `running`, `operational`).

---

## 2. Hostname (o troféu do dia 1 — 2026-10-09)
```bash
curl -sk -u admin:cisco123 -H "Accept: application/yang-data+json" \
  "https://192.168.0.142/restconf/data/Cisco-IOS-XE-native:native/hostname"
```
→ 200:
```json
{"Cisco-IOS-XE-native:hostname":"CSR8000v"}
```
**Lição:** no Cat8000v 17.6 o hostname NÃO mora no `ietf-system:system` — mora no modelo nativo da Cisco. Ler a API doc, não assumir o modelo ietf.

---

## 3. Interfaces — CONFIG (o "show run" da API)
```bash
curl -sk -u admin:cisco123 -H "Accept: application/yang-data+json" \
  "https://192.168.0.142/restconf/data/Cisco-IOS-XE-native:native/interface"
```
→ 200: árvore `Cisco-IOS-XE-native:interface → GigabitEthernet → [lista]`.
**Lições:**
- O `name` de cada item é só o SUFIXO (`"1"`, não `"GigabitEthernet1"`) — o prefixo vem da lista.
- A Gi1 mostra `ip address dhcp` (a config), **não** o IP aprendido. Config ≠ state.

---

## 4. Interfaces — STATE (o "show ip int brief" da API)
```bash
curl -sk -u admin:cisco123 -H "Accept: application/yang-data+json" \
  "https://192.168.0.142/restconf/data/ietf-interfaces:interfaces-state"
```
→ 200: cada interface com `oper-status` (`up` / `lower-layer-down`), `speed`, `phys-address` e `statistics` (`in-octets`, `out-octets`, `in-errors`...).
**Lição:** a chave raiz da resposta espelha o FINAL do path pedido (`ietf-interfaces:interfaces-state` — não `interfaces`). Parsear = ler o que veio, não o que se esperava.

### 4.1 State de UMA interface (path direto)
```bash
curl -sk -u admin:cisco123 -H "Accept: application/yang-data+json" \
  "https://192.168.0.142/restconf/data/ietf-interfaces:interfaces-state/interface=GigabitEthernet1"
```
→ 200: a ficha da Gi1 (mesma estrutura do GET largo, por interface).

---

## 5. O IP da interface — dois becos, uma saída

### 5.1 ❌ TENTATIVA: ipv4 dentro do state ietf
```bash
curl -sk -u admin:cisco123 -H "Accept: application/yang-data+json" \
  "https://192.168.0.142/restconf/data/ietf-interfaces:interfaces-state/interface=GigabitEthernet1/ietf-ip:ipv4"
```
→ erro:
```json
{"ietf-restconf:errors":{"error":[{"error-type":"application",
  "error-tag":"invalid-value","error-message":"uri keypath not found"}]}}
```
**Lição:** IOS XE 17.6 **não exporta** o bloco `ietf-ip:ipv4` no state (augmentation não montada). Testado 2026-10-12.

### 5.2 ✅ SOLUÇÃO: modelo operacional da Cisco
```bash
curl -sk -u admin:cisco123 -H "Accept: application/yang-data+json" \
  "https://192.168.0.142/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces/interface=GigabitEthernet1"
```
→ 200: ficha rica — o `show interface` COMPLETO em JSON:
```json
{
  "Cisco-IOS-XE-interfaces-oper:interface": {
    "name": "GigabitEthernet1",
    "oper-status": "if-oper-state-ready",
    "ipv4": "192.168.0.142",
    "ipv4-subnet-mask": "255.255.255.0",
    "statistics": {
      "in-octets": "1330055", "out-octets": "197807",
      "rx-pps": "2", "rx-kbps": "1", "tx-pps": "0", "tx-kbps": "0",
      "num-flaps": "0", "in-crc-errors": "0"
    },
    "ether-state": {"negotiated-duplex-mode": "full-duplex",
                    "negotiated-port-speed": "speed-1gb"}
  }
}
```
**Lição-tesouro:** quando o modelo **ietf padrão** não exporta um dado, a Cisco mantém modelos **`-oper`** próprios (`Cisco-IOS-XE-*-oper`) que cobrem a lacuna. ietf = interoperabilidade; oper = riqueza de dados.
**Bônus:** `rx-kbps`/`tx-kbps` = taxa ao vivo medida PELO roteador (alternativa nativa ao truque de 2 amostras de contadores).

---

## 6. Erros que já pagamos (gabarito de diagnóstico)

| Sintoma | Causa | Cura |
|---|---|---|
| `404` no path | `restconf` desligado no boot (sem `wr`!) | `conf t → restconf → end → wr` |
| `401 Unauthorized` | usuário inexistente / senha errada | `username admin privilege 15 secret cisco123` |
| `invalid-value: uri keypath not found` | path existe no ietf mas o IOS não exporta o bloco | tentar o modelo `Cisco-IOS-XE-*-oper` |
| `Could not open socket` (ncclient) | `netconf-yang` desligado | `conf t → netconf-yang → wr` |
| `Errno -3` no Python | DNS sem resolver (sem IP/nameserver) | conferir `ip a` e `resolv.conf` |
| `Errno 113` no Python | sem rota — script rodou do HOST, não do container | olhar o prompt: `marcelo@pop-os` ≠ `root@devnet-1` |
| `400 Cookie Too Large` (navegador) | cookies acumulados no sandbox | limpar cookies do site |

---

## 7. Regras de ouro desta semana

1. **Espie antes de parsear:** `print(json.dumps(dado, indent=2)[:800])` — a chave raiz espelha o final do path pedido.
2. **Config × State:** `Cisco-IOS-XE-native` = running-config (`show run`); `*-state` / `*-oper` = execução (`show ip int brief` / `show interface`).
3. **ietf não deu? Cisco-oper dá.**
4. **Mudou config na borda → `wr` imediato** — IOS XE no GNS3 reboota amnésico.
5. **GET largo vem magro, path direto detalha** — list-all resume, get-one aprofunda.

---
*Testado no lab devnet-journey · devnet-1 → CSR8000v 17.6 · atualizado 2026-10-12*
