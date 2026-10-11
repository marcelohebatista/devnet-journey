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
    openssh-server \
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

# ------------------------------------------------------------
# CAMADA 2.5 — Servidor SSH (acesso de fora ao container)
#   root:devnet = credenciais (troque a senha se quiser)
#   /run/sshd    = obrigatório ou o sshd não sobe (erro clássico)
# ------------------------------------------------------------
RUN echo 'root:devnet' | chpasswd \
    && mkdir -p /run/sshd \
    && sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22

# CAMADA 3 — Workspace e entrypoint
WORKDIR /lab

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
