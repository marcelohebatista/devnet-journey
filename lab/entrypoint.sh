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

# ------------------------------------------------------------
# Servidor SSH: sobe depois do IP (senão ele nem escuta certo)
# ------------------------------------------------------------
mkdir -p /run/sshd
/usr/sbin/sshd
echo " SSH ativo:  ssh root@$(ip -4 addr show eth0 | grep -oP '(?<=inet )[\d.]+')   (senha: devnet)"

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
