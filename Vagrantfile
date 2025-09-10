Vagrant.configure("2") do |config|
  BOX_NAME = "generic/ubuntu2004"

  config.vm.define "proxy" do |proxy|
    proxy.vm.box = BOX_NAME
    proxy.vm.hostname = "proxy"
    proxy.vm.network "private_network", type: "dhcp"
  end

  config.vm.define "web" do |web|
    web.vm.box = BOX_NAME
    web.vm.hostname = "web"
    web.vm.network "private_network", type: "dhcp"

    web.vm.synced_folder "./app", "/home/vagrant/app"

    web.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y python3 python3-pip

      if [ -f /home/vagrant/app/requirements.txt ]; then
        pip3 install -r /home/vagrant/app/requirements.txt
      fi
      cd app
      fuser -k 5000/tcp || true
      python3 main.py
    SHELL
  end

  config.vm.define "db" do |db|
    db.vm.box = BOX_NAME
    db.vm.hostname = "database"
    db.vm.network "private_network", type: "dhcp"
  end
end
