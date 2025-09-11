#!/bin/bash

# Configurar chave SSH
echo "Configurando chave SSH..."
mkdir -p /home/vagrant/.ssh
chmod 700 /home/vagrant/.ssh

# Gerar chave SSH se não existir
if [ ! -f /home/vagrant/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -f /home/vagrant/.ssh/id_rsa -N "" -q
fi

chmod 600 /home/vagrant/.ssh/id_rsa

# Configurar known_hosts para evitar prompts
ssh-keyscan -H 10.0.1.20 >> /home/vagrant/.ssh/known_hosts 2>/dev/null
ssh-keyscan -H 10.0.1.30 >> /home/vagrant/.ssh/known_hosts 2>/dev/null

# Clonar o repositório
cd /home/vagrant
if [ ! -d "Plantractor" ]; then
    git clone https://github.com/RafaMazoliniF/Plantractor.git
    cd Plantractor
    git switch -c development
    git pull origin development
    cd /home/vagrant
else
    echo "Pasta Plantractor já existe, pulando clone..."
fi

echo "Instalando Nginx..."
sudo DEBIAN_FRONTEND=noninteractive apt install nginx -y

echo "Configurando Nginx..."
sudo tee /etc/nginx/nginx.conf > /dev/null <<EOF
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 768;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://10.0.1.20:5000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF

echo "Iniciando Nginx..."
sudo systemctl start nginx
sudo systemctl enable nginx

echo "Nginx configurado e rodando!"

# Função para copiar chave pública para um host
copy_ssh_key() {
    local host=$1
    echo "Configurando acesso SSH para $host..."
    
    # Tentar copiar a chave (pode falhar se o host não estiver pronto)
    sshpass -p vagrant ssh-copy-id -o StrictHostKeyChecking=no -i /home/vagrant/.ssh/id_rsa.pub vagrant@$host 2>/dev/null || \
    echo "Não foi possível copiar chave para $host (host pode não estar acessível ainda)"
}

# Instalar sshpass para automação com senha
echo "Instalando sshpass..."
sudo DEBIAN_FRONTEND=noninteractive apt install sshpass -y

# Copiar chaves públicas para os servidores de destino
copy_ssh_key "10.0.1.20"
copy_ssh_key "10.0.1.30"

echo "Copiando pasta Plantractor para os servidores 10.0.1.20 e 10.0.1.30..."

# Função para tentar SCP com retry
copy_with_retry() {
    local host=$1
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "Tentativa $attempt de $max_attempts para copiar para $host..."
        
        if scp -r -o StrictHostKeyChecking=no -i /home/vagrant/.ssh/id_rsa /home/vagrant/Plantractor vagrant@$host:/home/vagrant/ 2>/dev/null; then
            echo "Sucesso ao copiar para $host!"
            return 0
        else
            echo "Falha na tentativa $attempt, aguardando 10 segundos..."
            sleep 10
            ((attempt++))
        fi
    done
    
    echo "Não foi possível copiar para $host após $max_attempts tentativas"
    return 1
}

# Copiar para os servidores
copy_with_retry "10.0.1.20"
copy_with_retry "10.0.1.30"

echo "Processo de cópia concluído!"