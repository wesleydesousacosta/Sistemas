#!/bin/bash

# Instalações de pré-requisitos (executadas apenas uma vez por container)
apt update && apt install -y wget curl systemd iproute2 less net-tools

# Instalação do etcd
ETCD_VERSION=3.5.6
wget -q https://github.com/etcd-io/etcd/releases/download/v${ETCD_VERSION}/etcd-v${ETCD_VERSION}-linux-amd64.tar.gz -O /tmp/etcd.tar.gz
tar xvf /tmp/etcd.tar.gz -C /tmp/
mv /tmp/etcd-v${ETCD_VERSION}-linux-amd64/etcd* /usr/local/bin/

# Criação do diretório de dados do etcd
mkdir -p /var/lib/etcd

# Define as variáveis de acordo com o nome do nó
if [ "$NODE_NAME" == "mx-nodel" ]; then
    NODE_IP="172.21.0.10"
elif [ "$NODE_NAME" == "mx-nodel2" ]; then
    NODE_IP="172.21.0.11"
elif [ "$NODE_NAME" == "mx-nodel3" ]; then
    NODE_IP="172.21.0.12"
else
    echo "NODE_NAME não definido ou inválido."
    exit 1
fi

# Inicia o etcd em foreground (necessário para Docker)
/usr/local/bin/etcd \
  --name ${NODE_NAME} \
  --data-dir /var/lib/etcd \
  --initial-advertise-peer-urls http://${NODE_IP}:2380 \
  --listen-peer-urls http://0.0.0.0:2380 \
  --listen-client-urls http://0.0.0.0:2379 \
  --advertise-client-urls http://${NODE_IP}:2379 \
  --initial-cluster "mx-nodel=http://172.21.0.10:2380,mx-nodel2=http://172.21.0.11:2380,mx-nodel3=http://172.21.0.12:2380" \
  --initial-cluster-token etcd-cluster-1 \
  --initial-cluster-state new