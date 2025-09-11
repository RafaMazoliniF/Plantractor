#!/bin/bash

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