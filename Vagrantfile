Vagrant.configure("2") do |config|

  config.vm.define "master" do |master|
    master.vm.box = "ubuntu/bionic64"
#     master.disksize.size = '250GB'
    master.vm.hostname = "master"
    master.vm.network "private_network", ip: "192.168.206.1", netmask: "255.255.128.0", virtualbox__intnet: "management", mac: "9cb65490d900"
    master.vm.network "forwarded_port", guest: 8888, host: 8888
    master.vm.network "forwarded_port", guest: 8086, host: 8086
    master.vm.network "forwarded_port", guest: 5000, host: 5000
      #playbook = 'master'
    #master.vm.provision "#{playbook}", type: "ansible" do |ansible|
    #  ansible.compatibility_mode = "2.0"
    #  ansible.playbook = "ansible/#{playbook}.yml"
    #end
  end

  config.vm.define "clientHost" do |client|
    client.vm.box = "ubuntu/bionic64"
    client.vm.hostname = "client"
    client.vm.network "private_network", ip: "192.168.202.1", netmask: "255.255.128.0", virtualbox__intnet: "management", mac: "3ca82a1e631c"
    client.vm.network "private_network", ip: "192.168.2.2", netmask: "255.255.128.0", virtualbox__intnet: "client_to_switch", mac: "f4ce46fd3de0"
#     client.vm.network "private_network", ip: "192.168.2.3", netmask: "255.255.128.0", virtualbox__intnet: "eve_to_switch", mac: "f4ce46fd3de4"
    client.vm.provider "virtualbox" do |vb|
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
      vb.customize ["modifyvm", :id, "--nicpromisc4", "allow-all"]
    end
    playbook = 'client'
    #client.vm.provision "#{playbook}", type: "ansible" do |ansible|
    #  ansible.compatibility_mode = "2.0"
    #  ansible.playbook = "ansible/#{playbook}.yml"
    #end
  end

  #  config.vm.define "eve" do |eve|
  #    eve.vm.box = "ubuntu/bionic64"
  #    eve.vm.hostname = "eve"
  #    eve.vm.network "private_network", ip: "192.168.206.30", virtualbox__intnet: "management"
  #    eve.vm.network "private_network", ip: "192.168.43.30", virtualbox__intnet: "eve2switch", mac: "f4:ce:46:fd:3d:e1"
  #    playbook = 'eve'
  #    eve.vm.provision "#{playbook}", type: "ansible" do |ansible|
  #      ansible.compatibility_mode = "2.0"
  #      ansible.playbook = "ansible/#{playbook}.yml"
  #    end
  #  end

  config.vm.define "sa1" do |sa1| #IPS
    sa1.vm.box = "ubuntu/bionic64"
    sa1.vm.hostname = "sa1"
    sa1.vm.network "private_network", ip: "192.168.203.1", netmask: "255.255.128.0", virtualbox__intnet: "management", mac: "9cb65490b9b0"
    sa1.vm.network "private_network", ip: "0.0.0.0", netmask: "255.255.128.0", virtualbox__intnet: "sa1_to_switch", mac: "441ea1170a18"
    sa1.vm.network "private_network", ip: "0.0.0.0", netmask: "255.255.128.0", virtualbox__intnet: "sa1_fr_switch", mac: "441ea1170a1c"
    sa1.vm.provider "virtualbox" do |vb|
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
      vb.customize ["modifyvm", :id, "--nicpromisc4", "allow-all"]
    end
  end

  config.vm.define "sa2" do |sa2| # FW
    sa2.vm.box = "ubuntu/bionic64"
    sa2.vm.hostname = "sa2"
    sa2.vm.network "private_network", ip: "192.168.204.1", netmask: "255.255.128.0", virtualbox__intnet: "management", mac: "9cb65490f990"
    sa2.vm.network "private_network", ip: "0.0.0.0", netmask: "255.255.128.0", virtualbox__intnet: "sa2_to_switch", mac: "f4ce46fdec38"
    sa2.vm.network "private_network", ip: "0.0.0.0", netmask: "255.255.128.0", virtualbox__intnet: "sa2_fr_switch", mac: "f4ce46fdec39"
    sa2.vm.provider "virtualbox" do |vb|
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
      vb.customize ["modifyvm", :id, "--nicpromisc4", "allow-all"]
    end
  end

  config.vm.define "sa3" do |sa3|
    sa3.vm.box = "ubuntu/bionic64"
    sa3.vm.hostname = "sa3"
    sa3.vm.network "private_network", ip: "192.168.205.1", netmask: "255.255.128.0", virtualbox__intnet: "management", mac: "9cb6549099e4"
    sa3.vm.network "private_network", ip: "192.168.5.2", netmask: "255.255.128.0", virtualbox__intnet: "sa3_to_switch", mac: "f4ce46fd3d58"
#     sa3.vm.network "private_network", ip: "192.168.5.3", netmask: "255.255.128.0", virtualbox__intnet: "sa3_fr_switch", mac: "f4ce46fd3d59"
    sa3.vm.provider "virtualbox" do |vb|
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
      vb.customize ["modifyvm", :id, "--nicpromisc4", "allow-all"]
      vb.cpus = 4
    end
  end

  config.vm.define "server" do |server|
    server.vm.box = "ubuntu/bionic64"
    server.vm.hostname = "server"
    server.vm.network "private_network", ip: "192.168.201.1", netmask: "255.255.128.0", virtualbox__intnet: "management", mac: "9457a56dd218"
    server.vm.network "private_network", ip: "192.168.1.2", netmask: "255.255.128.0", virtualbox__intnet: "server_to_switch", mac: "5cb901999dd4"
    server.vm.provider "virtualbox" do |vb|
      vb.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
    end
    #    playbook = 'server'
    #    server.vm.provision "#{playbook}", type: "ansible" do |ansible|
    #      ansible.compatibility_mode = "2.0"
    #      ansible.playbook = "ansible/#{playbook}.yml"
    #    end
  end

  config.vm.define "switch" do |switch| # MAC               nic     ofport
    nets = { 3 => "client_to_switch",   # 12:34:56:78:90:10 enp0s9  1
            4 => "eve_to_switch",       # 12:34:56:78:90:11 enp0s10 2
            5 => "sa1_to_switch",       # 12:34:56:78:90:12 enp0s16 3
            6 => "sa1_fr_switch",       # 12:34:56:78:90:13 enp0s17 4
            7 => "sa2_to_switch",       # 12:34:56:78:90:14 enp0s18 5
            8 => "sa2_fr_switch",       # 12:34:56:78:90:15 enp0s19 6
            9 => "sa3_to_switch",       # 12:34:56:78:90:16 enp2s0  7
            10 => "sa3_fr_switch",      # 12:34:56:78:90:17 enp2s1  8
            11 => "server_to_switch"    # 12:34:56:78:90:18 enp2s2  9
            }
    switch.vm.box = "ubuntu/bionic64"
    switch.vm.hostname = "switch"
    switch.vm.provider "virtualbox" do |vb|
      vb.customize ["modifyvm", :id, "--chipset", "ich9"]
      nets.each do |nic, net|
        vb.customize ["modifyvm", :id, "--nic#{nic}", "intnet"]
        vb.customize ["modifyvm", :id, "--intnet#{nic}", "#{net}"]
        vb.customize ["modifyvm", :id, "--cableconnected#{nic}", "on"]
        vb.customize ["modifyvm", :id, "--macaddress#{nic}", "12345678901" + (nic-3).to_s]
      vb.customize ["modifyvm", :id, "--nicpromisc#{nic}", "allow-all"]
      end
    end
    switch.vm.network "private_network", ip: "192.168.207.1", netmask: "255.255.128.0", virtualbox__intnet: "management", mac: "9cb654b2ad8e"
  end
end
