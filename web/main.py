# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Box base para todas as VMs
  config.vm.box = "generic/ubuntu2204"
  
  config.vm.provider :libvirt do |libvirt|
    libvirt.memory = 1024
    libvirt.cpus = 1
  end

  # Script de provisionamento comum para todas as VMs
  config.vm.provision "shell", inline: <<-SHELL
    # Atualizar sistema e instalar git
    apt-get update
    apt-get install -y git
    
    # Clonar o repositório
    cd /home/vagrant
    git clone https://github.com/RafaMazoliniF/Plantractor.git
    cd Plantractor
    git switch -c development
    git pull origin development
    
    # Alterar proprietário do diretório clonado
    chown -R vagrant:vagrant /home/vagrant/Plantractor
  SHELL

  # VM 1 - Mantém internet (proxy)
  config.vm.define "vm1" do |vm1|
    vm1.vm.hostname = "vm1"
    vm1.vm.network "private_network", 
                   ip: "10.0.1.10",
                   type: "dhcp",
                   libvirt__network_name: "vagrant-private-network",
                   libvirt__dhcp_enabled: false,
                   libvirt__forward_mode: "nat"
    
    vm1.vm.provider :libvirt do |v|
      v.memory = 1024
      v.cpus = 1
    end
    vm1.vm.provision "shell", inline: <<-SHELL
      # Instalar Nginx
      sudo apt install -y nginx
      
      # Parar o Nginx se estiver rodando
      sudo systemctl stop nginx
      
      # Remover configuração padrão que causa conflito
      sudo rm -f /etc/nginx/sites-enabled/default
      
      # Criar arquivo de configuração do proxy
      sudo tee /etc/nginx/conf.d/proxy.conf > /dev/null << 'EOL'
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://10.0.1.20:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL
      
      # Testar a configuração
      sudo nginx -t
      
      # Iniciar e habilitar o Nginx
      sudo systemctl start nginx
      sudo systemctl enable nginx
    SHELL
  end

  # VM 2 - Sem internet após instalação
  config.vm.define "vm2" do |vm2|
    vm2.vm.hostname = "vm2"
    vm2.vm.network "private_network", 
                   ip: "10.0.1.20",
                   type: "dhcp",
                   libvirt__network_name: "vagrant-private-network",
                   libvirt__dhcp_enabled: false,
                   libvirt__forward_mode: "nat"
    
    vm2.vm.provider :libvirt do |v|
      v.memory = 1024
      v.cpus = 1
    end

    vm2.vm.provision "shell", inline: <<-SHELL
      # Instalar dependências (com internet)
      apt-get install -y python3 python3-pip
      if [ -f /home/vagrant/Plantractor/web/requirements.txt ]; then
        pip3 install -r /home/vagrant/Plantractor/web/requirements.txt
      fi
    SHELL

    # Desabilitar internet após instalação
    vm2.vm.provision "shell", run: "always", inline: <<-SHELL
      # Remover rota padrão (default gateway) para bloquear internet
      sudo ip route del default
      
      # Opcional: bloquear acesso externo com iptables
      sudo iptables -P OUTPUT DROP
      sudo iptables -A OUTPUT -d 10.0.1.0/24 -j ACCEPT  # Permitir apenas rede local
      sudo iptables -A OUTPUT -o lo -j ACCEPT           # Permitir loopback
    SHELL
  end

  # VM 3 - Sem internet após instalação
  config.vm.define "vm3" do |vm3|
    vm3.vm.hostname = "vm3"
    vm3.vm.network "private_network", 
                   ip: "10.0.1.30",
                   type: "dhcp",
                   libvirt__network_name: "vagrant-private-network",
                   libvirt__dhcp_enabled: false,
                   libvirt__forward_mode: "nat"
    
    vm3.vm.provider :libvirt do |v|
      v.memory = 1024
      v.cpus = 1
    end

    vm3.vm.provision "shell", inline: <<-SHELL
      # Instalar dependências (com internet)
      apt-get install -y python3 python3-pip
      if [ -f /home/vagrant/Plantractor/database/requirements.txt ]; then
        pip3 install -r /home/vagrant/Plantractor/database/requirements.txt
      fi
      sudo ufw allow from 10.0.1.20 to any port 5001
    SHELL

    # Desabilitar internet após instalação
    vm3.vm.provision "shell", run: "always", inline: <<-SHELL
      # Remover rota padrão (default gateway) para bloquear internet
      sudo ip route del default
      
      # Opcional: bloquear acesso externo com iptables
      sudo iptables -P OUTPUT DROP
      sudo iptables -A OUTPUT -d 10.0.1.0/24 -j ACCEPT  # Permitir apenas rede local
      sudo iptables -A OUTPUT -o lo -j ACCEPT           # Permitir loopback
    SHELL
  end
end