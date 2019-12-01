Vagrant.configure("2") do |config|

  config.vm.define "master" do |master|
    master.vm.box = "ubuntu/bionic64"
#     master.disksize.size = '250GB'
    master.vm.hostname = "master"
    master.vm.network "private_network", ip: "192.168.42.2", virtualbox__intnet: "management", mac: "9cb65490d900"
    master.vm.network "forwarded_port", guest: 8888, host: 8888
    master.vm.network "forwarded_port", guest: 8086, host: 8086
    #playbook = 'master'
    #master.vm.provision "#{playbook}", type: "ansible" do |ansible|
    #  ansible.compatibility_mode = "2.0"
    #  ansible.playbook = "ansible/#{playbook}.yml"
    #end
  end

  config.vm.define "clientHost" do |client|
    client.vm.box = "ubuntu/bionic64"
    client.vm.hostname = "client"
    client.vm.network "private_network", ip: "192.168.42.10", virtualbox__intnet: "management", mac: "3ca82a1e631c"
    client.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "client_to_switch", mac: "f4ce46fd3de0"
    client.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "eve_to_switch", mac: "f4ce46fd3de1"
    playbook = 'client'
    #client.vm.provision "#{playbook}", type: "ansible" do |ansible|
    #  ansible.compatibility_mode = "2.0"
    #  ansible.playbook = "ansible/#{playbook}.yml"
    #end
  end

#    config.vm.define "eve" do |eve|
#      eve.vm.box = "ubuntu/bionic64"
#      eve.vm.hostname = "eve"
#      eve.vm.network "private_network", ip: "192.168.42.30", virtualbox__intnet: "management"
#      eve.vm.network "private_network", ip: "192.168.43.30", virtualbox__intnet: "eve2switch", mac: "f4:ce:46:fd:3d:e1"
#      playbook = 'eve'
#      eve.vm.provision "#{playbook}", type: "ansible" do |ansible|
#        ansible.compatibility_mode = "2.0"
#        ansible.playbook = "ansible/#{playbook}.yml"
#      end
#    end

  config.vm.define "sa1" do |sa1|
    sa1.vm.box = "ubuntu/bionic64"
    sa1.vm.hostname = "sa1"
    sa1.vm.network "private_network", ip: "192.168.42.50", virtualbox__intnet: "management", mac: "9cb65490b9b0"

#     sa1.vm.provider "virtualbox" do |vb|
#       vb.customize ["modifyvm", :id, "--nic3", "intnet"]
#       vb.customize ["modifyvm", :id, "--intnet3", "sa1_to_switch"]
#       vb.customize ["modifyvm", :id, "--cableconnected3", "on"]
#       vb.customize ["modifyvm", :id, "--macaddress3", "987654321011"]
#     end
    sa1.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "sa1_to_switch", mac: "441ea1170a18"
#     sa1.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "sa1_fr_switch", mac: "441ea1170a1c"
  end

  config.vm.define "sa2" do |sa2|
    sa2.vm.box = "ubuntu/bionic64"
    sa2.vm.hostname = "sa2"
    sa2.vm.network "private_network", ip: "192.168.42.51", virtualbox__intnet: "management", mac: "9cb65490f990"
    sa2.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "sa2_to_switch", mac: "f4ce46fdec38"
#     sa2.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "sa2_fr_switch", mac: "f4ce46fdec39"
  end

  config.vm.define "sa3" do |sa3|
    sa3.vm.box = "ubuntu/bionic64"
    sa3.vm.hostname = "sa3"
    sa3.vm.network "private_network", ip: "192.168.42.52", virtualbox__intnet: "management", mac: "9cb6549099e4"
    sa3.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "sa3_to_switch", mac: "f4ce46fd3d58"
    sa3.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "sa3_fr_switch", mac: "f4ce46fd3d59"
  end

  config.vm.define "server" do |server|
    server.vm.box = "ubuntu/bionic64"
    server.vm.hostname = "server"
    server.vm.network "private_network", ip: "192.168.42.60", virtualbox__intnet: "management", mac: "9457a56dd218"
    server.vm.network "private_network", ip: "0.0.0.0", virtualbox__intnet: "server_to_switch", mac: "5cb901999dd4"
    #    playbook = 'server'
    #    server.vm.provision "#{playbook}", type: "ansible" do |ansible|
    #      ansible.compatibility_mode = "2.0"
    #      ansible.playbook = "ansible/#{playbook}.yml"
    #    end
  end

  config.vm.define "switch" do |switch|
    nets = {
#              3 => "client_to_switch",
#              4 => "eve_to_switch",
             5 => "sa1_to_switch",
#              6 => "sa1_fr_switch",
             7 => "sa2_to_switch",
#              8 => "sa2_fr_switch",
#              9 => "sa3_to_switch",
#              10 => "sa3_fr_switch",
#              11 => "server_to_switch"
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
      end
    end
    switch.vm.network "private_network", ip: "192.168.42.3", virtualbox__intnet: "management", mac: "9cb654b2ad8e"
  end
end
