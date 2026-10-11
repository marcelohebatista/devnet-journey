#!/bin/bash
# ================================================================
# cria-devnet.sh — gera a pasta devnet/ com os 3 arquivos completos
# Uso:  bash cria-devnet.sh   (roda DENTRO de ~/devnet-lab/)
# ================================================================
set -e
cd devnet

# ---------------- 1/3: Dockerfile ----------------
cat << 'EOF' > Dockerfile
# ================================================================
# devnet — O CONTAINER TUDO-EM-UM dos estudos DevNet (200-901)
# Linguagem: Python 3 · Automação: netmiko/ansible/ncclient/napalm
# APIs: requests/flask · Rede: nmap/tcpdump/iperf3 · Git
# ================================================================
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    TZ=America/Sao_Paulo

# CAMADA 1 — Sistema: rede completa + build + editores + git
RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 \
    iputils-ping \
    net-tools \
    dnsutils \
    traceroute \
    mtr-tiny \
    isc-dhcp-client \
    tcpdump \
    nmap \
    iperf3 \
    curl \
    wget \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    openssh-client \
    vim \
    nano \
    jq \
    && rm -rf /var/lib/apt/lists/*

# CAMADA 2 — Stack Python do exame 200-901
RUN pip3 install --no-cache-dir --break-system-packages \
    requests \
    flask \
    netmiko \
    paramiko \
    ncclient \
    napalm \
    ansible \
    pyyaml \
    jinja2 \
    || pip3 install --no-cache-dir \
    requests flask netmiko paramiko ncclient napalm ansible pyyaml jinja2

# CAMADA 3 — Workspace e entrypoint
WORKDIR /lab

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
EOF

# ---------------- 2/3: entrypoint.sh ----------------
cat << 'EOF' > entrypoint.sh
#!/bin/bash
# ================================================================
# devnet — entrypoint: rede primeiro, shell depois
# ================================================================
echo "[entrypoint] aguardando eth0..."
for i in $(seq 1 15); do
    ip link show eth0 >/dev/null 2>&1 && break
    sleep 1
done
ip link set eth0 up 2>/dev/null || true

# DHCP com timeout — se falhar, IP estático de emergência (lab 10.10.10.0/24)
timeout 20 dhclient -v eth0 2>/dev/null || {
    echo "!! DHCP não respondeu — configurando IP estático de emergência"
    ip addr add 10.10.10.20/24 dev eth0 2>/dev/null || true
    ip route add default via 10.10.10.1 2>/dev/null || true
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
}

echo ""
echo "======================================================"
echo "  devnet PRONTO — o container tudo-em-um dos estudos"
echo "======================================================"
ip -4 addr show eth0 | grep inet || echo "(sem IPv4)"
ip route | head -3
echo "------------------------------------------------------"
echo " Arsenal: python3 · ansible · netmiko · ncclient · napalm"
echo "          requests · flask · git · nmap · tcpdump · iperf3"
echo "------------------------------------------------------"
echo " Teste rápido:"
echo "   ping -c2 10.10.10.1        (roteador de borda)"
echo "   python3 -c 'import netmiko, ansible, requests; print(\"stack OK\")'"
echo "   curl -k -u admin:cisco123 \\"
echo "     https://10.10.10.1/restconf/data/Cisco-IOS-XE-native:native/hostname"
echo "======================================================"

# Shell interativo — o console do GNS3 cai aqui
exec /bin/bash
EOF

# ---------------- 3/3: docker-compose.yml ----------------
cat << 'EOF' > docker-compose.yml
# ================================================================
# devnet — docker-compose
# Fora do GNS3:  docker compose up -d   → docker exec -it devnet bash
# Dentro do GNS3: build manual → template console TELNET → drag → Start
# ================================================================
services:
  devnet:
    build: .
    image: devnet:1.0
    container_name: devnet
    stdin_open: true        # -i: bash vivo
    tty: true               # -t: shell bonito no console
    restart: unless-stopped
    networks:
      - gns3_net
    # volumes:              # descomente p/ código versionado do host:
    #  - ~/devnet-lab/lab:/lab

networks:
  gns3_net:
    name: gns3_net
    driver: bridge
EOF

chmod +x entrypoint.sh

echo ""
echo ">>> CRIADO:"
ls -la
echo ""
echo ">>> Próximo:  docker build -t devnet:1.0 ."
